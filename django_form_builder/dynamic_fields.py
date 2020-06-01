import ast
import base64
import inspect
import json
import logging
import os
import random
import re
import string
import sys

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import formset_factory
from django.forms import ModelChoiceField
from django.forms.fields import *
from django.template.defaultfilters import filesizeformat
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from . enc import encrypt
from . formsets import build_formset
from . widgets import *
from . settings import *
from . utils import (_split_choices,
                     _split_choices_in_list_canc,
                     _successivo_ad_oggi)

logger = logging.getLogger(__name__)

get_signatures = None
try:
    from filesig.filesig import get_signatures
except Exception as e:
    logger.error('Error: {}'.format(e))

if not get_signatures:
    try:
        from filesig import get_signatures
    except Exception as e:
        logger.error('Error: {}'.format(e))


MAX_UPLOAD_SIZE = getattr(settings, 'MAX_UPLOAD_SIZE', MAX_UPLOAD_SIZE)
ATTACH_NAME_MAX_LEN = getattr(settings, 'ATTACH_NAME_MAX_LEN',
                              ATTACH_NAME_MAX_LEN)
PERMITTED_UPLOAD_FILETYPE = getattr(settings,
                                    'PERMITTED_UPLOAD_FILETYPE',
                                    PERMITTED_UPLOAD_FILETYPE)
WRONG_TYPE = getattr(settings, 'WRONG_TYPE', WRONG_TYPE)
WRONG_SIZE = getattr(settings, 'WRONG_SIZE', WRONG_SIZE)
WRONG_LENGHT = getattr(settings, 'WRONG_LENGHT', WRONG_LENGHT)
IMG_FILETYPE = getattr(settings, 'IMG_FILETYPE', IMG_FILETYPE)
DATA_FILETYPE = getattr(settings, 'DATA_FILETYPE', DATA_FILETYPE)
PDF_FILETYPE = getattr(settings, 'PDF_FILETYPE', PDF_FILETYPE)
P7M_FILETYPE = getattr(settings, 'P7M_FILETYPE', P7M_FILETYPE)
CLASSIFICATION_LIST = getattr(settings, 'CLASSIFICATION_LIST', CLASSIFICATION_LIST)


def get_fields_types(class_name=sys.modules[__name__]):
    fields_types = []
    for m in inspect.getmembers(class_name, inspect.isclass):
        if hasattr(m[1],'field_type'):
            field_type = getattr(m[1], 'field_type')
            if field_type:
                fields_types.append(tuple((m[1].__name__, field_type)))
    fields_types.sort(key=lambda tup: tup[1])
    return fields_types


def format_field_name(field_name, lower=True):
    f = field_name.replace(' ','_')
    f = f.replace('(','')
    f = f.replace(')','')
    f = f.replace('/','_')
    if lower: return f.lower()
    return f.upper


class BaseCustomField(Field):
    """
    Base Class that defines methods for every field
    """

    # is a complex field
    is_complex = False
    # is a formset
    is_formset = False

    def define_value(self, custom_value=None, **kwargs):
        """
        Integrates fields building with more data coming from user
        configuration params
        """
        return

    def get_fields(self):
        """
        If field isn't complex, it returns a single element list with self.
        Else it returns a child fields list
        """
        return [self]

    def raise_error(self, name, cleaned_data, **kwargs):
        """
        Returns field validation errors list
        """
        return []


class CustomCharField(CharField, BaseCustomField):
    """
    CharField
    """
    field_type = _("Testo")


class CustomEmailField(EmailField, BaseCustomField):
    """
    EmailField
    """
    field_type = _("E-mail")


class CustomChoiceField(ChoiceField, BaseCustomField):
    """
    ChoiceField
    """
    def __init__(self, *args, **data_kwargs):
        super().__init__(*args, **data_kwargs)
        self.choices = []

    def define_value(self, choices, **kwargs):
        """
        Set field choices (if present)
        """
        if choices:
            # split string into separate choices
            self.choices += _split_choices(choices)

