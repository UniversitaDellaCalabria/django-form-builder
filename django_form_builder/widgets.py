import base64
import re

from django import forms
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from . captcha import get_captcha
from . enc import encrypt, decrypt
from . formsets import build_formset
from . settings import FORMSET_TEMPLATE_NAMEID


FORMSET_TEMPLATE_NAMEID = getattr(settings, 'FORMSET_TEMPLATE_NAMEID',
                                  FORMSET_TEMPLATE_NAMEID)


class CaptchaWidget(forms.Widget):
    template_name = 'widgets/captcha.html'

    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget as an HTML string."""
        context = self.get_context(name, value, attrs)
        # captcha = get_captcha(value)
        captcha = get_captcha(self.attrs['value'])

        context['image_b64'] = base64.b64encode(captcha.read()).decode()
        context['widget']['value'] = ''
        context['widget']['hidden_field'] = self.attrs['hidden_field']

        inline_code = mark_safe(
            '<script>'
            'function refresh_captcha(){{'
                '$.get(location.href, function(data) {{'
                    '$("#{name}_img").attr("src",($(data).find("#{name}_img").attr("src")));'
                    '$("#{hidden_field}").val($(data).find("#{hidden_field}").val());'
                '}});'
            '}}'
            '</script>'.format(name=name,
                               hidden_field=self.attrs['hidden_field'])
        )

        return self._render(self.template_name, context, renderer) + inline_code


class FormsetdWidget(forms.Widget):

    def __init__(self, *attrs, **kwargs):
        self.template = 'widgets/formset.html'
        self.readonly = False
        init_data_list = ['choices', 'data']
        field_required = kwargs.pop('field_required')
        self.prefix = kwargs.pop('prefix')
        for i in init_data_list:
            if i in kwargs.keys():
                setattr(self, i, kwargs.pop(i))

        if getattr(self, 'data'):
            # It MUST be a list!
            # self.data = [{'ccc': 'dfgdfgdfg', 'co': 'sono', 'col1': 'un', 'data': '2019-04-03'},
            #              {'ccc': '234234', 'co': 'son44o', 'col1': 'un333', 'data': '2016-04-03'}]
            self.formset = build_formset(choices=self.choices,
                                         required=field_required,
                                         prefix=self.prefix,
                                         data=self.data)
            self.formset.is_valid()
        else:
            # this initialized the formset as void
            self.formset = build_formset(choices=self.choices,
                                         required=field_required,
                                         extra=0,
                                         prefix=self.prefix)
        super().__init__(*attrs, **kwargs)

    def get_js_template(self):
        formset = build_formset(choices=self.choices,
                                prefix=self.prefix,
                                extra=1)
        res = re.sub('{}-0'.format(self.prefix),
                     '{}-{}'.format(self.prefix,
                                    FORMSET_TEMPLATE_NAMEID),
                     formset.forms[0].as_table())
        return mark_safe(res)

    def render(self, name='', value='', attrs=None, renderer=None):
        context_data = {'formset_id': self.prefix,
                        'template_generic_id': FORMSET_TEMPLATE_NAMEID,
                        'formset': self.formset,
                        'formset_template': self.get_js_template(),
                        'readonly': self.readonly,}
        html_output = render_to_string(self.template, context_data)
        return mark_safe(html_output)

    def make_readonly(self, attr='disabled'):
        self.readonly = True
        for form in self.formset:
            for generic_field in form:
                field = form.fields[generic_field.name]
                widget = field.widget
                widget.attrs[attr] = True
        return True
