# Working on this setup

Read README.md before editing startup or desktop integration. This repository is a snapshot/installer, not the active configuration: do not install into the current user's home merely to test it.

- Critical invariant: with backdrop-shell active, Ctrl+Shift+T must inherit the active tab's working directory. Keep the outer-TTY capture, manually reloaded Ghostty integration, and direct OSC 7 `chpwd`/`precmd` hooks together. `/dev/tty` inside backdrop is the wrong destination.
- Preserve ordering: backdrop exec → Ghostty integration → banner → p10k instant prompt → Oh My Zsh/p10k → cwd hooks.
- Keep user-specific paths, private aliases, history and credentials out of snapshots. Use XDG paths and local source builds rather than copied binaries.
- Run `python3 tests/test_setup.py`, `bash -n install.sh scripts/dependencies.sh scripts/doctor.sh`, and Zsh syntax checks after relevant changes. Installer tests use temporary homes.
- Real acceptance requires README's live Ghostty tab test, including spaces, `%`, Unicode and tabs in different directories. Do not claim desktop shortcut behavior from unit tests alone.
- Dependencies are pinned. Upgrades need deliberate pin edits plus the live acceptance test. Never run upstream `backdrop-shell enable` as part of installation: it can overwrite the custom startup block.
