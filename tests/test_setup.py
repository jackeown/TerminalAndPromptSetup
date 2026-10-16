#!/usr/bin/env python3
"""Offline integration tests using temporary homes and local Git fixtures."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import pty
import select
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('setup_install', ROOT / 'scripts/install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class SetupTests(unittest.TestCase):
    def test_install_restore_and_desktop(self):
        with tempfile.TemporaryDirectory(prefix='terminal setup ') as tmp:
            home = Path(tmp)
            cfg = home / 'custom config'
            data = home / 'custom data'
            env = dict(os.environ, HOME=tmp, XDG_CONFIG_HOME=str(cfg), XDG_DATA_HOME=str(data), XDG_CURRENT_DESKTOP='KDE')
            env.pop('ZDOTDIR', None)
            deps = data / 'terminal-setup/deps'
            pins = {}
            for name in installer.PINS:
                dest = deps / name
                dest.mkdir(parents=True)
                subprocess.run(['git', 'init', '-q', str(dest)], check=True)
                subprocess.run(['git', '-C', str(dest), '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture', '--allow-empty'], check=True)
                sha = subprocess.check_output(['git', '-C', str(dest), 'rev-parse', 'HEAD'], text=True).strip()
                pins[name] = ('unused/offline', sha)
            (home / '.local/bin').mkdir(parents=True)
            (home / '.local/bin/backdrop-shell').write_text('# fixture, not executed\n')
            (home / '.zshrc').write_text('# old shell\n')
            cfg.mkdir()
            shortcuts = '[other.desktop]\n_launch=Ctrl+Alt+T\\tMeta+T,none,Other\n[unrelated]\nfoo=bar\n'
            (cfg / 'kglobalshortcutsrc').write_text(shortcuts)
            (cfg / 'kdeglobals').write_text('[General]\nColorScheme=KeepMe\n')
            originals = {str(p): p.read_bytes() for p in [home / '.zshrc', cfg / 'kglobalshortcutsrc', cfg / 'kdeglobals']}
            # Ghostty availability is checked but never launched by installation.
            real_which = shutil.which
            def which(tool):
                return '/usr/bin/ghostty' if tool == 'ghostty' else real_which(tool)
            with patch.dict(os.environ, env, clear=True), patch.object(installer, 'PINS', pins), patch.object(installer.shutil, 'which', side_effect=which), patch('sys.argv', ['install.py', '--offline', '--desktop']), contextlib.redirect_stdout(io.StringIO()):
                installer.main()
                manifests = sorted((data / 'terminal-setup/backups').glob('*/manifest.json'))
                self.assertEqual(len(manifests), 1)
                manifest = manifests[0]
                installer.main()
                self.assertEqual(len(list((data / 'terminal-setup/backups').glob('*/manifest.json'))), 1, 'Repeat must not rewrite identical files')
            self.assertIn('ColorScheme=KeepMe', (cfg / 'kdeglobals').read_text())
            self.assertIn('_launch=Meta+T,none,Other', (cfg / 'kglobalshortcutsrc').read_text())
            self.assertIn('Ctrl+Alt+T,none,Ghostty', (cfg / 'kglobalshortcutsrc').read_text())
            self.assertNotIn('/home/jack', (home / '.zshrc').read_text())
            self.assertIn(str(cfg / 'ghostty/background.png'), (cfg / 'ghostty/config').read_text())
            subprocess.run(['zsh', '-n', str(home / '.zshrc')], check=True)
            subprocess.run(['python3', str(ROOT / 'scripts/restore.py'), str(manifest), '--apply'], check=True, stdout=subprocess.DEVNULL)
            for path, content in originals.items():
                self.assertEqual(Path(path).read_bytes(), content)
            for item in json.loads(manifest.read_text()):
                if item['backup'] is None:
                    self.assertFalse(Path(item['path']).exists())

    def test_non_tty_wrapper_is_skipped(self):
        block = (ROOT / 'config/zshrc').read_text().split('# Ghostty: backdrop-shell')[0]
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / '.local/bin/backdrop-shell'
            binary.parent.mkdir(parents=True)
            binary.write_text('#!/bin/sh\nexit 91\n')
            binary.chmod(0o755)
            env = dict(os.environ, HOME=tmp)
            env.pop('LIMONI_BACKDROP_SHELL', None)
            result = subprocess.run(['zsh', '-fic', block + '\nprint wrapper-skipped'], env=env, capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0)
            self.assertIn('wrapper-skipped', result.stdout)

    def test_cwd_report_bypasses_inner_terminal(self):
        source = (ROOT / 'config/zshrc').read_text()
        function = source[source.index('__emit_osc7_cwd() {'):source.index('add-zsh-hook chpwd')]
        with tempfile.TemporaryDirectory(prefix='cwd % ü ') as tmp:
            outer_master, outer_slave = pty.openpty()
            inner_master, inner_slave = pty.openpty()
            try:
                env = dict(os.environ, GHOSTTY_RESOURCES_DIR='/fixture', LIMONI_BACKDROP_SHELL=os.ttyname(inner_slave), GHOSTTY_BACKDROP_OUTER_TTY=os.ttyname(outer_slave))
                subprocess.run(['zsh', '-f', '-c', function + '\n__emit_osc7_cwd'], cwd=tmp, env=env, stdout=inner_slave, check=True)
                self.assertTrue(select.select([outer_master], [], [], 2)[0], 'Report missing on outer PTY')
                report = os.read(outer_master, 65536)
                self.assertIn(tmp.encode(), report)
                self.assertTrue(report.startswith(b'\x1b]7;kitty-shell-cwd://'))
                self.assertTrue(report.endswith(b'\x07'))
                self.assertFalse(select.select([inner_master], [], [], 0)[0], 'Report incorrectly sent through backdrop')
                env.pop('LIMONI_BACKDROP_SHELL')
                output = subprocess.check_output(['zsh', '-f', '-c', function + '\n__emit_osc7_cwd'], cwd=tmp, env=env)
                self.assertIn(tmp.encode(), output)
                env.pop('GHOSTTY_RESOURCES_DIR')
                self.assertEqual(subprocess.check_output(['zsh', '-f', '-c', function + '\n__emit_osc7_cwd'], env=env), b'')
            finally:
                for fd in (outer_master, outer_slave, inner_master, inner_slave):
                    os.close(fd)


if __name__ == '__main__':
    unittest.main(verbosity=2)
