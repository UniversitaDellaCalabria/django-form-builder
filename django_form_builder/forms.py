import copy
import re

from collections import OrderedDict
from django import forms
from django.conf import settings
from django.forms.fields import FileField
from django.http import QueryDict
from django.template.defaultfilters import filesizeformat
from django.utils.module_loading import import_string

from . import dynamic_fields
from . settings import FORMSET_REGEX
from . utils import format_field_name, _split_choices_in_list_canc
from . widgets import FormsetdWidget


def _remove_filefields_from_formset(formset):
    for f_form in formset.forms:
        to_be_removed_formset = []
        for f_field in f_form.fields:
            if not isinstance(f_form.fields[f_field], FileField):
                to_be_removed_formset.append(f_field)
        for i in to_be_removed_formset:
            del f_form.fields[i]


class BaseDynamicForm(forms.Form):
    def __init__(self,
                 fields_source=dynamic_fields,
                 initial_fields={},
                 final_fields={},
                 constructor_dict={},
                 custom_params={},
                 ignore_format_field_name=False,
                 *args,
                 **kwargs):
        """
        Base class for form building.
        User custom forms have to inherit from this.
        Example: class MyCustomFormClass(BaseDynamicForm)

        :type fields_source: String
        :type initial_fields: dict
        :type final_fields: dict
        :type constructor_dict: OrderedDict
        :type custom_params: dict
        :type ignore_format_field_name: boolean

        :param fields_source: fields source file (default: dynamic_fields.py, but you can create your own to extend dynamic_fields.py)
        :param initial_fields: static initial fields to render in every instance of your form
        :param final_fields: static final fields to render in every instance of your form
        :param constructor_dict: form fields to render between initial and final fields
        :param custom_params: extra params you may need your own form
        :param ignore_format_field_name: choose if build or not fields names from labels (dynamic_fields.format_field_name() method)

        :example initial_fields:
        # Generate static NAME field
        name_id = format_field_name("Personal name")
        # Set NAME field data
        name_data = {'required' : True,
                     'label': "Name",
                     'help_text': "Your help-text"}
        # Build NAME field (define type and pass arguments)
        name_field = getattr(dynamic_fields, 'CustomCharField')(**name_data)
        # Put NAME field in initial_fields{}
        self.initial_fields[name_id] = name_field

        :example final_fields:
        same as initial_fields, but use initial_fields{} dict

        :example constructor_dict
        constructor_dict = OrderedDict([
            # CharField
            ('Phone',
                ('CustomCharField',
                    {'label': 'Phone number',
                     'required': True,
                     'help_text': 'Mobile',
                     'pre_text': ''},
                    '')
            ),
            # Complex field (start date / end date)
            ('From to',
                ('DateStartEndComplexField',
                    {'label': 'From to',
                     'required': True,
                     'help_text': 'From date to date',
                     'pre_text': ''},
                    '')
            ),
            # Formset
            ('Formset data',
                ('CustomComplexTableField',
                    {'label': 'Formset data',
                     'required': True,
                     'help_text': '',
                     'pre_text': 'This is a formset, this text is printed before rendering field'},
                    # Columns of tables with different field types
                    'select_option({"type":"CustomSelectBoxField","choices":"v1;v2;v3"})'
                    '#'
                    'simple_text'
                    '#'
                    'email({"type":"CustomEmailField"})'
                    '#'
                    'phone({"type":"PositiveIntegerField"})'
                    '#'
                    'valid_until({"type":"BaseDateField"})')
            ),
            # Captcha
            ('CaPTCHA',
                ('CustomCaptchaComplexField',
                    {'label': 'CaPTCHA',
                     'pre_text': ''},
                    '')
            ),
        ])

        :example custom_params:
        custom_params = {'my_custom_param': True,
                         'another_param_to_pass_to_form': 'value',}
        """
        super().__init__(*args, **kwargs)

        # if initial fields are present
        # form fields start from them
        self.fields = initial_fields or self.fields

        # if there's a constructor_dict
        # start fields building
        if constructor_dict:

            # make a deepcopy avoiding to edit dict passed as argument
            constructor_dict = copy.deepcopy(constructor_dict)

            # for every key in dict, start building field
            for key, value in constructor_dict.items():

                # if ignore_format_field_name
                # then field_id is the key
                if ignore_format_field_name:
                    field_id = key
                # else build id with utility method
                else:
                    field_id = format_field_name(key)

                # start building field data kwargs
                # default contructor data (capitalize key for label)
                data_kwargs = {'label': key.title()}

                # see constructor_dict example in docstring
                # This is constructor_dict element value for key 'Phone'
                # ('CustomCharField',
                #  {'label': 'Phone number',
                #   'required': True,
                #   'help_text': 'Mobile',
                #   'pre_text': ''},
                # '')

                # value[0] is field_type (CustomCharField in this case)
                custom_field_name = value[0]

                # value[1] is field data dict (label, required, etc...)
                custom_field_dict = value[1]

                # value[2] is field value (if needed from field.)
                # Empty in this example case
                custom_field_values = value[2]

                # get field pre_text (if key exists) and pop from dict
                pre_text = ''
                if 'pre_text' in custom_field_dict.keys():
                    pre_text = custom_field_dict.pop('pre_text')

                # update field data kwargs
                data_kwargs.update(custom_field_dict)

                # get field object from fields_source
                custom_field = self._get_object_from_fields_source(fields_source,
                                                                   custom_field_name,
                                                                   data_kwargs)

                # if field has been created
                if custom_field:
                    # call define_value method to set field value
                    # and pass custom_params dict if it needs
                    custom_field.define_value(custom_field_values,
                                              **custom_params)

                    # if custom_field is a complex field returns a list with two or more elements.
                    # if it's a simple field returns a list with one element
                    fields = custom_field.get_fields()

                    # for every field in custom field
                    for field in fields:
                        # set name
                        name = getattr(field, 'name', field_id)

                        # add field to form fields (self.fields)
                        self.fields[name]= field

                        # if pre_text is setted add it to form field
                        if pre_text:
                            self.fields[name].pre_text = pre_text

                        # if is a Formset
                        if isinstance(field,
                                      dynamic_fields.CustomComplexTableField):

                            # get formset choices with the utility method
                            # _split_choices_in_list_canc()
                            # (pass custom_field_values string as argument, see above)
                            choices = _split_choices_in_list_canc(custom_field_values)

                            # add formset widget to form field
                            self.fields[name].widget = FormsetdWidget(choices=choices,
                                                                      data=kwargs.get('data',{}),
                                                                      files=kwargs.get('files',{}),
                                                                      field_required=field.required,
                                                                      prefix=name)
                        # else if field isn't a Formset
                        else:
                            # get a custom widget (if user has defined it in its settings file)
                            custom_widget = getattr(settings, 'CUSTOM_WIDGETS', {}).get(field.__class__.__name__)

                            # if theresn't a custom widget, then apply the standard field widget
                            if not custom_widget:
                                custom_widget = self.fields[name].widget

                            # Manage widget declaration
                            # (class or string? manage both)
                            if isinstance(custom_widget, str):
                                self.fields[name].widget = import_string(custom_widget)()
                            else:
                                self.fields[name].widget = custom_widget

                            # set form field choices attribute
                            if hasattr(field, 'choices'):
                                self.fields[name].choices = getattr(field, 'choices')

        # if final fields are present append them to form
        self.fields.update(final_fields)

    def _get_object_from_fields_source(self,
                                       fields_source,
                                       field_name,
                                       data):
        """
        if fields_source defines custom_field_name class,
        get an instance of that class ad pass data to it
        """
        if not fields_source: return False
        if not field_name: return False
        if hasattr(fields_source, field_name):
            return getattr(fields_source, field_name)(**data)
        return False

    def remove_not_compiled_fields(self):
        """
        Remove all not filled fields from a compiled form.
        Used in get_form() method
        """
        to_be_removed = []
        for field in self:
            form_field = self.fields[field.name]

            # remove not compiled single fields in formset
            if form_field.is_formset:
                formset = form_field.widget.formset
                for f_form in formset:
                    to_be_removed_formset = []
                    for generic_field in f_form:
                       if not generic_field.value():
                            to_be_removed_formset.append(generic_field.name)
                    for i in to_be_removed_formset:
                        del f_form.fields[i]
                continue

            if not field.value():
                to_be_removed.append(field.name)
        for i in to_be_removed:
            del self.fields[i]

    def remove_datafields(self):
        """
        Remove all fields different from FileField
        """
        to_be_removed = []
        for field in self.fields:
            if isinstance(self.fields[field], dynamic_fields.CustomComplexTableField):
                _remove_filefields_from_formset(self.fields[field].widget.formset)
            elif not isinstance(self.fields[field], FileField):
                to_be_removed.append(field)
        for i in to_be_removed:
            del self.fields[i]

    def remove_files(self, allegati=None):
        """
        Remove all FileFields.
        Used in edit form if attachments are present
        """
        REGEX = getattr(settings, 'FORMSET_REGEX', FORMSET_REGEX)
        to_be_removed = []
        for field in self.fields:
            if isinstance(allegati, dict):
                for allegato in allegati:
                    if field==allegato:
                        to_be_removed.append(field)
                    else:
                        formset_regex = re.match(FORMSET_REGEX.format(field), allegato)
                        if formset_regex:
                            index = int(formset_regex['index'])
                            name = formset_regex['name']
                            formset = self.fields[field].widget.formset
                            try:
                                del formset.forms[index].fields[name]
                            except Exception: continue # nosec
            else:
                # remove all attachments/files
                if isinstance(self.fields[field], FileField):
                    to_be_removed.append(field)
                elif isinstance(self.fields[field], dynamic_fields.CustomComplexTableField):
                    _remove_filefields_from_formset(self.fields[field].widget.formset)
        for i in to_be_removed:
            del self.fields[i]

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean()

        self.data = copy.deepcopy(self.data)

        # CaPTCHA MUST BE ALWAYS RENEWED!
        for field_name, field_obj in self.fields.items():
            if type(field_obj) in (dynamic_fields.CaptchaField,
                                   dynamic_fields.CaptchaHiddenField):
                self.data[field_name] = self.fields[field_name].widget.attrs['value']
        # end CAPTCHA

        for fname in self.fields:
            field = self.fields[fname]

            # formset is empty or not valid
            if field.is_formset:
                if not field.widget.formset:
                    continue
                for f_form in field.widget.formset.forms:
                    for f_field_name in f_form.fields:
                        f_field = f_form.fields[f_field_name]
                        if not hasattr(f_field, 'raise_error'):
                            continue
                        errors = f_field.raise_error(f_field_name,
                                                     f_form.cleaned_data.get(f_field_name),
                                                     **kwargs)
                        if errors:
                            f_form.add_error(f_field_name, errors)
                    if not f_form.is_valid():
                        f_form_errors = f_form.errors.as_data()
                        for error_field in f_form_errors:
                            if error_field in f_form.fields:
                                self.add_error(fname, f_form_errors[error_field])

            if not hasattr(field, 'raise_error'):
                continue

            # other fields check
            # if field is a child of a complex field
            if hasattr(field, 'parent'):
                field = getattr(field, 'parent')
                errors = field.raise_error(fname,
                                           cleaned_data,
                                           **kwargs)
            # else if is a simple field
            else:
                errors = field.raise_error(None,
                                           cleaned_data.get(fname),
                                           **kwargs)

            # if errors are present
            if errors:
                self.add_error(fname, errors)

    @staticmethod
    def build_constructor_dict(fields):
        """
        Static method that builds the constructor_dict OrderedDict
        from a list/queryset of fields.
        Useful when fields are managed by RDBMS
        """
        constructor_dict = OrderedDict()
        for field in fields:
            field_params = {'label': field.name,
                            'required' : field.is_required,
                            'help_text' : field.aiuto,
                            'pre_text': getattr(field, 'pre_text', '')}
            constructor_dict[field.name] = (field.field_type,
                                            field_params,
                                            field.valore)
        return constructor_dict

    @classmethod
    def get_form(cls,
                 class_obj=None,
                 constructor_dict={},
                 custom_params={},
                 remove_filefields=False,
                 remove_datafields=False,
                 fields_order=[],
                 *args, **kwargs):
        """
        Static method that builds a form from a constructor_dict,
        custom_params (if present) and a source class (class_obj)
        """
        # form = class_obj(constructor_dict=constructor_dict,
                         # custom_params={} if class_obj == BaseDynamicForm else custom_params,
                         # *args, **kwargs)
        constructor_class = class_obj or cls
        form = constructor_class(constructor_dict=constructor_dict,
                                 custom_params=custom_params,
                                 *args, **kwargs)

        if remove_filefields:
            form.remove_files(allegati=remove_filefields)
        if remove_datafields:
            form.remove_datafields()
        if fields_order:
            form.order_fields(fields_order)
        return form

    class Media:
        # javascript to formset dynamic management
        js = ('js/formset_js.js',)
