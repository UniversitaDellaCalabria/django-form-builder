import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from django_form_builder import dynamic_fields
from django_form_builder.forms import BaseDynamicForm
from django_form_builder.models import *


class BaseTest(TestCase):

    def get_baseform(self, initial_fields, data={}, files={}):
        """
        Build a form from BaseDynamicForm
        """
        form = BaseDynamicForm.get_form(initial_fields=initial_fields,
                                        data=data,
                                        files=files)
        return form

    def create_field(self, field_class, field_label='', required=True):
        """
        Create a field using class name
        """
        label = field_label or 'test field'
        field_data = {'required': required,
                      'label': label}
        field = getattr(dynamic_fields, field_class)(**field_data)
        if field.is_complex:
            return field.get_fields()
        return [field,]

    def create_fake_file(self, name="test", ext="pdf",
                         content_type="application/pdf"):
        """
        Create a fake file to simulate upload
        """
        return SimpleUploadedFile("{}.{}".format(name, ext),
                                  b"file_content",
                                  content_type=content_type)

    def get_file(self, real_file_name,
                 name="test", ext="pdf",
                 content_type="application/pdf"):
        """
        Simulate upload using a real file
        """
        if not real_file_name: return None
        module_dir = "{}/{}".format(os.path.dirname(__file__), "files")
        file_path = os.path.join(module_dir, real_file_name)
        file_obj = open(file_path, 'rb')
        return SimpleUploadedFile("{}.{}".format(name, ext),
                                  file_obj.read(),
                                  content_type=content_type)

    def single_field_form(self, field_class,
                          data_value='{}', file_value='{}',
                          required=True):
        """
        Build a form with a single field
        """
        field = self.create_field(field_class=field_class,
                                  required=required)[0]
        field_id = dynamic_fields.format_field_name(field.label)
        initial_fields = {field_id: field}
        data = {field_id: data_value}
        files = {field_id: file_value}
        form = self.get_baseform(initial_fields=initial_fields,
                                 data=data,
                                 files=files)
        return form

    def complex_field_form(self, field_class, data, field_label=''):
        """
        Build a form with a single complex field
        """
        fields = self.create_field(field_class, field_label)
        initial_fields = {}
        for field in fields:
            initial_fields[field.name] = field
        data = data
        form = self.get_baseform(initial_fields=initial_fields,
                                 data=data)
        return form

    def get_filepath(self):
        return "{}/{}".format(os.path.dirname(__file__), "files")

    def get_full_filepath(self, filename):
        module_dir = "{}/{}".format(os.path.dirname(__file__), "files")
        return os.path.join(module_dir, filename)