class CustomMultiChoiceField(MultipleChoiceField, BaseCustomField):
    """
    ChoiceField
    """
    def __init__(self, *args, **data_kwargs):
        super().__init__(*args, **data_kwargs)
        self.choices = []

    def define_value(self, choices, **kwargs):
        """
        Set field choices (if present)
        """
        if choices:
            # if there is a '#' parameter at the end of the string (...#3)
            # defines the maximum number of selectable options
            splitted_string = choices.split("#")
            self.max_permitted = int(splitted_string[1]) if len(splitted_string)>1 else 0
            # split string into separate choices
            self.choices += _split_choices(splitted_string[0])

    def clean(self, *args, **kwargs):
        args = args if isinstance(args[0], list) else ([args[0]],)
        return super().clean(*args, **kwargs)

    def raise_error(self, name, cleaned_data, **kwargs):
        errors = []
        if cleaned_data and self.max_permitted>0 and len(cleaned_data)>self.max_permitted:
            errors.append(_("Numero massimo di scelte consentito: {}").format(self.max_permitted))
        return errors


class CustomFileField(FileField, BaseCustomField):
    """
    FileField
    """
    field_type = _("Allegato (generico)")

    def __init__(self, *args, **data_kwargs):
        super().__init__(*args, **data_kwargs)

    def raise_error(self, name, cleaned_data, **kwargs):
        data = cleaned_data
        errors = []
        if data:
            msg = ''
            self_valid_extensions = getattr(self, 'valid_extensions', None)
            settings_upload_filetype = PERMITTED_UPLOAD_FILETYPE
            permitted_upload_filetype = self_valid_extensions or settings_upload_filetype
            max_upload_size = MAX_UPLOAD_SIZE
            attach_max_len = ATTACH_NAME_MAX_LEN

            if data.content_type not in permitted_upload_filetype:
                msg_tmpl = WRONG_TYPE
                msg = msg_tmpl.format(permitted_upload_filetype, data.content_type)
            elif data.size > int(max_upload_size):
                msg_tmpl = WRONG_SIZE
                msg = msg_tmpl.format(filesizeformat(max_upload_size),
                                      filesizeformat(data.size))
            elif len(data._name) > attach_max_len:
                msg_tmpl = WRONG_LENGTH
                msg = msg_tmpl.format(attach_max_len, len(data._name))
            if msg: errors.append(msg)
        return errors


class CustomImageField(CustomFileField):
    """
    FileField
    """
    field_type = _("Allegato Immagine")

    def __init__(self, *args, **data_kwargs):
        self.valid_extensions = IMG_FILETYPE
        super().__init__(*args, **data_kwargs)


class CustomDataField(CustomFileField):
    """
    FileField
    """
    field_type = _("Allegato file dati (JSON, CSV, Excel)")

    def __init__(self, *args, **data_kwargs):
        self.valid_extensions = DATA_FILETYPE
        super().__init__(*args, **data_kwargs)


class CustomPDFField(CustomFileField):
    """
    FileField
    """
    field_type = _("Allegato PDF")

    def __init__(self, *args, **data_kwargs):
        self.valid_extensions = PDF_FILETYPE
        super().__init__(*args, **data_kwargs)


class CustomSignedFileField(CustomFileField):
    validation_error = _('Errore di validazione della firma digitale')
    fileformat = ''
    field_type = None

    def get_signature_params(self, data):
        """
        """
        if not data: return
        res = get_signatures(data, type=self.fileformat, only_valids=True)
        return res

    def get_cleaned_signature_params(self, data):
        res = self.get_signature_params(data)
        details = {}
        if res:
            details['Signature Validation'] = res[-1].get('Signature Validation')
            details['Signing Time'] = res[-1].get('Signing Time')
            details['Signer full Distinguished Name'] = res[-1].get('Signer full Distinguished Name')
        return details

    def raise_error(self, name, cleaned_data, **kwargs):
        data = cleaned_data
        errors = []
        if data:
            simple_filefield_errors = super().raise_error(name, cleaned_data, **kwargs)
            errors.extend(simple_filefield_errors)
            res = self.get_signature_params(data)
            if not res or 'is valid' not in res[-1].get('Signature Validation').lower():
                errors.append(self.validation_error)
        return errors


class CustomSignedPdfField(CustomSignedFileField):
    """
    """
    field_type = _("Allegato PDF firmato")
    fileformat = 'pdf'
    valid_extensions = PDF_FILETYPE


class CustomSignedP7MField(CustomSignedFileField):
    """
    """
    field_type = _("Allegato P7M firmato")
    fileformat = 'p7m'
    valid_extensions = P7M_FILETYPE


