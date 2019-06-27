.. django-form-builder documentation master file, created by
   sphinx-quickstart on Tue Jul  2 08:50:49 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

django-form-builder's documentation
===================================

A Django Framework application to build dynamic forms and define
custom form fields types.

**Github:** https://github.com/UniversitaDellaCalabria/django-form-builder

**Features:**

- Forms definitions via JSON object;
- Save compiled form as JSON objects in model db and get its structure and contents with a simple model method call;
- Override form constructor in order to add static common fields;
- Create input fields using heritable classes, with customizable validation methods;
- Manage Django Formset fields, with form insertion and removal via javascript;
- Manage and verify digitally signed file fields (PDF and P7M) without a certification authority validation (TODO via third-party API).

---------------------------------------

.. toctree::
   :maxdepth: 2
   :caption: Installation

   install/requirements-setup.rst

.. toctree::
   :maxdepth: 2
   :caption: Use single fields in your form

   Description <usage/single-fields/description.rst>
   Methods ad Attributes <usage/single-fields/methods.rst>
   Create your own fields <usage/single-fields/customization.rst>

.. toctree::
   :maxdepth: 2
   :caption: Build dynamic forms

   Description <usage/dynamic-forms/description.rst>
   Add static fields to a form <usage/dynamic-forms/customization.rst>
   Configuration <usage/dynamic-forms/configuration.rst>

.. toctree::
   :maxdepth: 2
   :caption: Special features

   Digitally signed attachments <features/signed-files.rst>
   Formset javascript manager <features/formset.rst>
   
   
