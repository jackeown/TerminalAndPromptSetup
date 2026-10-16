from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
for emoji in '🔭 🌌 🪐 ✨ 🔮 🧭 🚀 🗺️ 🛰️ 🥾 🎨 🛠️ 💡 🧪 🎼 👋 🌞 😊 🌻 ☕'.split():
    im = Image.new('RGBA', (160, 160))
    ImageDraw.Draw(im).text((4, 0), emoji, font=font, embedded_color=True)
    im = im.crop(im.getbbox())
    im.thumbnail((10, 10), Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA', (10, 10))
    canvas.alpha_composite(im, ((10-im.width)//2, (10-im.height)//2))
    result = ''
    for y in range(0, 10, 2):
        result += '  '
        for x in range(10):
            top, bottom = canvas.getpixel((x,y)), canvas.getpixel((x,y+1))
            a, b = top[3] >= 80, bottom[3] >= 80
            fg=lambda p: '\033[38;2;%d;%d;%dm' % p[:3]
            bg=lambda p: '\033[48;2;%d;%d;%dm' % p[:3]
            if a and b: result += fg(top)+bg(bottom)+'▀'
            elif a: result += '\033[49m'+fg(top)+'▀'
            elif b: result += '\033[49m'+fg(bottom)+'▄'
            else: result += '\033[0m '
        result += '\033[0m\n'
    (Path(__file__).parent / (emoji+'.ansi')).write_text(result)
