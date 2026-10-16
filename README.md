# Ghostty + Zsh + Powerlevel10k + backdrop-shell

A portable snapshot of Jack’s terminal, captured on 2026-10-16: Ubuntu 24.04, KDE Plasma, Ghostty 1.3.1, Zsh, Oh My Zsh and Powerlevel10k. It includes the actual p10k configuration, static blue background, animated aurora, random greeting/quote banner and cached emoji images.

**Ctrl+Alt+T opens Ghostty. Ctrl+Shift+T opens a tab in the current tab’s working directory, including with backdrop-shell running.** The latter depends on the direct-to-outer-TTY workaround in `config/zshrc`; see debugging below.

## Install

On Ubuntu/Kubuntu/Debian with a graphical Linux session:

```bash
git clone https://github.com/jackeown/TerminalAndPromptSetup.git
cd TerminalAndPromptSetup
./install.sh --dry-run
./install.sh --deps --desktop
```

Run as your normal user, **not with sudo**. `--deps` uses sudo for apt packages and, if Ghostty is missing, a classic Snap installation. It downloads Go modules/toolchains, builds backdrop-shell for your architecture, and fetches pinned Git dependencies. Allow time for downloads. If Python 3 or Git is missing, first run `sudo apt-get install python3 git`.

`--desktop` is for **KDE only**. Omit it on other desktops:

```bash
./install.sh --deps
```

Log out and back in after configuring KDE, then open a **new Ghostty window**. Do not source `.zshrc` into an existing Bash/Fish/Zsh session: backdrop-shell replaces its parent shell and the integration needs a fresh terminal. The login shell is deliberately not changed: Ghostty explicitly launches the detected Zsh executable. Existing development tools can be added to `~/.zshrc.local`.

The installer replaces `.zshrc`, `.p10k.zsh`, and the specific bundled configuration/asset files. Changed existing files are backed up before replacement; unrelated configuration files are retained. Previous `.zshrc` content is **not automatically sourced**, because another prompt/backdrop initializer can break this setup. Move needed language-manager initialization, aliases and PATH additions into `.zshrc.local`. Jack’s private project aliases and Codex executable override are excluded. No history, credentials, or machine binaries are bundled.

## Other machines and desktop environments

- Linux x86_64 and ARM: backdrop-shell is compiled locally. Ghostty availability depends on your package source and architecture. The exact appearance is based on Ghostty **1.3.1 or newer**; older versions may reject the background and opacity options.
- Other Linux distributions: install Python 3, Git, Zsh, Ghostty, Go with automatic toolchain support (Go >=1.21), Hack, Noto Color Emoji and fontconfig with your package manager. Put the pinned backdrop binary in `~/.local/bin` (command below), then run `./install.sh`. The apt/Snap shortcut is not a universal package installer.
- GNOME: set a custom keyboard shortcut running the absolute path from `command -v ghostty`, bound to Ctrl+Alt+T, and remove any conflicting terminal shortcut in Settings → Keyboard. If your distribution provides a preferred-terminal selector, choose Ghostty there.
- Xfce: select Ghostty under Preferred Applications → Utilities → Terminal Emulator; bind Ctrl+Alt+T in Keyboard → Application Shortcuts. Other desktops/window managers need their own launcher/default-terminal configuration.
- KDE: `--desktop` installs a user desktop entry with a stable ID, updates only the terminal preferences and relevant shortcut entries, and removes Ctrl+Alt+T from conflicting KDE shortcut assignments. It backs up both affected KDE files. Log out/in to load the changes; check System Settings → Shortcuts if another service grabs the key.
- There is no single Linux-wide default terminal. KDE preferences and its launcher are automated. Programs that explicitly invoke `konsole`, `gnome-terminal` or `/usr/bin/x-terminal-emulator` may still open those applications. On Debian/Ubuntu, inspect `sudo update-alternatives --config x-terminal-emulator` separately if needed; this installer does not change a system-wide alternative for other users.
- macOS/Windows: not supported by these scripts. Ghostty/macOS shortcuts, config locations and backdrop PTYs need a separate port; WSL additionally needs a graphical environment. Do not assume the Linux desktop setup applies.
- `XDG_CONFIG_HOME` and `XDG_DATA_HOME` are honored; they must be absolute and exported consistently in the graphical session and shells. Custom `ZDOTDIR` is rejected to avoid silently installing an unused `.zshrc`.

