.. django-form-builder documentation master file, created by
   sphinx-quickstart on Tue Jul  2 08:50:49 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Fields methods and attributes
=============================

| ``BaseCustomField`` is the base class for every custom field.
| This class defines two attributes and trhee foundamental methods that make fields work well.

**Attributes**

- ``is_complex`` (default *False*): if *True*, specifies that the field is composed by more elementar fields (like two DateFields);
- ``is_formset`` (default *False*): if *True*, specifies that the field is a `Django Formset <https://docs.djangoproject.com/en/2.2/topics/forms/formsets/>`_.

**Methods**

- ``def define_value(self, custom_value=None, **kwargs)``: it integrates the field initialization with custom configuration parameters defined by user (e.g. choices of a SelectBox);
- ``get_fields(self)``: if field *is_complex*, it returns a Python list of child fields. Else, it returns ``[self]``;
- ``def raise_error(self, name, cleaned_data, **kwargs):``: it integrates ``clean()`` method to have a customizable behaviour processing ``cleaned_data``.
