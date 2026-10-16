#!/usr/bin/env bash
# Read-only; no history, credentials, or complete environment dump.
set -u
cfg=${XDG_CONFIG_HOME:-$HOME/.config}
printf 'OS: '; uname -sm
printf 'Desktop: %s\nConfig root: %s\nSHELL: %s\nZDOTDIR: %s\n' "${XDG_CURRENT_DESKTOP:-unknown}" "$cfg" "${SHELL:-unset}" "${ZDOTDIR:-unset}"
for tool in ghostty zsh git go backdrop-shell; do
  command -v "$tool" || true
done
command -v ghostty >/dev/null && ghostty --version
command -v zsh >/dev/null && zsh --version
if command -v ghostty >/dev/null; then
  echo '--- Ghostty configuration validation ---'
  ghostty +validate-config || echo 'FAIL: Ghostty rejected configuration'
fi
zsh -n "$HOME/.zshrc" && echo 'Zsh syntax OK'
for file in "$HOME/.p10k.zsh" "$cfg/ghostty/background.png" "$cfg/limoni/backdrop.conf" "$cfg/zsh/ghostty-banner.zsh" "$HOME/.local/bin/backdrop-shell"; do
  [[ -r $file ]] && printf 'OK %s\n' "$file" || printf 'MISSING %s\n' "$file"
done
printf 'Ghostty resources: %s\nBackdrop PTY: %s\nOuter TTY: %s\n' "${GHOSTTY_RESOURCES_DIR:-unset}" "${LIMONI_BACKDROP_SHELL:-unset}" "${GHOSTTY_BACKDROP_OUTER_TTY:-unset}"
[[ -n ${GHOSTTY_RESOURCES_DIR:-} && -r $GHOSTTY_RESOURCES_DIR/shell-integration/zsh/ghostty-integration ]] && echo 'Ghostty Zsh integration readable'
[[ -n ${GHOSTTY_BACKDROP_OUTER_TTY:-} && -w $GHOSTTY_BACKDROP_OUTER_TTY ]] && echo 'Outer terminal writable'
command -v fc-match >/dev/null && fc-match Hack
if command -v go >/dev/null && [[ -f $HOME/.local/bin/backdrop-shell ]]; then
  go version -m "$HOME/.local/bin/backdrop-shell"
fi
echo 'Also run the live-tab commands in README from the affected interactive shell.'
