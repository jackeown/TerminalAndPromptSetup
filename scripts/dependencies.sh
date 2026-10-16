#!/usr/bin/env bash
# Install prerequisites on Ubuntu/Debian; other systems use their package manager.
set -euo pipefail
if [[ $EUID == 0 ]]; then echo 'Run as your normal user (sudo is used only for packages).' >&2; exit 1; fi
if command -v apt-get >/dev/null; then
  sudo apt-get update
  sudo apt-get install -y git zsh golang-go fonts-hack fonts-noto-color-emoji fontconfig ca-certificates
else
  echo 'Install git, zsh, Go >= 1.21 (automatic toolchain downloads), Hack and Noto Color Emoji using your package manager.' >&2
fi
if ! command -v ghostty >/dev/null; then
  if command -v snap >/dev/null; then
    sudo snap install ghostty --classic
  else
    echo 'Install Ghostty >= 1.3.1: https://ghostty.org/docs/install/binary' >&2
    exit 1
  fi
fi
# Go downloads the module-required toolchain. Build for this machine, never copy Jack’s ELF.
command -v go >/dev/null
mkdir -p "$HOME/.local/bin"
if [[ -e $HOME/.local/bin/backdrop-shell ]]; then
  cp -p "$HOME/.local/bin/backdrop-shell" "$HOME/.local/bin/backdrop-shell.before-terminal-setup.$(date +%s)"
fi
GOTOOLCHAIN=auto GOBIN="$HOME/.local/bin" go install github.com/thebanri/limoni/apps/backdrop-shell@v0.0.0-20261005163702-ad0518f23a8a
