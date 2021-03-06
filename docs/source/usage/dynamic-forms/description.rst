.. django-form-builder documentation master file, created by
   sphinx-quickstart on Tue Jul  2 08:50:49 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Build dynamic forms
===================

Now you can build your own form dynamically both in Django backend and frontend, just selecting the fields that you want,
in total flexibility and easiness.

Every form can be saved in a configurable storage, in JSON format or simply defined in a Python Dictionary.
Please see ``django_dynamic_form.dynamic_fields`` to see all the supported type.


::

    from django_form_builder.forms import BaseDynamicForm
    from collections import OrderedDict

    constructor_dict = OrderedDict([('Telefono',  # field name
                  ('CustomCharField',           # defines the FieldType
                   {'label': 'Telefono',
                    'required': True,
                    'help_text': 'Fisso o Mobile',
                    'pre_text': ''},            # a text to be rendered before the input field
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
                    'help_text': 'data di scadenza delle credenziali.',
                    'pre_text': ''},
                   '')),
                 ('Descrizione Attività',
                  ('TextAreaField',
                   {'label': 'Descrizione Attività',
                    'required': True,
                    'help_text': "Descrizione dell'attività per la quale si richiedono le credenziali",
                    'pre_text': ''},
                   '')),
                 ('Richiede che le seguenti anagrafiche vengano attivate',
                  ('CustomComplexTableField',  # a django fieldset
                   {'label': 'Richiede che le seguenti anagrafiche vengano attivate',
                    'required': True,
                    'help_text': 'inserire almeno first_name, last_name e email',
                    'pre_text': ''},
                   'first_name#last_name#place_of_birth#date_of_birth#codice_fiscale#email#tel#valid_until'))])

    form = BaseDynamicForm.get_form(#class_obj=YourCustomDynFormClass, # None by default, then use BaseDynamicForm
                                    constructor_dict=constructor_dict,
                                    custom_params=None,
                                    #data=data,   # if there's some data to load
                                    #files=files, # if there's some file attachments (handled separately)
                                    remove_filefields=False,
                                    remove_datafields=False)

--------------------------------

*Example of Dynamic Form built via frontend:*

.. thumbnail:: ../../images/dyn_form_building.png

*Preview of the builded form:*

.. thumbnail:: ../../images/dyn_form_preview.png
