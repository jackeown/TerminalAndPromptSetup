#!/usr/bin/env python3
"""Install only explicit files; preserve backups and a machine-readable undo manifest."""
import argparse
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'oh-my-zsh': ('ohmyzsh/ohmyzsh', '964ddf789b022b6958b27d02d7fa54f552de21e9'),
    'powerlevel10k': ('romkatv/powerlevel10k', 'd05a1b00f9a61f9578bf9dc19b8451942dde8734'),
    'custom/plugins/zsh-autosuggestions': ('zsh-users/zsh-autosuggestions', '85919cd1ffa7d2d5412f6d3fe437ebdbeeec4fc5'),
    'custom/plugins/zsh-syntax-highlighting': ('zsh-users/zsh-syntax-highlighting', 'e6683f20e5c38d3e5447f45845d04ddda75d0f23'),
}

def run(*args):
    subprocess.run(args, check=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--deps', action='store_true', help='install system prerequisites and pinned backdrop-shell first')
    p.add_argument('--desktop', action='store_true', help='configure KDE default terminal and Ctrl+Alt+T (log out afterward)')
    p.add_argument('--offline', action='store_true', help='use already installed pinned dependency checkouts')
    p.add_argument('--dry-run', action='store_true', help='print plan without downloads or writes')
    a = p.parse_args()
    home = Path.home()
    cfg = Path(os.environ.get('XDG_CONFIG_HOME', home / '.config'))
    data = Path(os.environ.get('XDG_DATA_HOME', home / '.local/share')) / 'terminal-setup'
    if a.dry_run:
        print(f'Install snapshot into {home}/.zshrc, {home}/.p10k.zsh, {cfg}/{{ghostty,zsh,limoni}}')
        print(f'Pinned source checkouts: {data}/deps; backups: {data}/backups/<timestamp>')
        print(f'System dependencies: {a.deps}; KDE integration: {a.desktop}')
        return
    if os.geteuid() == 0:
        sys.exit('Run as the target user, without sudo.')
    if sys.platform != 'linux':
        sys.exit('This installer targets Linux. See README for other systems.')
    for label, path in (('XDG_CONFIG_HOME', cfg), ('XDG_DATA_HOME', data)):
        if not path.is_absolute():
            sys.exit(f'{label} must be absolute.')
    if a.deps:
        run('bash', str(ROOT / 'scripts/dependencies.sh'))
    for tool in ('git', 'zsh', 'ghostty'):
        if not shutil.which(tool):
            sys.exit(f'Missing {tool}; use ./install.sh --deps or install it manually.')
    if not (home / '.local/bin/backdrop-shell').is_file():
        sys.exit('Missing ~/.local/bin/backdrop-shell. Use --deps or build the pinned module there.')
    if 'ZDOTDIR' in os.environ and Path(os.environ['ZDOTDIR']) != home:
        sys.exit('Custom ZDOTDIR detected. Unset it in your login environment before using this ~/.zshrc installer.')
    if a.desktop and 'KDE' not in os.environ.get('XDG_CURRENT_DESKTOP', '').upper():
        sys.exit('--desktop currently supports KDE only; see README for other desktops.')
    deps = data / 'deps'
    for name, (repo, commit) in PINS.items():
        dest = deps / name
        if not dest.exists() and not a.offline:
            dest.parent.mkdir(parents=True, exist_ok=True)
            run('git', 'clone', '--no-checkout', f'https://github.com/{repo}.git', str(dest))
            run('git', '-C', str(dest), 'checkout', '--detach', commit)
        result = subprocess.run(['git', '-C', str(dest), 'rev-parse', 'HEAD'], capture_output=True, text=True)
        dirty = subprocess.run(['git', '-C', str(dest), 'status', '--porcelain'], capture_output=True, text=True)
        if result.returncode or result.stdout.strip() != commit or dirty.returncode or dirty.stdout:
            sys.exit(f'{dest} is missing, modified, or at the wrong revision; move it aside and rerun online.')
    backup = data / 'backups' / datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup.mkdir(parents=True)
    manifest = []

    def write(dest, content):
        dest = Path(dest)
        if dest.is_symlink() or (dest.exists() and not dest.is_file()):
            raise RuntimeError(f'Refusing to replace symlink or non-file: {dest}; move it aside first.')
        if dest.exists() and dest.read_bytes() == content:
            return
        saved = None
        if dest.exists():
            saved = backup / str(len(manifest))
            shutil.copy2(dest, saved)
        manifest.append({'path': str(dest), 'backup': str(saved) if saved else None})
        (backup / 'manifest.json').write_text(json.dumps(manifest, indent=2))
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        print('Installed', dest)

    ghost = (ROOT / 'config/ghostty/config.in').read_text()
    ghost = ghost.replace('@BACKGROUND@', str(cfg / 'ghostty/background.png')).replace('@ZSH@', os.path.realpath(shutil.which('zsh')))
    write(cfg / 'ghostty/config', ghost.encode())
    write(home / '.zshrc', (ROOT / 'config/zshrc').read_bytes())
    write(home / '.p10k.zsh', (ROOT / 'config/p10k.zsh').read_bytes())
    for folder in ('ghostty', 'zsh', 'limoni'):
        for src in sorted((ROOT / 'config' / folder).rglob('*')):
            if src.is_file() and src.name != 'config.in':
                write(cfg / folder / src.relative_to(ROOT / 'config' / folder), src.read_bytes())
    if a.desktop:
        # Use a stable desktop ID regardless of Snap/native/Flatpak desktop IDs.
        exe = shutil.which('ghostty')
        escaped = exe.replace('\\', '\\\\').replace('"', '\\"').replace('`', '\\`').replace('$', '\\$').replace('%', '%%')
        desktop = f'[Desktop Entry]\nType=Application\nName=Ghostty (Terminal Setup)\nExec="{escaped}"\nIcon=com.mitchellh.ghostty\nTerminal=false\nCategories=System;TerminalEmulator;\n'
        apps = Path(os.environ.get('XDG_DATA_HOME', home / '.local/share')) / 'applications'
        write(apps / 'terminal-setup-ghostty.desktop', desktop.encode())
        # Preserve unrelated lines and groups, including KDE-specific escaping.
        def update_ini(path, changes, clear_conflicts=False):
            lines = path.read_text().splitlines() if path.exists() else []
            group = ''
            out = []
            remaining = dict(changes)
            for line in lines:
                if line.startswith('['):
                    group = line.strip()[1:-1]
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    if (group, key) in changes:
                        line = key + '=' + changes[group, key]
                        remaining.pop((group, key), None)
                    elif clear_conflicts and 'Ctrl+Alt+T' in value.split(',')[0].split('\\t'):
                        fields = value.split(',')
                        fields[0] = '\\t'.join(x for x in fields[0].split('\\t') if x != 'Ctrl+Alt+T') or 'none'
                        line = key + '=' + ','.join(fields)
                out.append(line)
            for (group, key), value in remaining.items():
                out.extend(['', '[' + group + ']', key + '=' + value])
            # Duplicate groups are accepted by KConfig, but consolidate them for clarity.
            groups = {}; current = ''; preamble = []
            for line in out:
                if line.startswith('['):
                    current = line
                    groups.setdefault(current, [])
                elif current:
                    groups[current].append(line)
                else:
                    preamble.append(line)
            text = '\n'.join(preamble + [x for g, body in groups.items() for x in [g, *body]]) + '\n'
            write(path, text.encode())
        update_ini(cfg / 'kdeglobals', {('General', 'TerminalApplication'): exe, ('General', 'TerminalService'): 'terminal-setup-ghostty.desktop'})
        update_ini(cfg / 'kglobalshortcutsrc', {('terminal-setup-ghostty.desktop', '_k_friendly_name'): 'Ghostty', ('terminal-setup-ghostty.desktop', '_launch'): 'Ctrl+Alt+T,none,Ghostty'}, True)
        print('KDE settings saved. Log out and back in so KGlobalAccel loads the shortcut.')
    print(f'Backup/undo manifest: {backup}/manifest.json')
    print('Open a NEW Ghostty window. Run bash scripts/doctor.sh and follow README acceptance checks.')


if __name__ == '__main__':
    main()
