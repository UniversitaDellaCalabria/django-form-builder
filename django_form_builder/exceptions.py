class ChoicesNotDefined(Exception):
    """
    if 'choices' not found in constructor kwargs
    """
    pass


class AudioCaptchaLangPackNotFound(Exception):
    """
    the language pack for Audio CaPTCHA cannot be found
    """
    def __init__(self,
                 msg='the language pack for Audio CaPTCHA cannot be found',
                 *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