Manual backdrop build (same module version as the original binary):

```bash
mkdir -p ~/.local/bin
GOTOOLCHAIN=auto GOBIN="$HOME/.local/bin" go install \
  github.com/thebanri/limoni/apps/backdrop-shell@v0.0.0-20261005163702-ad0518f23a8a
```

The upstream backdrop installer calls `enable` and modifies shell files. We build directly instead and supply our own initializer, preserving the Ghostty workaround. Avoid running `backdrop-shell enable` afterward: it may replace this custom block.

## What it looks like

| Component | Snapshot |
| --- | --- |
| Ghostty | Hack 12pt; Apple System Colors; padding 12×10; opacity 0.69; translucent painted cells; static background, cover/center; nonblinking block cursor |
| Backdrop | Aurora; opacity 0.6; animated; scene-native FPS; text-only mouse selection enabled |
| Prompt | Exact bundled `.p10k.zsh`; powerline mode; Oh My Zsh git, autosuggestions, syntax highlighting |
| Greeting | Random WONDER/EXPLORE/CREATE/HELLO, quote and emoji before p10k instant prompt |
| Shortcuts | Ctrl+Alt+T: desktop launch; Ctrl+Shift+T: same-directory tab; Ctrl+Shift+U: opacity toggle |

The original `.zshrc` listed `zsh-syntax-highlighting` but the plugin was missing on the source machine. This installer installs it so the configured plugin actually works. Hack is the original font, not Hack Nerd Font; this p10k config uses powerline mode. Font fallback and display scaling may vary. The unused `ghostty/auto` theme fragment is not installed: the active Ghostty config never includes it.

## Verify before calling it done

```bash
bash scripts/doctor.sh
```

Then, **inside a fresh Ghostty tab**, run:

```zsh
mkdir -p "$HOME/terminal tab test/percent% space/ü"
cd "$HOME/terminal tab test/percent% space/ü"
pwd
```

Press **Ctrl+Shift+T**, run `pwd` in the new tab, and confirm the directory is identical. Repeat from two tabs in different directories and with Ctrl+Alt+T after a desktop login. Confirm the aurora, greeting, prompt and opacity toggle visually. This manual check is required: syntax/config checks cannot prove the desktop’s shortcut routing or Ghostty’s live PTY behavior on another machine.

## Why the new-tab fix matters (for humans and coding agents)

Startup order:

1. Ghostty launches Zsh and injects shell integration.
2. The first `.zshrc` stores its terminal device in `GHOSTTY_BACKDROP_OUTER_TTY`, then **execs** backdrop-shell with `zsh` (or `zsh -l`). SSH sessions, non-TTY runs and `zsh -ic` skip this wrapper.
3. backdrop-shell creates an inner PTY and sets `LIMONI_BACKDROP_SHELL`; this prevents recursively wrapping the shell again.
4. The inner Zsh manually sources `$GHOSTTY_RESOURCES_DIR/shell-integration/zsh/ghostty-integration` because the original integration belonged to the replaced shell.
5. The greeting runs before p10k instant prompt, then Oh My Zsh and p10k initialize.
6. `chpwd` and `precmd` hooks emit OSC 7 using `kitty-shell-cwd://HOST/PWD` **directly to the saved outer TTY** when backdrop is active. backdrop-shell’s emulator does not forward the needed cwd reports in this captured version. Ghostty uses these reports for `tab-inherit-working-directory = true`.

Do not simplify away the outer TTY write, use `/dev/tty` inside backdrop, or rely only on `shell-integration = zsh`. The inner `/dev/tty` belongs to backdrop, not Ghostty. Raw paths in this Ghostty-supported OSC variant preserve spaces and percent signs.

