from collections import OrderedDict

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import strip_tags

from django_form_builder.forms import BaseDynamicForm
from django_form_builder.utils import get_labeled_errors


# this is the dictionary that builds the DynamicForm
constructor_dict = OrderedDict([
    # CharField
    ('Telefono',
        ('CustomCharField',
            {'label': 'Telefono',
             'required': True,
             'help_text': 'Fisso o Mobile',
             'pre_text': ''},
            '')
    ),
    # Complex field (start date / end date)
    ('Credenziali attive dal/al',
        ('DateStartEndComplexField',
            {'label': 'Credenziali attive dal/al',
             'required': True,
             'help_text': 'Data di attivazione e disattivazione delle credenziali',
             'pre_text': ''},
            '')
    ),
    # TextField
    ('Descrizione Attività',
        ('TextAreaField',
            {'label': 'Descrizione Attività',
             'required': True,
             'help_text': "Descrizione dell'attività per la quale si richiedono le credenziali",
             'pre_text': ''},
            '')
    ),
    # Formset
    ('Richiede che le seguenti anagrafiche vengano attivate',
        ('CustomComplexTableField',
            {'label': 'Richiede che le seguenti anagrafiche vengano attivate',
             'required': True,
             'help_text': '',
             'pre_text': 'This is a formset, this text is printed before rendering field'},
            # Columns of tables with different field types
            'first_name({"type":"CustomSelectBoxField","choices":"v1;v2;v3"})'
            '#'
            'last_name'
            '#'
            'place_of_birth'
            '#'
            'date_of_birth'
            '#'
            'codice_fiscale'
            '#'
            'email({"type":"CustomEmailField"})'
            '#'
            'tel({"type":"PositiveIntegerField"})'
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


@csrf_exempt
def dynform(request):
    if request.method == 'GET':
        form = BaseDynamicForm.get_form(constructor_dict=constructor_dict,
                                        #data=data,
                                        #files=files,
                                        remove_filefields=False,
                                        remove_datafields=False)
    # if POST (form submitted)
    else:
        form = BaseDynamicForm.get_form(constructor_dict=constructor_dict,
                                        data=request.POST,
                                        files=request.FILES,
                                        remove_filefields=False,
                                        remove_datafields=False)

        if form.is_valid():
            messages.add_message(request, messages.SUCCESS, "form is valid")
        else:
            # show all error messages
            for k,v in get_labeled_errors(form).items():
                messages.add_message(request, messages.ERROR,
                                     "<b>{}</b>: {}".format(k, strip_tags(v)))

    d = {'form': form}
    return render(request, "form.html", d)