class PositiveIntegerField(DecimalField, BaseCustomField):
    """
    Positive integer DecimalField
    """
    field_type = _("Numero intero positivo")
    default_validators = [MinValueValidator(0)]

    def __init__(self, *args, **data_kwargs):
        # Non si accettano formati con cifre decimali
        data_kwargs['decimal_places'] = 0
        super().__init__(*args, **data_kwargs)

    def raise_error(self, name, cleaned_data, **kwargs):
        if not cleaned_data: return []
        # Only numbers (expressions like 16e50 aren't permitted)
        if not re.match('^[0-9]+$', str(cleaned_data)):
            return [_("Solo numeri ammessi"),]


class PositiveFloatField(DecimalField, BaseCustomField):
    """
    Positive float DecimalField
    """
    field_type = _("Numero con virgola positivo")
    default_validators = [MinValueValidator(0)]

    def __init__(self, *args, **data_kwargs):
        # Max 3 cifre decimali
        data_kwargs['decimal_places'] = 3
        super().__init__(*args, **data_kwargs)

    def raise_error(self, name, cleaned_data, **kwargs):
        if not cleaned_data: return []
        # Only numbers (expressions like 16e50 aren't permitted)
        if not re.match('^[0-9]+\.?[0-9]?$', str(cleaned_data)):
            return [_("Solo numeri ammessi"),]


class TextAreaField(CharField, BaseCustomField):
    """
    TextArea
    """
    field_type = _("Testo lungo")
    widget = forms.Textarea


class CheckBoxField(BooleanField, BaseCustomField):
    """
    BooleanField Checkbox
    """
    field_type = _("Checkbox")
    widget = forms.CheckboxInput

class MultiCheckBoxField(CustomMultiChoiceField):
    """
    BooleanField Checkbox multi-value
    """
    field_type = _("Checkbox multi-valore")
    widget = forms.CheckboxSelectMultiple


class CustomSelectBoxField(CustomChoiceField):
    """
    SelectBox
    """
    field_type = _("Lista di opzioni (tendina)")

    def __init__(self, *args, **data_kwargs):
        super().__init__(*args, **data_kwargs)
        self.choices = [('', _('Scegli una opzione')),]


class CustomRadioBoxField(CustomChoiceField):
    """
    RadioBox
    """
    field_type = _("Lista di opzioni (checkbox)")
    widget = forms.RadioSelect

class BaseDateField(DateField, BaseCustomField):
    """
    DateField
    """
    field_type = _("Data")
    widget = forms.DateInput
    input_formats = settings.DATE_INPUT_FORMATS


class BaseDateTimeField(BaseCustomField):
    """
    DateTimeField
    """
    field_type = _("Data e Ora")
    is_complex = True

    def __init__(self, *args, **data_kwargs):
        # Date DateField
        self.data = BaseDateField(*args, **data_kwargs)
        self.data.label = _("{} (Data)").format(data_kwargs.get('label'))
        self.data.name = "{}_dyn".format(format_field_name(self.data.label))
        self.data.parent = self

        # Hour SelectBox
        self.hour = CustomSelectBoxField(*args, **data_kwargs)
        self.hour.label = _("{} (Ore)").format(data_kwargs.get('label'))
        self.hour.name = "{}_dyn".format(format_field_name(self.hour.label))
        self.hour.choices = [(i,i) for i in range(24)]
        self.hour.initial = 0
        self.hour.parent = self

        # Minutes SelectBox
        self.minute = CustomSelectBoxField(*args, **data_kwargs)
        self.minute.label = _("{} (Minuti)").format(data_kwargs.get('label'))
        self.minute.name = "{}_dyn".format(format_field_name(self.minute.label))
        self.minute.choices = [(i,i) for i in range(60)]
        self.minute.initial = 0
        self.minute.parent = self

    def get_fields(self):
        return [self.data, self.hour, self.minute]


class DateStartEndComplexField(BaseCustomField):
    """
    Field composed by StartDate (DateField) and EndDate (DateField)
    """
    field_type = _("Data inizio e Data fine")
    is_complex = True

    def __init__(self, *args, **data_kwargs):
        parent_label = data_kwargs.get('label')

        # Start date
        self.start = BaseDateField(*args, **data_kwargs)
        self.start.required = data_kwargs.get('required')
        self.start.label = _("{} (Data inizio)").format(parent_label)
        self.start.name = "{}_dyn".format(format_field_name(self.start.label))

        # Set child parent
        self.start.parent = self

        # End date
        self.end = BaseDateField(*args, **data_kwargs)
        self.end.required = data_kwargs.get('required')
        self.end.label = _("{} (Data fine)").format(parent_label)
        self.end.name = "{}_dyn".format(format_field_name(self.end.label))

        # Set child parent
        self.end.parent = self

    def get_fields(self):
        fields = [self.start, self.end]
        return fields

    def raise_error(self, name, cleaned_data, **kwargs):
        errors = []
        start_value = cleaned_data.get(self.start.name)
        end_value = cleaned_data.get(self.end.name)

        # If inizialization fails
        if not cleaned_data.get(name): return []

        # Check Start date
        if name == self.start.name:
            # if start_date > end_date
            if end_value and start_value > end_value:
                errors.append(_("La data di inizio non può "
                                "essere successiva a quella di fine"))

        return errors


