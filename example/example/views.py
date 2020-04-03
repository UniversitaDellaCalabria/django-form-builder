from collections import OrderedDict

from django.http import HttpResponse
from django_form_builder.forms import BaseDynamicForm
from django_form_builder.models import DynamicFieldMap
from django.views.decorators.csrf import csrf_exempt



constructor_dict = OrderedDict([
            ('Telefono',
              ('CustomCharField',
               {'label': 'Telefono',
                'required': True,
                'help_text': 'Fisso o Mobile',
                'pre_text': ''},
               '')),
             ('Credenziali attive dal',
              ('BaseDateField',
               {'label': 'Credenziali attive dal',
                'required': True,
                'help_text': 'Data di attivazione delle credenziali',
                'pre_text': ''},
               '')),
             ('al',
              ('BaseDateField',
               {'label': 'al',
                'required': True,
                'help_text': 'data di scadenza delle credenziali. ATTENZIONE: non saranno considerati valori superiori ai 2 anni.',
                'pre_text': ''},
               '')),
             ('Descrizione Attività',
              ('TextAreaField',
               {'label': 'Descrizione Attività',
                'required': True,
                'help_text': "Descrizione dell'attività per la quale si richiedono le credenziali",
                'pre_text': ''},
               '')),
             ('CaPTCHA',
              ('CustomCaptchaComplexField',
               {'label': 'CaPTCHA',
                'pre_text': ''},
               '')),
             #('Richiede che le seguenti anagrafiche vengano attivate',
              #('CustomComplexTableField',
               #{'label': 'Richiede che le seguenti anagrafiche vengano attivate',
                #'required': True,
                #'help_text': 'inserire almeno first_name, last_name e email',
                #'pre_text': ''},
               #'first_name#last_name#place_of_birth#date_of_birth#codice_fiscale#email#tel#valid_until'))
    ]
)


@csrf_exempt
def dynform(request):
    #context = {'form': form}
    page = """<form method=POST>
                  <table>
                    {}
                  </table>
                  <button type='submit'>Submit</button>
              </form>
              """

    if request.method == 'GET':
        form = DynamicFieldMap.get_form(BaseDynamicForm,
                                    constructor_dict=constructor_dict,
                                    custom_params=None,
                                    #data=data,
                                    #files=files,
                                    remove_filefields=False,
                                    remove_datafields=False)
        return HttpResponse(page.format(form.as_table()))
    else:
        form = DynamicFieldMap.get_form(BaseDynamicForm,
                                    constructor_dict=constructor_dict,
                                    custom_params=None,
                                    data=request.POST,
                                    files=request.FILES,
                                    remove_filefields=False,
                                    remove_datafields=False)
        
        if not form.is_valid():
            return HttpResponse(page.format(form.as_table()))
        else:
            return HttpResponse('form is valid')
