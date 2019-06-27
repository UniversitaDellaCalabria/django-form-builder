.. django-form-builder documentation master file, created by
   sphinx-quickstart on Tue Jul  2 08:50:49 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Configure your project to use dynamic forms
===========================================

- **Step 1**
  
  Every Dynamic Form needs a table to store the list of fields that compose it.

  Also, it has to be strictly linked to a project model entity to be rendered 
  (e.g. what kind of object wil the form map? A Book, a Car or something else!?).

  In your project's models, then, create a Model Class to store the list of fields,
  make it inherit class ``DynamicFieldMap`` and choose the ForeignKey that represents the
  form linked model entity.

  .. code-block:: python
   
     from django_form_builder.dynamic_fields import get_fields_types
     from django_form_builder.models import DynamicFieldMap
     
     class MyFieldsListModel(DynamicFieldMap):
         """
	 This class represents every single form field, each one linked to a unique object
         """          

         # if you want to integrate dynamic fields with your own,
         # define a new file that import all 'dynamic_fields' and defines others new and
         # then pass it as param to get_fields_types(class_name=my_custom_fields_file)

         my_entity = models.ForeignKey(MyEntityClass, on_delete=models.CASCADE)
         DynamicFieldMap._meta.get_field('field_type').choices = get_fields_types()
         
- **Step 2**
  
  Every submitted *dynamic form*, if valid, save its content as a JSON.
  Once we have our fields model (step 1), we have to define a Model Class to save our compiled form JSON attribute.
  
  .. code-block:: python
   
     from django_form_builder.models import SavedFormContent
     
     class MyModelClass(SavedFormContent):
         """
	 This class contains the JSON with all submitted form details
         """
         ...

- **Step 3**
  
  In your views, use/override ``get_form()`` and ``compiled_form()`` methods to respectively build form structure from scratch (using your *step 1* model class) 
  and rebuild and fill it simply by the JSON field.
  
  .. code-block:: python
   
     from django_form_builder.models import DynamicFieldMap
     
     ...

     # the class used as foreign key in 'Step 1'
     class MyEntityClass(models.Model):

	  ...
	  
          def get_form(self,
                       data=None,
                       files=None,
                       remove_filefields=False,
                       remove_datafields=False,
                       **kwargs):
            """
	    Returns the form (empty if data=None)
            if remove_filefields is not False, remove from form the passed FileFields
            if remove_datafields is True, remove all fields different from FileFields
            """
	    # retrieve all the fields (the model class is in 'Step 1')
            form_fields_from_model = self.myfieldslistmodel.all().order_by('ordinamento')
            if not form_fields_from_model: return None
            # Static method of DynamicFieldMap that build the constructor dictionary
            constructor_dict = DynamicFieldMap.build_constructor_dict(form_fields_from_model)
	
	    # more params to pass with 'data'
            custom_params = {'extra_1': value_1,
                             'extra_2': value_2}
	    # the form retrieved by calling get_form() static method
            form = DynamicFieldMap.get_form(# define it only if you 
                                            # need your custom form:
                                            # class_obj=MyDynamicForm,
                                            constructor_dict=constructor_dict,
                                            custom_params=custom_params,
                                            data=data,
                                            files=files,
                                            remove_filefields=remove_filefields,
                                            remove_datafields=remove_datafields)

            return form

  .. code-block:: python
   
     from django_form_builder.models import SavedFormContent
     
     ...

     # the class used in 'Step 2'
     class MyModelClass(SavedFormContent):
	
	 ...

         def compiled_form(self, files=None, remove_filefields=True):
             """
             Returns the builded and filled form
             Integrates django_form_builder.models.SavedFormContent.compiled_form
	     SavedFormContent.compiled_form uses DynamicFieldMap.get_form() filled
             """
             # set get_form() source class (step 1)
             form_source = self.my_entity
             # set data source class (inherited from 'SavedFormContent')
             data_source = self.modulo_compilato

             form = SavedFormContent.compiled_form(data_source=data_source,
                                                   files=files,
                                                   remove_filefields=remove_filefields,
                                                   form_source=form_source,
                                                   **other_extra_params)

             return form
