import inspect

from django import template

from django_form_builder import dynamic_fields

register = template.Library()

@register.filter
def get_dyn_field_name(value):
    for m in inspect.getmembers(dynamic_fields, inspect.isclass):
        if m[0]==value: return getattr(m[1], 'field_type')
    return value

@register.simple_tag
def get_attachment_sign_details(form, field_path, field_name, field_value):
    field = form.fields.get(field_name, None)
    if field and isinstance(field, dynamic_fields.CustomSignedFileField):
        return field.get_cleaned_signature_params('{}/{}'.format(field_path, field_value))
    return False
