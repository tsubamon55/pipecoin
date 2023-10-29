import glob
import secrets

from PIL import Image
import qrcode
from blockchaincore import db, Ledger
import wallet

images_list = glob.glob('../code/*')

sample = Image.open('0rUcsGZ5wA1sKXw93-ud7Q.png')
text = Image.open('text1.png')


def get_concat_h():
    dst = Image.new('RGB', (sample.width * 4, sample.height * 6))
    for i in range(4):
        for j in range(3):
            img = Image.open(images_list.pop(1))
            dst.paste(text, (sample.width * i, sample.height * j*2))
            dst.paste(img, (sample.width * i, sample.height * (j*2 + 1)))
    c = secrets.token_urlsafe(16)
    dst.save(f'prepdf/{c}.png')


get_concat_h()
# print(text.height)
# print(text.width)