In the affected interactive Zsh (these functions are not visible inside the doctor subprocess):

```zsh
print -r -- "cwd=$PWD" "inner=$LIMONI_BACKDROP_SHELL" "outer=$GHOSTTY_BACKDROP_OUTER_TTY"
tty
[[ -w $GHOSTTY_BACKDROP_OUTER_TTY ]] && print 'outer writable'
typeset -p chpwd_functions precmd_functions
functions __emit_osc7_cwd
__emit_osc7_cwd
```

Expected: the saved outer TTY differs from `tty` inside backdrop, is writable, and both hook arrays contain `__emit_osc7_cwd`. `GHOSTTY_RESOURCES_DIR` must point to a readable integration script. Check that the config includes `tab-inherit-working-directory = true`, `shell-integration = zsh`, and the explicit new-tab keybinding. If reporting works but the key does not, inspect desktop/global key interception and Ghostty overrides.

For a clean emergency shell, launch `ghostty -e /bin/zsh -f` from another terminal (adjust Zsh’s path if necessary). `-f` skips `.zshrc`. To disable only the animated layer temporarily, launch Ghostty with `LIMONI_BACKDROP=off ghostty`; fully exit existing Ghostty instances first so a reused process cannot retain the old environment. Rendering issues can be isolated with `still = true` or reduced opacity/FPS in `~/.config/limoni/backdrop.conf`.

No greeting? It intentionally runs only in interactive Ghostty with a TTY, not `zsh -ic`. Cached `.kitty`/`.rows` emoji graphics need Ghostty’s image support; the banner has a text emoji fallback. The `render*.py` files are optional regeneration tools requiring Pillow and the Ubuntu Noto Color Emoji font path; they are not run during installation.

## Backups, repeat installs, and rollback

The installer prints a timestamped `manifest.json` under `${XDG_DATA_HOME:-~/.local/share}/terminal-setup/backups/`. Identical files are skipped. Git dependencies live under the same data directory in `deps/`; they must match the recorded pins and have no local modifications. To refresh a damaged checkout, move that dependency directory aside and rerun. `--offline` skips cloning and requires all four clean pinned checkouts already present. It does not make `--deps` offline.

Preview and apply restoration for one install:

```bash
python3 scripts/restore.py /absolute/path/to/backups/TIMESTAMP/manifest.json
python3 scripts/restore.py /absolute/path/to/backups/TIMESTAMP/manifest.json --apply
```

Restoration replaces later edits to those files. Restore multiple installs newest first. Desktop restoration also needs logout/login. Dependency checkouts, apt/Snap packages, build caches and backdrop-shell are retained. The dependency helper saves any existing backdrop binary as `~/.local/bin/backdrop-shell.before-terminal-setup.TIMESTAMP`; restore it manually if needed. No login-shell change needs undoing.

## Maintenance and validation

`python3 tests/test_setup.py` checks isolated installation, backups, idempotency, rollback, and direct cwd reporting through PTYs. It does not install packages or alter your home. Source revisions are recorded in `scripts/install.py`; backdrop’s module pin is in `scripts/dependencies.sh`. Upgrading backdrop or Ghostty requires rerunning the live same-directory-tab acceptance test.

Upstream references: [Ghostty configuration](https://ghostty.org/docs/config/reference), [Ghostty installation](https://ghostty.org/docs/install/binary), [backdrop-shell source](https://github.com/thebanri/limoni/tree/ad0518f23a8acf5dfc2ce1bcb5b9c75af9adb8d2/apps/backdrop-shell), [Powerlevel10k](https://github.com/romkatv/powerlevel10k), [Oh My Zsh](https://github.com/ohmyzsh/ohmyzsh).

The bundled emoji images are rendered from Noto Color Emoji. See `THIRD_PARTY.md` for provenance and font licensing. No blanket license is asserted over third-party material.
