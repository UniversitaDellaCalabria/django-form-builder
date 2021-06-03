import logging
import os

from django_form_builder import dynamic_fields
from django_form_builder.settings import ATTACHMENTS_DICT_PREFIX, CLASSIFICATION_LIST
from django_form_builder.templatetags.django_form_builder_tags import *
from django_form_builder.utils import format_field_name, get_labeled_errors

from . base import BaseTest

logger = logging.getLogger(__name__)


class TestInvalidFields(BaseTest):

    def test_integer_valid(self):
        """
        Test valid value in PositiveIntegerField
        """
        form = self.single_field_form('PositiveIntegerField', 44)
        logger.info("Test valid PositiveIntegerField")
        assert form.is_valid()

    def test_integer_invalid(self):
        """
        Test invalid value in PositiveIntegerField
        Decimal value instead of Integer
        """
        form = self.single_field_form('PositiveIntegerField', 16e50)
        logger.info("Test invalid PositiveIntegerField")
        logger.info(get_labeled_errors(form))
        self.assertFalse(form.is_valid())

    def test_float_valid(self):
        """
        Test valid value in PositiveFloatField
        """
        form = self.single_field_form('PositiveFloatField', 4)
        logger.info("Test valid PositiveFloatField")
        assert form.is_valid()

    def test_float_invalid(self):
        """
        Test invalid value in PositiveFloatField
        """
        form = self.single_field_form('PositiveFloatField', 16e50)
        logger.info("Test invalid PositiveFloatField")
        logger.info(get_labeled_errors(form))
        self.assertFalse(form.is_valid())

    def test_float_invalid_2(self):
        """
        Test invalid value in PositiveFloatField
        """
        form = self.single_field_form('PositiveFloatField', 4.3333)
        logger.info("Test invalid PositiveFloatField")
        logger.info(get_labeled_errors(form))
        self.assertFalse(form.is_valid())

    def test_date_startend_valid(self):
        """
        Test valid values in DateStartEndComplexField
        """
        data = {'test_field_data_inizio_dyn': '12/01/2020',
                'test_field_data_fine_dyn': '12/03/2020'}
        form = self.complex_field_form('DateStartEndComplexField', data)
        logger.info("Test valid DateStartEndComplexField")
        assert form.is_valid()

    def test_date_startend_invalid(self):
        """
        Test invalid values in DateStartEndComplexField
        Start date > End date
        """
        data = {'test_field_data_inizio_dyn': '12/01/2022',
                'test_field_data_fine_dyn': '12/03/2020'}
        form = self.complex_field_form('DateStartEndComplexField', data)
        logger.info("Test valid DateStartEndComplexField")
        self.assertFalse(form.is_valid())

    def test_ip_valid(self):
        """
        Test invalid values in CustomIPField
        """
        form = self.single_field_form('CustomIPField', '192.168.0.1')
        logger.info("Test valid CustomIPField")
        assert form.is_valid()


    def test_ip_invalid(self):
        """
        Test invalid values in CustomIPField
        """
        form = self.single_field_form('CustomIPField', '192.168000001')
        logger.info("Test invalid CustomIPField")
        self.assertFalse(form.is_valid())

    def test_mac_valid(self):
        """
        Test invalid values in CustomIPField
        """
        form = self.single_field_form('CustomMACField', '98:54:1b:07:15:ed')
        logger.info("Test valid CustomMACField")
        assert form.is_valid()


    def test_mac_invalid(self):
        """
        Test invalid values in CustomIPField
        """
        form = self.single_field_form('CustomMACField', '98.541b:07:15:ed')
        logger.info("Test invalid CustomMACField")
        self.assertFalse(form.is_valid())


    def test_datetimefield_valid(self):
        """
        Test valid values in BaseDateTimeField
        """
        super_label = 'Field label'
        field_id = format_field_name(super_label)
        data = {'{}_data_dyn'.format(field_id): '11/01/2020',
                '{}_ore_dyn'.format(field_id): '12',
                '{}_minuti_dyn'.format(field_id): '12'}
        form = self.complex_field_form('BaseDateTimeField',
                                        data,
                                        super_label)
        logger.info("Test valid BaseDateTimeField")
        assert form.is_valid()

    def test_protocollo_invalid(self):
        """
        Test invalid values in ProtocolloField
        data_protocollo > current date
        """
        data = {'test_field_tipo_numerazione_dyn': CLASSIFICATION_LIST[0][0],
                'test_field_numero_protocollo_delibera_decreto_dyn': '12312 text',
                'test_field_data_protocollo_delibera_decreto_dyn': '12/03/2010'}
        form = self.complex_field_form('ProtocolloField', data)
        logger.info("Test valid ProtocolloField")
        assert form.is_valid()

    def test_filefield(self):
        """
        Test valid value in PositiveIntegerField
        """
        file_test = self.create_fake_file()
        form = self.single_field_form('CustomFileField',
                                      file_value=file_test)
        logger.info("Test valid CustomFileField")
        assert form.is_valid()

    # def test_signed_pdf(self):
        # """
        # Test valid value in PositiveIntegerField
        # """
        # name = 'test_signed.pdf'
        # file_obj = self.get_file(name)
        # form = self.single_field_form('CustomSignedPdfField',
                                      # file_value=file_obj)
        # logger.info("Test valid CustomSignedPdfField")
        # assert form.is_valid()

    # def test_signed_pdf_show_details(self):
        # """
        # Test valid value in PositiveIntegerField
        # """
        # name = 'test_signed.pdf'
        # file_obj = self.get_file(name)
        # field = self.create_field('CustomSignedPdfField')[0]
        # field_id = format_field_name(field.label)
        # initial_fields = {field_id: field}
        # files = {field_id: file_obj}
        # form = self.get_baseform(initial_fields=initial_fields,
                                 # files=files)
        # logger.info("Test valid PDF signed file (sign details)")
        # logger.info(get_attachment_sign_details(form,
                                                # self.get_filepath(),
                                                # field_id,
                                                # name))
        # assert form.is_valid()

    # def test_signed_p7m(self):
        # """
        # Test valid value in PositiveIntegerField
        # """
        # name = 'test_signed.pdf.p7m'
        # file_obj = self.get_file(name, content_type='application/pkcs7-mime')
        # form = self.single_field_form('CustomSignedP7MField', file_value=file_obj)
        # logger.info("Test valid CustomSignedP7MField")
        # assert form.is_valid()
