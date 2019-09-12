import ast
import inspect
import re
import os
import sys

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import formset_factory
from django.forms import ModelChoiceField
from django.forms.fields import *
from django.template.defaultfilters import filesizeformat
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from filesig.filesig import get_signatures

from . settings import *
from . utils import (_split_choices,
                     _split_choices_in_list_canc,
                     _successivo_ad_oggi)

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
    if lower: return f.lower()
    return f.upper

def get_empty_form(form_class=forms.Form):
    class Dynamic(form_class):
        pass
    return Dynamic

def build_formset(choices, extra=0, required=False, prefix='form', data=None):
    """ Get formset
    """
    _regexp = '(?P<colname>[a-zA-Z0-9_]*)\((?P<coldict>[\{\}\.0-9a-zA-Z\'\"\:\;\_\,\s\-]*)\)'
    min_num = 0
    if required: min_num = 1
    eform = get_empty_form()
    for choice in choices:
        colname = choice # needed for simple CharField withoud attrs
        contenuto = re.search(_regexp, choice)
        field_dict = None
        if contenuto:
            coldict = contenuto.groupdict().get('coldict')
            colname = contenuto.groupdict()['colname']
            if coldict:
                field_dict = ast.literal_eval(coldict)
                field_type_name = field_dict['type']
                del field_dict['type']

                custom_widget = settings.CUSTOM_WIDGETS.get(field_type_name)
                if custom_widget:
                    widget = import_string(custom_widget)()

                custom_field = getattr(sys.modules[__name__], field_type_name)(**field_dict) \
                               if hasattr(sys.modules[__name__], field_type_name) else CustomCharField()
                custom_widget = settings.CUSTOM_WIDGETS.get(field_type_name)
                if custom_widget:
                    custom_field.widget = import_string(custom_widget)()
                if field_dict.get('choices'):
                    custom_field.choices += _split_choices(field_dict.get('choices'))
        else:
            custom_field = CustomCharField()
        eform.base_fields[colname] = custom_field
        eform.declared_fields[colname] = custom_field

    # Django formset
    fac =  formset_factory(eform, extra=extra, min_num=min_num)
    if data: return fac(prefix=prefix, data=data)
    return fac(prefix=prefix)


class BaseCustomField(Field):
    """
    Classe Base che definisce i metodi per ogni CustomField
    """
    is_complex = False
    is_formset = False

    def __init__(self, *args, **data_kwargs):
        super().__init__(*args, **data_kwargs)

    def define_value(self, custom_value=None, **kwargs):
        """
        Integra la costruzione del field con informazioni aggiuntive
        provenienti dai parametri di configurazione definiti dall'utente
        """
        return

    def get_fields(self):
        """
        Se è un field semplice, torna se stesso.
        Se è un field composto, torna una lista di fields.
        """
        return [self]

    def raise_error(self, name, cleaned_data, **kwargs):
        """
        Torna la lista degli errori generati dalla validazione del field
        """
        return []


class CustomCharField(CharField, BaseCustomField):
    """
    CharField
    """
    field_type = _("Testo")

    def __init__(self, *args, **data_kwargs):
        super().__init__(*args, **data_kwargs)


class CustomChoiceField(ChoiceField, BaseCustomField):
    """
    ChoiceField
    """
    def __init__(self, *args, **data_kwargs):
        super().__init__(*args, **data_kwargs)
        self.choices = []

    def define_value(self, choices, **kwargs):
        """
        Se presenti, sostituisce alle opzioni di default
        quelle di 'custom_value'
        """
        # Imposta le 'choices' definite in backend come opzioni
        if choices:
            self.choices += _split_choices(choices)


class CustomFileField(FileField, BaseCustomField):
    """
    FileField
    """
    field_type = _("Allegato PDF")

    def __init__(self, *args, **data_kwargs):
        super().__init__(*args, **data_kwargs)

    def raise_error(self, name, cleaned_data, **kwargs):
        data = cleaned_data
        errors = []
        if data:
            msg = ''
            if data.content_type not in PERMITTED_UPLOAD_FILETYPE:
                msg_tmpl = WRONG_TYPE
                msg = msg_tmpl.format(data.content_type)
            elif data.size > int(MAX_UPLOAD_SIZE):
                msg_tmpl = WRONG_SIZE
                msg = msg_tmpl.format(filesizeformat(MAX_UPLOAD_SIZE),
                                      filesizeformat(data.size))
            elif len(data._name) > ATTACH_NAME_MAX_LEN:
                msg_tmpl = WRONG_LENGTH
                msg = msg_tmpl.format(ATTACH_NAME_MAX_LEN, len(data._name))
            if msg: errors.append(msg)
        return errors


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


