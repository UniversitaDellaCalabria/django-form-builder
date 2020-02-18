import json

from collections import OrderedDict
from django.db import models

from . dynamic_fields import get_fields_types
from . forms import BaseDynamicForm
from . utils import get_as_dict

class DynamicFieldMap(models.Model):
    """
    """
    name = models.CharField(max_length=150,)
    field_type = models.CharField(max_length=100,
                                  choices = get_fields_types())
    valore = models.CharField(max_length=255,
                              blank=True,
                              default='',
                              verbose_name='Lista di Valori',
                              help_text="Viene considerato solo se si sceglie"
                                        " 'Menu a tendina' oppure 'Serie di Opzioni'."
                                        " (Es: valore1;valore2;valore3...)")
    is_required = models.BooleanField(default=True)
    aiuto = models.CharField(max_length=254, blank=True, default='')
    ordinamento = models.PositiveIntegerField(help_text="posizione nell'ordinamento",
                                              blank=True,
                                              default=0)

    @staticmethod
    def build_constructor_dict(fields):
        """
        costruisco il dizionario da dare in pasto
        al costruttore del form dinamico
        """
        constructor_dict = OrderedDict()
        for field in fields:
            d = {'label': field.name,
                 'required' : field.is_required,
                 'help_text' : field.aiuto}
            constructor_dict[field.name] = (field.field_type,
                                            d, field.valore)
        return constructor_dict

    @staticmethod
    def get_form(class_obj=BaseDynamicForm,
                 constructor_dict={},
                 custom_params={},
                 remove_filefields=False,
                 remove_datafields=False,
                 fields_order=[],
                 *args, **kwargs):
        if class_obj == BaseDynamicForm:
            custom_params = {}
        form = class_obj(constructor_dict=constructor_dict,
                         custom_params=custom_params,
                         *args, **kwargs)

        if remove_filefields:
            form.remove_files(allegati = remove_filefields)
        if remove_datafields:
            form.remove_datafields()
        if fields_order:
            form.order_fields(fields_order)
        return form

    class Meta:
        abstract = True
        ordering = ('ordinamento',)


class SavedFormContent(models.Model):
    """
    """
    # libreria esterna oppure cambio client per JsonField
    # non serve gestirlo come JsonField perchè non vi facciamo ricerche al suo interno ;)
    modulo_compilato = models.TextField()

    @staticmethod
    def compiled_form(data_source=None,
                      constructor_dict={},
                      files=None,
                      remove_filefields=True,
                      remove_datafields=False,
                      form_source=None,
                      # fields_order=[],
                      extra_datas={},
                      **kwargs):
        json_dict = json.loads(data_source)
        data = get_as_dict(json_dict, allegati=False)
        if extra_datas:
            for k,v in extra_datas.items():
                data[k]=v
        if not form_source:
            form_source = DynamicFieldMap
        form = form_source.get_form(constructor_dict=constructor_dict,
                                    data=data,
                                    files=files,
                                    remove_filefields=remove_filefields,
                                    remove_datafields=remove_datafields,
                                    **kwargs)
        # Già invocato nel "form_source", ma è bene tenerlo come riferimento
        # if fields_order:
            # form.order_fields(fields_order)
        return form

    @staticmethod
    def compiled_form_readonly(form, attr='disabled', fields_to_remove=[]):
        """
        Restituisce una versione "più pulita" di compiled_form
        - I field non compilati non vengono mostrati (remove_not_compiled_fields())
        - Il campo "titolo" di default non viene mostrato
        - I fields sono readonly
        NOTA: i field select non risentono dell'attributo readonly!!!
        Usato nei metodi che producono le anteprime non modificabili
        dei moduli compilati
        """
        form.remove_not_compiled_fields()
        for field_to_remove in fields_to_remove:
            del form.fields[field_to_remove]
        for generic_field in form:
            field = form.fields[generic_field.name]
            widget = field.widget
            widget.attrs[attr] = True
            # If field is a Formset, the widget will make it readonly
            if field.is_formset:
                widget.make_readonly(attr)
                continue
            # Es: TextArea non ha attributo 'input_type'
            # Senza questo controllo il codice genera un'eccezione
            if not hasattr(widget, 'input_type'):
                # widget.attrs[attr] = True
                continue
            tipo = widget.input_type
            if tipo in ['select', 'checkbox', 'radiobox']:
                widget.attrs['disabled'] = True
            # else:
                # widget.attrs[attr] = True
        return form

    class Meta:
        abstract = True