class ProtocolloField(BaseCustomField):
    """
    Protocolo type, number and date (or another classification type)
    """
    field_type = "Protocollo (tipo/numero/data)"
    is_complex = True

    def __init__(self, *args, **data_kwargs):
        parent_label = data_kwargs.get('label')

        # Procotol type (selectbox)
        self.tipo = CustomSelectBoxField(*args, **data_kwargs)
        self.tipo.required = data_kwargs.get('required')
        self.tipo.label = _("{} (Tipo numerazione)").format(parent_label)
        self.tipo.name = "{}_dyn".format(format_field_name(self.tipo.label))
        self.tipo.help_text = _("Scegli se protocollo/decreto/delibera, "
                                "al/alla quale la numerazione è riferita")
        self.tipo.choices += [(i[0].lower().replace(' ', '_'), i[1]) \
                             for i in CLASSIFICATION_LIST]
        self.tipo.parent = self

        # Protocol number (char field)
        self.numero = CustomCharField(*args, **data_kwargs)
        self.numero.required = data_kwargs.get('required')
        self.numero.label = _("{} (Numero Protocollo/Delibera/Decreto)").format(parent_label)
        self.numero.name = "{}_dyn".format(format_field_name(self.numero.label))
        self.numero.help_text = _("Indica il numero del "
                                  "protocollo/decreto/delibera")
        self.numero.parent = self

        # Protocol date (DateField)
        self.data = BaseDateField(*args, **data_kwargs)
        self.data.required = data_kwargs.get('required')
        self.data.label = _("{} (Data Protocollo/Delibera/Decreto)").format(parent_label)
        self.data.name = "{}_dyn".format(format_field_name(self.data.label))
        self.data.help_text = _("Indica la data del protocollo/delibera/decreto")
        self.data.parent = self

    def get_fields(self):
        return [self.tipo, self.numero, self.data]

    def get_data_name(self):
        return self.data.name

    def raise_error(self, name, cleaned_data, **kwargs):
        value = cleaned_data.get(name)

        if not value: return [_("Valore mancante")]

        # Check protocol date
        if name == self.data.name:
            errors = []
            # If protocol_date > today
            if _successivo_ad_oggi(value):
                errors.append(_("La data di protocollo non può essere"
                                " successiva ad oggi"))
            return errors


class CustomHiddenField(CharField, BaseCustomField):
    """
    CharField Hidden
    """
    field_type = _("Campo nascosto")
    widget = forms.HiddenInput

    def define_value(self, custom_value, **kwargs):
        self.widget = forms.HiddenInput(attrs={'value': custom_value})


class CaptchaHiddenField(CustomHiddenField):
    """
    Captcha Hidden field
    """
    field_type = ""


class CaptchaField(BaseCustomField):
    """
    Captcha

    in settings:
        CAPTCHA_FONTS = ['/usr/share/fonts/truetype/ttf-bitstream-vera/Vera.ttf',
                         '/usr/share/fonts/truetype/liberation/LiberationMono-Italic.ttf']
        CAPTCHA_SECRET = b'6sa78d6as83$_RDF'
        CAPTCHA_SALT = b'ingoalla'

    """
    widget = CaptchaWidget

    def define_value(self, custom_value, **kwargs):
        self.widget = CaptchaWidget(attrs={'value': custom_value,
                                           'hidden_field': kwargs.get('hidden_field', ''),
                                           'lang': kwargs.get('lang', getattr(settings,
                                                                              'CAPTCHA_DEFAULT_LANG',
                                                                              CAPTCHA_DEFAULT_LANG))})