class CustomSignedP7MField(CustomSignedFileField):
    """
    """
    field_type = _("Allegato P7M firmato")
    fileformat = 'p7m'


class PositiveIntegerField(DecimalField, BaseCustomField):
    """
    Int DecimalField positivo
    """
    field_type = _("Numero intero positivo")
    default_validators = [MinValueValidator(0)]

    def __init__(self, *args, **data_kwargs):
        # Non si accettano formati con cifre decimali
        data_kwargs['decimal_places'] = 0
        super().__init__(*args, **data_kwargs)


class PositiveFloatField(DecimalField, BaseCustomField):
    """
    Float DecimalField positivo
    """
    field_type = _("Numero con virgola positivo")
    default_validators = [MinValueValidator(0)]

    def __init__(self, *args, **data_kwargs):
        # Max 3 cifre decimali
        data_kwargs['decimal_places'] = 3
        super().__init__(*args, **data_kwargs)


class TextAreaField(CharField, BaseCustomField):
    """
    TextArea
    """
    field_type = _("Testo lungo")
    widget = forms.Textarea()

    def __init__(self, *args, **data_kwargs):
        super().__init__(*args, **data_kwargs)


class CheckBoxField(BooleanField, BaseCustomField):
    """
    BooleanField Checkbox
    """
    field_type = _("Checkbox")
    widget = forms.CheckboxInput()

    def __init__(self, *args, **data_kwargs):
        super().__init__(*args, **data_kwargs)


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
    CheckBox multiplo
    """
    field_type = _("Lista di opzioni (checkbox)")
    widget = forms.RadioSelect()

class BaseDateField(DateField, BaseCustomField):
    """
    DateField
    """
    field_type = _("Data")
    widget = forms.DateInput()
    input_formats = settings.DATE_INPUT_FORMATS

    def __init__(self, *args, **data_kwargs):
        super().__init__(*args, **data_kwargs)


class BaseDateTimeField(BaseCustomField):
    """
    DateTimeField
    """
    field_type = _("Data e Ora")
    is_complex = True

    def __init__(self, *args, **data_kwargs):
        # Data DateField
        self.data = BaseDateField(*args, **data_kwargs)
        self.data.label = _("{} (Data)").format(data_kwargs.get('label'))
        self.data.name = "{}_dyn".format(format_field_name(self.data.label))
        self.data.parent = self

        # Ore SelectBox
        self.hour = CustomSelectBoxField(*args, **data_kwargs)
        self.hour.label = _("{} (Ore)").format(data_kwargs.get('label'))
        self.hour.name = "{}_dyn".format(format_field_name(self.hour.label))
        self.hour.choices = [(i,i) for i in range(24)]
        self.hour.initial = 0
        self.hour.parent = self

        # Minuti SelectBox
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
    Field composto da DataInizio (DateField) e DataFine (DateField)
    """
    field_type = _("Data inizio e Data fine")
    is_complex = True

    def __init__(self, *args, **data_kwargs):
        # Data Inizio
        self.start = BaseDateField(*args, **data_kwargs)
        self.start.required = True
        self.start.label = _('Data Inizio')
        self.start.name = "data_inizio_dyn"

        # Riferimento a DateStartEndComplexField
        self.start.parent = self

        # Data Fine
        self.end = BaseDateField(*args, **data_kwargs)
        self.end.required = True
        self.end.label = _('Data Fine')
        self.end.name = "data_fine_dyn"

        # Riferimento a DateStartEndComplexField
        self.end.parent = self

    def get_fields(self):
        fields = [self.start, self.end]
        return fields

    def raise_error(self, name, cleaned_data, **kwargs):
        """
        Essendo un campo complesso che non ha riferimenti ai vincoli
        imposti dal bando, si eseguono solo i controlli standard sulle
        date di inizio e di fine
        """
        errors = []
        start_value = cleaned_data.get(self.start.name)
        end_value = cleaned_data.get(self.end.name)

        # Se il campo non viene correttamente inizializzato
        if not cleaned_data.get(name): return []

        # Si valuta 'Data Inizio'
        if name == self.start.name:
            # Se data_inizio > data_fine
            if end_value and start_value > end_value:
                errors.append(_("La data di inizio non può "
                                "essere successiva a quella di fine"))

        return errors


