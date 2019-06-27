.. django-form-builder documentation master file, created by
   sphinx-quickstart on Tue Jul  2 08:50:49 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Create your DynamicFormClass and add static fields
==================================================

If you need some static field in your form, than you can define a new Form Class, inheriting *BaseDynamicForm*

.. code-block:: python

   from django_form_builder import dynamic_fields
   from django_form_builder.forms import BaseDynamicForm

   class MyDynamicForm(BaseDynamicForm):
       def __init__(self,
		    constructor_dict={},
		    custom_params={},
		    *args,
		    **kwargs):
	  # Add a custom static field common to all dynamic forms
	  self.fields = {}
          my_static_field = dynamic_fields.format_field_name(choice_field_name)
          my_static_field_data = {'required' : True,
		              	  'label': choice_field_label,
		              	  'help_text': choice_field_helptext}
	  my_static_field = getattr(dynamic_fields,
                                   'CustomFieldClass')(**my_static_field_data)
	  self.fields[my_static_field_id] = my_static_field
          self.fields[my_static_field_id].initial = self.descrizione_indicatore
	    
	  # call super() constructor to build form
	  super().__init__(# define it only if you
                           # define a custom field source,
                           # see "Create your own fields" paragraph.
                           # fields_source=dynamic_fields_integration,
                           initial_fields=self.fields,
 		           constructor_dict=constructor_dict,
		           custom_params=custom_params,
		           *args, **kwargs)
	  
       # if needed, override clean() method with your own params
       def clean(self, *args, **kwargs):
           cleaned_data = super().clean(own_param=own_value)