class CustomCaptchaComplexField(BaseCustomField):
    """
    Captcha complex field (image, sound, input and hidden text)
    """
    field_type = _("Captcha")
    is_complex = True

    def __init__(self, *args, **kwargs):
        # for auto-generated CaPTCHA
        # you can pass in kwargs captcha_name and captcha_hidden_name
        captcha_name = kwargs.pop("captcha_name") if kwargs.get("captcha_name") else ""
        captcha_hidden_name = kwargs.pop("captcha_hidden_name") if kwargs.get("captcha_hidden_name") else ""

        # CaPTCHA
        parent_label = kwargs.get('label')
        length = getattr(settings, 'CAPTCHA_LENGTH', 5)
        self.text = ''.join([random.choice(string.ascii_letters) for i in range(length)])

        self.hidden_data = '{"created": "' + timezone.now().isoformat() + '", "text": "' + self.text + '"}'

        # self.value = base64.b64encode(encrypt(self.text)).decode()
        self.value = base64.b64encode(encrypt(self.hidden_data)).decode()

        # self.captcha_hidden.define_value(custom_value=value)
        logger.debug(self.text, self.value)

        # Captcha hidden field
        self.captcha_hidden = CaptchaHiddenField()
        self.captcha_hidden.required = True
        self.captcha_hidden.name = captcha_hidden_name or "{}_hidden_dyn".format(format_field_name(parent_label))
        self.captcha_hidden.label = ''
        self.captcha_hidden.parent = self

        # Captcha field
        self.captcha = CaptchaField(*args, **kwargs)
        self.captcha.required = True
        # self.captcha.define_value(custom_value=text,
                                  # hidden_field="id_{}".format(self.captcha_hidden.name),
                                  # lang=self.lang)
        self.captcha.label = parent_label
        self.captcha.name = captcha_name or "{}_dyn".format(format_field_name(parent_label))
        # this should be taken from constructore dict
        # self.captcha.help_text = _("CaPTCHA: inserisci i caratteri/numeri raffigurati nell'immagine")
        self.captcha.parent = self

    def define_value(self, custom_value, **kwargs):
        # captcha_hidden field define_value
        self.captcha_hidden.define_value(custom_value=self.value)
        # get language from form custom_params
        # default 'en' (see captcha.py)
        lang = kwargs.get('lang', getattr(settings,
                                          'CAPTCHA_DEFAULT_LANG',
                                          CAPTCHA_DEFAULT_LANG))
        # captcha field define_value (with language code)
        self.captcha.define_value(custom_value=self.text,
                                  hidden_field="id_{}".format(self.captcha_hidden.name),
                                  lang=lang)

    def get_fields(self):
        return [self.captcha, self.captcha_hidden]

    def raise_error(self, name, cleaned_data, **kwargs):
        """
        """
        _err_msg = _('CaPTCHA not valid!')
        errors = []
        value = cleaned_data.get(self.captcha.name)
        check = cleaned_data.get(self.captcha_hidden.name)
        try:
            cvalue = decrypt(check).decode()
            json_check = json.loads(cvalue)
            created = json_check['created']
            clear_text = json_check['text']

            # if a value is submitted raise errors
            # else required field error is raised
            if value:
                created_date = parse_datetime(created)
                expiration_time = getattr(settings, 'CAPTCHA_EXPIRATION_TIME', CAPTCHA_EXPIRATION_TIME)
                is_expired = timezone.now() > (created_date + timezone.timedelta(milliseconds=int(expiration_time)))

                # if captcha is expired
                # check on name
                # (prevent to call 2 times this control, one for each child field)
                if name == self.captcha.name and is_expired:
                    errors.append(_('CaPTCHA expired'))

                # if captcha is incorrect
                # if value and cvalue.lower() != value.lower():
                elif clear_text.lower() != value.lower():
                    errors.append(_err_msg)
        except Exception as e:
            errors.append(e)

        return errors


class CustomComplexTableField(ChoiceField, BaseCustomField):
    """
    Formset field
    """
    # error message if is_required and no forms are present
    validation_error = _("Questo campo necessita di almeno una riga")
    field_type = _("Inserimenti multipli")
    is_complex = True
    is_formset = True
    choices = None

    def get_formset(self):
        if not self.choices: return
        return build_formset(choices=self.choices)

    def clean(self, *args, **kwargs):
        # If is_required and there aren't forms raise ValidationError.
        # Else, each form will clean itself, raising its own fields errors.
        if self.required and not self.widget.formset.forms:
            raise ValidationError(self.validation_error)
        return

    def define_value(self, custom_value, **kwargs):
        # Set field choices (if 'custom_value')
        if custom_value:
            elements = _split_choices_in_list_canc(custom_value)
            self.choices = elements
