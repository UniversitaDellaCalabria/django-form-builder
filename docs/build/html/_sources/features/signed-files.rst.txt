.. django-form-builder documentation master file, created by
   sphinx-quickstart on Tue Jul  2 08:50:49 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Upload P7M and signed PDF files
===============================

Custom fields set provides a base class called ``CustomSignedFileField`` that 
via *FileSignatureValidator* library checks if an upload attachment is digitally signed.

Also, with ``get_cleaned_signature_params()`` method, it returns the sign details

- Signature Validation
- Signing Time
- Signer full Distinguished Name

| P7M file fields are built by ``CustomSignedP7MField(CustomSignedFileField)`` class.
| Signed PDF file fields are built by ``CustomSignedPdfField(CustomSignedFileField)`` class.
