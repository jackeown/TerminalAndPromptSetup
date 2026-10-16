"""Cache native-resolution font emoji and Kitty Unicode placeholder rows."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import base64
root = Path(__file__).parent
font = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
marks = [chr(n) for n in [0x305,0x30d,0x30e,0x310,0x312,0x33d,0x33e,0x33f,0x346,0x34a]]
for index, emoji in enumerate('🔭 🌌 🪐 ✨ 🔮 🧭 🚀 🗺️ 🛰️ 🥾 🎨 🛠️ 💡 🧪 🎼 👋 🌞 😊 🌻 ☕'.split(), 1):
    im = Image.new('RGBA', (160,160))
    ImageDraw.Draw(im).text((4,0), emoji, font=font, embedded_color=True)
    im = im.crop(im.getbbox())
    size = max(im.size)+8
    canvas = Image.new('RGBA',(size,size))
    canvas.alpha_composite(im,((size-im.width)//2,(size-im.height)//2))
    png = root / (emoji+'.png'); canvas.save(png)
    image_id = 0x5a0100+index
    payload = base64.b64encode(png.read_bytes()).decode()
    chunks = [payload[n:n+4096] for n in range(0,len(payload),4096)]
    transmission = ''
    for n, chunk in enumerate(chunks):
        header = f'a=T,f=100,t=d,U=1,i={image_id},c=10,r=5,q=2,' if n == 0 else ''
        transmission += '\033_G'+header+f'm={int(n<len(chunks)-1)};'+chunk+'\033\\'
    (root/(emoji+'.kitty')).write_text(transmission)
    rows=[]
    for row in range(5):
        rows.append(f'\033[38;2;90;1;{index}m'+''.join('\U0010eeee'+marks[row]+marks[col] for col in range(10))+'\033[0m')
    (root/(emoji+'.rows')).write_text('\n'.join(rows)+'\n')
