import copy

from django import forms
from django.conf import settings
from django.forms.fields import FileField
from django.template.defaultfilters import filesizeformat
from django.utils.module_loading import import_string


from . import dynamic_fields
from . dynamic_fields import CaptchaField, CaptchaHiddenField
from . utils import _split_choices_in_list_canc
from . widgets import FormsetdWidget


class BaseDynamicForm(forms.Form):
    def __init__(self,
                 fields_source=dynamic_fields,
                 initial_fields={},
                 constructor_dict={},
                 custom_params={},
                 ignore_format_field_name=False,
                 *args,
                 **kwargs):
        """
        initial_fields:
        dyn_constructor_dict:
        example:

        """
        super().__init__(*args, **kwargs)        
        self.fields = initial_fields or self.fields
        # Costruzione dinamica dei rimanenti fields del form
        if constructor_dict:
            constructor_dict = copy.deepcopy(constructor_dict)
            for key, value in constructor_dict.items():
                if ignore_format_field_name:
                    field_id = key
                else:
                    field_id = dynamic_fields.format_field_name(key)
                data_kwargs = {'label': key.title()}
                custom_field_name = value[0]
                custom_field_dict = value[1]
                pre_text = custom_field_dict.pop('pre_text')
                custom_field_values = value[2]
                # add custom attrs
                data_kwargs.update(custom_field_dict)
                custom_field = None
                if hasattr(fields_source, custom_field_name):
                    custom_field = getattr(fields_source,
                                           custom_field_name)(**data_kwargs)
                if custom_field:
                    custom_field.define_value(custom_field_values, **custom_params)
                    fields = custom_field.get_fields()
                    for field in fields:
                        name = getattr(field, 'name') if hasattr(field, 'name') else field_id
                        self.fields[name]= field
                        self.fields[name].pre_text = pre_text
                        if isinstance(field,
                                      dynamic_fields.CustomComplexTableField):
                            choices = _split_choices_in_list_canc(custom_field_values)
                            self.fields[name].widget = FormsetdWidget(choices=choices,
                                                                      data=kwargs.get('data', {}),
                                                                      field_required=field.required,
                                                                      prefix=name)
                        else:
                            custom_widget = getattr(settings, 'CUSTOM_WIDGETS', {}).get(field.__class__.__name__)
                            # Questo consente al widget di essere dichiarato anche come Tipo e non sempre come Stringa
                            if not custom_widget:
                                custom_widget = self.fields[name].widget
                            if isinstance(custom_widget, str):
                                self.fields[name].widget = import_string(custom_widget)()
                            else:
                                self.fields[name].widget = custom_widget
                            if hasattr(field, 'choices'):
                                self.fields[name].choices = getattr(field, 'choices')

    def remove_not_compiled_fields(self):
        """
        Rimuove da un form compilato tutti i campi non compilati
        Viene usato nel metodo get_form
        """
        to_be_removed = []
        for field in self:
            form_field = self.fields[field.name]

            # remove not compiled single fields in formset
            if form_field.is_formset:
                formset = form_field.widget.formset
                for fform in formset:
                    to_be_removed_formset = []
                    for generic_field in fform:
                       if not generic_field.value():
                            to_be_removed_formset.append(generic_field.name)
                    for i in to_be_removed_formset:
                        del fform.fields[i]
                continue

            if not field.value():
                to_be_removed.append(field.name)
        for i in to_be_removed:
            del self.fields[i]

    def remove_datafields(self):
        """
        """
        to_be_removed = []
        for field in self.fields:
            if not isinstance(self.fields[field], FileField):
                # rimuove tutti i fields  che non sono File
                to_be_removed.append(field)
        for i in to_be_removed:
            del self.fields[i]

    def remove_files(self, allegati = None):
        """
        Rimuove tutti i FileFields
        viene usato in modifica_form se allegati già presenti
        """
        to_be_removed = []
        for field in self.fields:
            if isinstance(allegati, dict):
                # rimuove solo i fields allegati/files specificati
                if field in allegati:
                    to_be_removed.append(field)
            elif isinstance(self.fields[field], FileField):
                # rimuove tutti i fields  allegati/files
                to_be_removed.append(field)
        for i in to_be_removed:
            del self.fields[i]

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean()

        self.data = copy.deepcopy(self.data)
        # CaPTCHA MUST BE ALWAYS RENEWED!
        for field_name, field_obj in self.fields.items():
            if type(field_obj) in (CaptchaField, CaptchaHiddenField):
                self.data[field_name] = self.fields[field_name].widget.attrs['value']
        # end CAPTCHA
        
        for fname in self.fields:
            field = self.fields[fname]
            # formset is empty or not valid
            if field.is_formset and not field.widget.formset.is_valid():
                errors = field.widget.formset.errors
                self.add_error(fname, errors)
                continue
            # other fields check
            if hasattr(field, 'parent'):
                field = getattr(field, 'parent')
                errors = field.raise_error(fname,
                                           cleaned_data,
                                           **kwargs)
            else:
                errors = field.raise_error(None,
                                           cleaned_data.get(fname),
                                           **kwargs)
            if errors:
                self.add_error(fname, errors)
                continue

    class Media:
        js = ('js/formset_js.js',)
