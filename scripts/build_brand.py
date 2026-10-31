"""Rasterize original brand geometry, not third-party imagery."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def icon(size):
    im=Image.new('RGB',(size,size),'#101d32');d=ImageDraw.Draw(im);s=size/48
    for y,right in [(13,36),(24,26),(35,36)]:d.line([(13*s,y*s),(right*s,y*s)],fill='#55d6c2',width=round(4*s))
    d.line([(23*s,30*s),(29*s,21*s),(34*s,24*s),(39*s,12*s)],fill='#d9ae68',width=round(3*s));return im
def main():
    for size in [192,512]:icon(size).save(ROOT/f'public/icon-{size}.png')
    im=Image.new('RGB',(1200,630),'#101d32');im.paste(icon(160),(65,70));d=ImageDraw.Draw(im)
    font_path=Path('C:/Windows/Fonts/arial.ttf');font=lambda n:ImageFont.truetype(str(font_path),n) if font_path.exists() else ImageFont.load_default(size=n)
    d.text((65,275),'ENARM Watcher',font=font(76),fill='#f4f7fb');d.text((68,385),'Observatorio Nacional del ENARM',font=font(38),fill='#55d6c2');d.text((68,520),'Fuentes oficiales · Ciencia de datos · by Doctor Data MX',font=font(25),fill='#a0b0c5');im.save(ROOT/'public/og-enarm-watcher.png')
if __name__=='__main__':main()
