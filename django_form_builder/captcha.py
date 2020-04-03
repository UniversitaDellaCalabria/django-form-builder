import random
import string

from captcha.audio import AudioCaptcha
from captcha.image import ImageCaptcha

from django.conf import settings


def get_captcha(text=None):
    fonts = getattr(settings, 'CAPTCHA_FONTS', None)
    length = getattr(settings, 'CAPTCHA_LENGTH', 5)
    image = ImageCaptcha(fonts=fonts)

    text = text or ''.join([random.choice(string.ascii_letters+string.hexdigits) for i in range(length)])
    data = image.generate(text)
    return data

