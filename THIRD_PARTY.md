# Asset and dependency provenance

- `config/p10k.zsh`: Jack’s generated Powerlevel10k configuration, retained verbatim. Powerlevel10k is MIT licensed; see `licenses/powerlevel10k-MIT.txt`.
- `config/zshrc`: adapted from Jack’s Oh My Zsh configuration plus his Ghostty/backdrop integration. Oh My Zsh is MIT licensed; see `licenses/oh-my-zsh-MIT.txt`.
- `config/zsh/banner-emoji/*`: cached PNG, ANSI and Kitty encodings rendered from the locally installed Noto Color Emoji font using the included Python generators. Noto font attribution/OFL text is retained in `licenses/noto-color-emoji.txt`; Apache text is included for the upstream project’s other material. No font binary is bundled.
- `config/ghostty/background.png`: copied from Jack’s active local Ghostty setup. Its original creator/source is not recorded in that configuration; establish provenance before granting a redistribution license for this asset.
- `config/zsh/ghostty-banner.zsh`: local banner implementation; quotation sources are listed in its comments.
- Ghostty, backdrop-shell, Oh My Zsh, Powerlevel10k and plugins are fetched/installed separately, with their upstream licenses. This repository does not bundle those executables or dependency source trees.

No general repository license has been chosen by the owner. These notices preserve known upstream attribution without asserting ownership of third-party material.
