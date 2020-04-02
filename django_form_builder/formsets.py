import re
from django import forms


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
                custom_field = getattr(sys.modules[__name__], field_type_name)(**field_dict) \
                               if hasattr(sys.modules[__name__], field_type_name) else CustomCharField()
                custom_widget = getattr(settings, 'CUSTOM_WIDGETS').get(field_type_name) \
                                if hasattr(settings, 'CUSTOM_WIDGETS') else None
                if custom_widget:
                    custom_field.widget = import_string(custom_widget)()

                if field_dict.get('choices'):
                    custom_field.choices += _split_choices(field_dict.get('choices'))
        else:
            custom_field = forms.CharField()
        eform.base_fields[colname] = custom_field
        eform.declared_fields[colname] = custom_field

    # Django formset
    fac =  forms.formset_factory(eform, extra=extra, min_num=min_num)
    if data: return fac(prefix=prefix, data=data)
    return fac(prefix=prefix)