class ProtocolloField(BaseCustomField):
    """
    Tipo,Numero e Data protocollo (o altro tipo di numerazione)
    """
    field_type = "Protocollo (tipo/numero/data)"
    is_complex = True

    def __init__(self, *args, **data_kwargs):
        # Tipo protocollo. SelectBox
        self.tipo = CustomSelectBoxField(*args, **data_kwargs)
        self.tipo.label = _("Tipo Protocollo/Delibera/Decreto")
        self.tipo.name = "tipo_numerazione_dyn"
        self.tipo.help_text = _("Scegli se protocollo/decreto/delibera, "
                                "al/alla quale la numerazione è riferita")
        self.tipo.choices += [(i[0].lower().replace(' ', '_'), i[1]) \
                             for i in CLASSIFICATION_LIST]
        self.tipo.parent = self

        # Numero protocollo. CharField
        self.numero = CustomCharField(*args, **data_kwargs)
        self.numero.required = True
        self.numero.label = _("Numero Protocollo/Delibera/Decreto")
        self.numero.name = "numero_protocollo_dyn"
        self.numero.help_text = _("Indica il numero del "
                                  "protocollo/decreto/delibera")
        self.numero.parent = self

        # Data protocollo. DateField
        self.data = BaseDateField(*args, **data_kwargs)
        self.data.name = "data_protocollo_dyn"
        self.data.label = _("Data Protocollo/Delibera/Decreto")
        self.data.help_text = _("Indica la data del protocollo/delibera/decreto")
        self.data.parent = self

    def get_fields(self):
        return [self.tipo, self.numero, self.data]

    def get_data_name(self):
        return self.data.name

    def raise_error(self, name, cleaned_data, **kwargs):
        """
        Questo campo complesso subisce controlli inerenti i parametri
        imposti dal bando e allo stesso tempo si relaziona, se presente,
        a DataInizio e DataFine in range
        """
        value = cleaned_data.get(name)

        if not value: return [_("Valore mancante")]

        # Si valuta 'Data protocollo'
        if name == self.data.name:
            errors = []
            # Se la data è successiva ad oggi
            if _successivo_ad_oggi(value):
                errors.append(_("La data di protocollo non può essere"
                                " successiva ad oggi"))
            return errors


class CustomHiddenField(CharField, BaseCustomField):
    """
    CharField Hidden
    """
    field_type = _("Campo nascosto")

    def __init__(self, *args, **data_kwargs):
        super().__init__(*args, **data_kwargs)

    def define_value(self, custom_value, **kwargs):
        self.widget = forms.HiddenInput(attrs={'value': custom_value})


class DurataComeInteroField(PositiveIntegerField):
    """
    Durata come Intero positivo
    """
    field_type = _("Durata come numero intero (anni,mesi,ore)")
    name = 'durata_come_intero'

    def __init__(self, *args, **data_kwargs):
        super().__init__(*args, **data_kwargs)


class CustomComplexTableField(ChoiceField, BaseCustomField):
    """
    CustomComplexTableField
    """
    validation_error = _('Questo campo necessita di almeno una riga')
    field_type = _("Inserimenti multipli")
    is_complex = True
    is_formset = True
    choices = None

    def get_formset(self):
        if not self.choices: return
        return build_formset(choices=self.choices)

    def clean(self, *args, **kwargs):
        # Se non ci sono forms e il campo è required allora deve fare
        # l'override. In caso contrario, deve essere ignorato e il
        # clean dei campi viene delegato ai singoli form
        if self.required and not self.widget.formset.forms:
            raise ValidationError(self.validation_error)
        return

    def define_value(self, custom_value, **kwargs):
        """
        Se presenti, sostituisce alle opzioni di default
        quelle di 'custom_value'
        """
        if custom_value:
            elements = _split_choices_in_list_canc(custom_value)
            self.choices = elements
