import ast
import re
import sys
from django import forms
from django.conf import settings
from django.utils.module_loading import import_string

from . settings import CUSTOM_WIDGETS_IN_FORMSETS
from . utils import format_field_name, _split_choices


def get_empty_form(form_class=forms.Form):
    class Dynamic(form_class):
        pass
    return Dynamic


def build_formset(choices, extra=0, required=False, prefix='form', data={}, files={}):
    """ Get formset
    """
    _regexp = '(?P<colname>[a-zA-Z0-9À-ÿ\'\"\_ ]*)\((?P<coldict>[\{\}\.0-9a-zA-ZÀ-ÿ\'\"\:\;\_\,\s\- ]*)\)'
    min_num = 0
    if required: min_num = 1
    eform = get_empty_form()
    for choice in choices:
        colname = format_field_name(choice) # needed for simple CharField withoud attrs
        contenuto = re.search(_regexp, choice)
        field_dict = None
        mod_name = __package__ + '.dynamic_fields'
        sysmod = sys.modules[mod_name]
        if contenuto:
            coldict = contenuto.groupdict().get('coldict')
            colname = format_field_name(contenuto.groupdict()['colname'])
            if coldict:
                field_dict = ast.literal_eval(coldict)
                field_type_name = field_dict['type']
                del field_dict['type']
                custom_field = getattr(sysmod, field_type_name)(**field_dict) \
                               if hasattr(sysmod, field_type_name) \
                               else getattr(sysmod, 'CustomCharField')()
                # choice if use or not fields custom widget
                # javascript may cause some problem
                use_custom_widget = getattr(settings, 'CUSTOM_WIDGETS_IN_FORMSETS', CUSTOM_WIDGETS_IN_FORMSETS)
                if use_custom_widget:
                    custom_widget = getattr(settings, 'CUSTOM_WIDGETS').get(field_type_name) \
                                    if hasattr(settings, 'CUSTOM_WIDGETS') else None
                    if custom_widget:
                        custom_field.widget = import_string(custom_widget)()

                if field_dict.get('choices'):
                    custom_field.choices += _split_choices(field_dict.get('choices'))
        else:
            # custom_field = forms.CharField()
            custom_field = getattr(sysmod, 'CustomCharField')()
        eform.base_fields[colname] = custom_field
        eform.declared_fields[colname] = custom_field

    # Django formset
    fac =  forms.formset_factory(eform, extra=extra, min_num=min_num)
    if data:
        return fac(prefix=prefix, data=data, files=files)
    return fac(prefix=prefix)
