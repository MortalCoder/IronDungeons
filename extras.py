import PIL as pil
from PIL import Image

im = Image.open('sprites/bg_tileset.png')

for x in range(4):
    for y in range(4):
        im.crop((x*32, y*32, x*32+32, y*32+32)).save(f'bg_tile{x*4+y}.png')
