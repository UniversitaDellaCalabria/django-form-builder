import logging

from django.test import TestCase

from django_form_builder import dynamic_fields
from django_form_builder.forms import BaseDynamicForm
from django_form_builder.models import *
from django_form_builder.settings import ATTACHMENTS_DICT_PREFIX
from django_form_builder.templatetags.django_form_builder_tags import *
from django_form_builder.utils import (get_allegati_dict,
                                       get_as_dict_with_allegati,
                                       get_labeled_errors)

from . base import BaseTest


logger = logging.getLogger('my_logger')

class DynamicFieldMapFake(object):
    """
    Fake generic object to simulate a DynamicFieldMap
    django_form_builder.models.DynamicFieldMap
    """
    pass

class TestFormsets(BaseTest):

    def _simulateDynamicFieldMapEntity(self,
                                       field_type,
                                       name='',
                                       valore=''):
        """
        Simulate a DynamicFieldMap object init
        Using a generic object and inserting needed variables
        """
        field_map_entity = DynamicFieldMapFake()
        field_map_entity.name = name
        field_map_entity.field_type = field_type
        field_map_entity.is_required = True
        field_map_entity.valore = valore
        field_map_entity.aiuto = "example help test"
        return field_map_entity

    def setUp(self):
        """
        Build some field assigning a value to test it
        """
        self.fields = []
        self.data = {}

        name = 'charfield'
        textfield = self._simulateDynamicFieldMapEntity('CustomCharField',
                                                        name=name)
        self.fields.append(textfield)
        self.data[name] = 'testo'

        name = 'integerfield'
        integerfield = self._simulateDynamicFieldMapEntity('PositiveIntegerField',
                                                           name=name)
        self.fields.append(integerfield)
        self.data[name] = 44

        name = 'radiofield'
        radiofield = self._simulateDynamicFieldMapEntity('CustomRadioBoxField',
                                                         name=name,
                                                         valore='col1;col2;col3')
        self.fields.append(radiofield)
        self.data[name] = 'col1'

        name = 'selectfield'
        selectfield = self._simulateDynamicFieldMapEntity('CustomSelectBoxField',
                                                          name=name,
                                                          valore='col1;col2;col3')
        self.fields.append(selectfield)
        self.data[name] = 'col1'

    def test_getform(self):
        """
        Test init form with build_constructor_dict() and fields list
        """
        constructor_dict = BaseDynamicForm.build_constructor_dict(self.fields)
        form = BaseDynamicForm.get_form(constructor_dict=constructor_dict,
                                        data=self.data)
        logger.info("Test form with dynamic fields (build_constructor_dict())")
        assert form.is_valid()

    def test_compiledform(self):
        """
        Test compiled_form() method
        """
        constructor_dict = BaseDynamicForm.build_constructor_dict(self.fields)
        form = SavedFormContent.compiled_form(data_source=json.dumps(self.data))
        logger.info("Test compiledform()")
        assert form.is_valid()

    def test_compiledform_readonly(self):
        """
        Test compiled_form_readonly() method
        """
        constructor_dict = BaseDynamicForm.build_constructor_dict(self.fields)
        form = BaseDynamicForm.get_form(constructor_dict=constructor_dict,
                                        data=self.data)
        SavedFormContent.compiled_form_readonly(form)
        logger.info("Test test_compiledform_readonly()")
        assert form.is_valid()

    def test_not_compiled_field(self):
        """
        Test valid value in PositiveIntegerField
        """
        form = self.single_field_form('PositiveIntegerField', '',
                                      required=False)
        form.remove_not_compiled_fields()
        logger.info("Test remove not compiled fields")
        assert form.is_valid()

    def test_remove_data_field(self):
        """
        Test valid value in PositiveIntegerField
        """
        form = self.single_field_form('PositiveIntegerField', '',
                                      required=False)
        logger.info("Test remove all data fields")
        assert form.is_valid()
        form.remove_datafields()
        assert not form.fields

    def test_remove_filefield(self):
        """
        Test valid value in PositiveIntegerField
        """
        file_test = self.create_fake_file()
        form = self.single_field_form('CustomFileField',
                                      file_value=file_test)
        logger.info("Test valid CustomFileField")
        assert form.is_valid()
        form.remove_files()
        assert not form.fields

    def test_get_dyn_field_name(self):
        """
        Test get_dyn_field_name() method
        """
        field_type = get_dyn_field_name('CustomFileField')
        logger.info("Test get_dyn_field_name()")
        assert field_type

    def test_get_allegati_dict(self):
        """
        Test get_allegati_dict() method
        """
        data = {'data_inizio_dyn': '12/01/2020',
                'data_fine_dyn': '12/03/2020',
                ATTACHMENTS_DICT_PREFIX: {
                    'test_file': 'test_file_path',
                    }
                }
        attachments = get_allegati_dict(compiled_module=data,
                                        pure_text=True)
        logger.info("Test get_allegati_dict()")
        assert attachments

    def test_get_allegati_dict_false(self):
        """
        Test invalid get_allegati_dict() method
        """
        data = {'data_inizio_dyn': '12/01/2020',
                'data_fine_dyn': '12/03/2020'
                }
        attachments = get_allegati_dict(compiled_module=data,
                                        pure_text=True)
        logger.info("Test empty get_allegati_dict()")
        self.assertFalse(attachments)

    def test_get_as_dict_with_allegati(self):
        """
        Test get_as_dict_with_allegati()
        """
        data = {'data_inizio_dyn': '12/01/2020',
                'data_fine_dyn': '12/03/2020',
                ATTACHMENTS_DICT_PREFIX: {
                    'test_file': 'test_file_path',
                    }
                }
        data = get_as_dict_with_allegati(compiled_module=data,
                                         pure_text=True)
        logger.info("Test empty get_allegati_dict()")
        assert data['test_file']
