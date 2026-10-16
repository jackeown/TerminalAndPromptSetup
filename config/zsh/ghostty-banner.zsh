# Local startup banner; sourced before Powerlevel10k's instant prompt.
# Quote sources:
# Newton: https://www.newtonproject.ox.ac.uk/view/texts/normalized/OTHE00018
# Dijkstra: https://www.cs.utexas.edu/~EWD/transcriptions/EWD04xx/EWD498.html
# Turing: Computing Machinery and Intelligence (1950), closing sentence.
# Whitman: https://www.gutenberg.org/ebooks/1322
# Wordsworth: https://www.gutenberg.org/ebooks/8905
# Shakespeare: https://www.gutenberg.org/ebooks/1540
# Weierstrass: https://www.gutenberg.org/ebooks/44730
function ghostty-banner() {
  emulate -L zsh
  local -a quotes authors
  quotes=(
    'If I have seen further it is by standing on the shoulders of Giants.'
    'Simplicity is prerequisite for reliability.'
    'We can only see a short distance ahead, but we can see plenty there that needs to be done.'
    'I am large, I contain multitudes.'
    'Poetry is the spontaneous overflow of powerful feelings.'
    'We are such stuff as dreams are made on.'
    'A mathematician who is not also something of a poet will never be a complete mathematician.'
  )
  authors=(
    'Isaac Newton' 'Edsger W. Dijkstra' 'Alan Turing' 'Walt Whitman'
    'William Wordsworth' 'William Shakespeare' 'Karl Weierstrass'
  )
  local -i pick=$(( RANDOM % ${#quotes} + 1 ))
  local -i width=$(( ${COLUMNS:-80} - 6 ))
  (( width > 72 )) && width=72
  (( width < 12 )) && width=12
  local word line=''
  # Five rows instead of six: approximately 20% shorter, with compact glyphs.
  local -a titles colors rows
  titles=(WONDER EXPLORE CREATE HELLO)
  colors=(81 111 141 177 183)
  local title=${titles[$(( RANDOM % ${#titles} + 1 ))]}
  local -a emojis
  case $title in
    WONDER)  emojis=(🔭 🌌 🪐 ✨ 🔮) ;;
    EXPLORE) emojis=(🧭 🚀 🗺️ 🛰️ 🥾) ;;
    CREATE)  emojis=(🎨 🛠️ 💡 🧪 🎼) ;;
    HELLO)   emojis=(👋 🌞 😊 🌻 ☕) ;;
  esac
  local emoji=${emojis[$(( RANDOM % ${#emojis} + 1 ))]}
  local -A glyphs
  glyphs=(
    W '█  █|█  █|█  █|█ ██| ██ '
    O ' ██ |█  █|█  █|█  █| ██ '
    N '█  █|██ █|█ ██|█  █|█  █'
    D '███ |█  █|█  █|█  █|███ '
    E '████|█   |███ |█   |████'
    R '███ |█  █|███ |█ █ |█  █'
    X '█  █|█  █| ██ |█  █|█  █'
    P '███ |█  █|███ |█   |█   '
    L '█   |█   |█   |█   |████'
    C ' ███|█   |█   |█   | ███'
    A ' ██ |█  █|████|█  █|█  █'
    T '████| ██ | ██ | ██ | ██ '
    H '█  █|█  █|████|█  █|█  █'
  )
  local -i row column
  local character art
  print
  # Upload PNG directly to Ghostty; pass text placeholders through backdrop.
  # This keeps the image attached to the banner when the screen is redrawn.
  local emoji_base="${XDG_CONFIG_HOME:-$HOME/.config}/zsh/banner-emoji/$emoji"
  local -a image_rows
  local image_tty=/dev/tty
  [[ -n ${LIMONI_BACKDROP_SHELL-} && -w ${GHOSTTY_BACKDROP_OUTER_TTY-} ]] && image_tty=$GHOSTTY_BACKDROP_OUTER_TTY
  if (( ${COLUMNS:-80} >= ${#title} * 5 + 15 )) && [[ -t 1 && -n ${GHOSTTY_RESOURCES_DIR-} && -r $emoji_base.kitty && -r $emoji_base.rows ]]; then
    if print -rn -- "$(<"$emoji_base.kitty")" > "$image_tty"; then
      image_rows=("${(@f)$(<"$emoji_base.rows")}")
    fi
  fi
  if (( ${COLUMNS:-80} >= ${#title} * 5 + 15 )); then
    for row in {1..5}; do
      art=''
      for (( column=1; column<=${#title}; column++ )); do
        character=${title[column]}
        rows=("${(@s:|:)glyphs[$character]}")
        art+="${rows[row]} "
      done
      if (( ${#image_rows} == 5 )); then
        printf '  %s   \033[38;5;%sm%s\033[0m\n' "${image_rows[row]}" "${colors[row]}" "${art% }"
      else
        local icon='  '
        (( row == 3 )) && icon=$emoji
        printf '  %s   \033[38;5;%sm%s\033[0m\n' "$icon" "${colors[row]}" "${art% }"
      fi
    done
  else
    printf '  %s  \033[38;5;117m%s\033[0m\n' "$emoji" "$title"
  fi
  print
  # Print quote text literally, rather than treating it as prompt escapes.
  for word in ${=quotes[pick]}; do
    if (( ${#line} + ${#word} + 1 > width )) && [[ -n $line ]]; then
      printf '  \033[38;5;252m%s\033[0m\n' "$line"
      line=''
    fi
    line+="${line:+ }$word"
  done
  [[ -n $line ]] && printf '  \033[38;5;252m%s\033[0m\n' "$line"
  printf '  \033[38;5;141m— %s\033[0m\n\n' "${authors[pick]}"
}

# Once per shell, only in an interactive Ghostty terminal (not zsh -ic).
if [[ -o interactive && -t 1 && -n ${GHOSTTY_RESOURCES_DIR-} && -z ${ZSH_EXECUTION_STRING-} && -z ${_GHOSTTY_BANNER_SHOWN-} ]]; then
  typeset -g _GHOSTTY_BANNER_SHOWN=1
  ghostty-banner
fi
