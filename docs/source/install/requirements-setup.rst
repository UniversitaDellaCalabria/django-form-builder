.. django-form-builder documentation master file, created by
   sphinx-quickstart on Tue Jul  2 08:50:49 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Requirements and Setup
======================

Only ``FileSignatureValidator`` library is required as system dependency, it is needed to verify digitally signed attachments.
See also requirements for python requirements.

.. code-block:: python

   pip install git+https://github.com/peppelinux/FileSignatureValidator.git

In ``INSTALLED_APPS`` include ``django_form_builder`` app.

.. code-block:: python

   INSTALLED_APPS = (
       # other apps
       'django_form_builder',
   )
