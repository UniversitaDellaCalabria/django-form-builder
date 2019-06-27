.. django-form-builder documentation master file, created by
   sphinx-quickstart on Tue Jul  2 08:50:49 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Use single fields in your form
==============================

| You can simply take single fields from this app and use them in you own form.
| Just in your project include

.. code-block:: python

   from django_form_builder import dynamic_fields

and use every field as a normal form field

.. code-block:: python

   my_field = dynamic_fields.DynamicFieldClassName(params)


Every field has (or inherit) a ``raise_error()`` method that can be overrided to implement cleaning features and 
validation functions.
