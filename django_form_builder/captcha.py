import os
import random
import string

from captcha.audio import AudioCaptcha
from captcha.image import ImageCaptcha

from django.conf import settings
from . exceptions import AudioCaptchaLangPackNotFound
from . settings import CAPTCHA_DEFAULT_LANG


def get_captcha(text=None, lang=getattr(settings,
                                        'CAPTCHA_DEFAULT_LANG',
                                        CAPTCHA_DEFAULT_LANG)):
    fonts = getattr(settings, 'CAPTCHA_FONTS', None)
    length = getattr(settings, 'CAPTCHA_LENGTH', 5)
    voicedir = getattr(settings, 'CAPTCHA_VOICEDIR',
                       os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                    'data', 'audio_captcha', lang))
    # if audio for that language is not available
    # fallback to settings default (english: en)
    if not os.path.exists(voicedir):
        voicedir = getattr(settings, 'CAPTCHA_VOICEDIR',
                           os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                        'data', 'audio_captcha',
                                        CAPTCHA_DEFAULT_LANG))
    image = ImageCaptcha(fonts=fonts)

    try:
        audio = AudioCaptcha(voicedir=voicedir)
    except IndexError as e:
        raise AudioCaptchaLangPackNotFound()

    text = text or ''.join([random.choice(string.ascii_letters+string.hexdigits)
                            for i in range(length)])

    data_image = image.generate(text)
    data_audio = audio.generate(text)
    return data_image, data_audio
