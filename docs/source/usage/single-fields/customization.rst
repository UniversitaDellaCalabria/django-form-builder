.. django-form-builder documentation master file, created by
   sphinx-quickstart on Tue Jul  2 08:50:49 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Create your own fields
======================

If you need to define your own fields inheriting an existing one, 
you can fastly create them by importing ``dynamic_fields``

.. code-block:: python

   from django_form_builder import dynamic_fields

make an inheritance declaration

.. code-block:: python

   class MyCustomField(dynamic_fields.DynamicFieldClassName):
        # e.g. MyCustomField(BaseCustomField)
	...

and override ``get_fields()``, ``define_value()`` and ``raise_error()`` according to your needs.
