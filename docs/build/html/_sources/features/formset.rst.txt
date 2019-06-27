.. django-form-builder documentation master file, created by
   sphinx-quickstart on Tue Jul  2 08:50:49 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Add/Remove Formset dynamically with javascript
==============================================

Django Form Builder provides a particular type of field, ``CustomComplexTableField``,
that allows user to easily insert `Django Formset <https://docs.djangoproject.com/en/2.2/topics/forms/formsets/>`_ Fields in his form.

The built-in javascript enables form inserting and removing via frontend, simply using the relative buttons!

To build a formset just define the ``CustomComplexTableField`` attribute *valore* setting columuns.
Divide each one using *#* char and, for every column, define the field type with a dictionary, like in the example

.. code-block:: html

   column1({'type':'CustomSelectBoxField', 'choices': 'value1;value2;value3',})#column2({'type':'CustomRadioBoxField', 'choices': 'value1;value2',})#column3#column4({'type':'BaseDateField',})

Column with no params dict generate ``CustomCharField`` by default.

--------------------------------

.. thumbnail:: ../images/formset.png
