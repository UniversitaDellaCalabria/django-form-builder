import logging

from django.test import TestCase

from django_form_builder import dynamic_fields
from django_form_builder.forms import BaseDynamicForm
from django_form_builder.models import *
from django_form_builder.utils import (_split_choices_in_list,
                                       _split_choices_in_list_canc,
                                       get_formset_dict,
                                       get_formset_list,
                                       get_formset_labeled_errors,
                                       get_labeled_errors)
from django_form_builder.widgets import FormsetdWidget

from . base import BaseTest


logger = logging.getLogger('my_logger')

class TestFormsets(BaseTest):

    def test_formset(self):
        """
        Build a formset passing valid example data
        """
        choices_string = "col1({'type':'CustomSelectBoxField', 'choices':'v1;v2;v3'})#"\
                         "co({'type':'BaseDateField'})#"\
                         "ccc"
        prefix = "prefix"
        data = {
            '{}-TOTAL_FORMS'.format(prefix): '1',
            '{}-INITIAL_FORMS'.format(prefix): '0',
            '{}-MAX_NUM_FORMS'.format(prefix): '',
            '{}-0-col1'.format(prefix): 'v1',
            '{}-0-co'.format(prefix): '1904-06-16',
            '{}-0-ccc'.format(prefix): 'Plain text',
        }

        choices = _split_choices_in_list_canc(choices_string)
        formset = dynamic_fields.build_formset(choices=choices,
                                               required=True,
                                               prefix=prefix,
                                               data=data)
        logger.info("Test form with formset")
        assert formset.is_valid()

    def test_formset_invalid(self):
        """
        Build a formset passing invalid example data
        """
        choices_string = "col1({'type':'CustomSelectBoxField', 'choices':'v1;v2;v3'})#"\
                         "co({'type':'BaseDateField'})#"\
                         "ccc"
        prefix = "prefix"
        data = {
            '{}-TOTAL_FORMS'.format(prefix): '1',
            '{}-INITIAL_FORMS'.format(prefix): '0',
            '{}-MAX_NUM_FORMS'.format(prefix): '',
            '{}-0-col1'.format(prefix): 'v1',
            '{}-0-co'.format(prefix): '1904-106-16',
            '{}-0-ccc'.format(prefix): 'Plain text',
        }

        choices = _split_choices_in_list_canc(choices_string)
        formset = dynamic_fields.build_formset(choices=choices,
                                               required=True,
                                               prefix=prefix,
                                               data=data)
        logger.info("Test form with formset (invalid)")
        logger.info(get_formset_labeled_errors(formset.errors))
        self.assertFalse(formset.is_valid())

    def test_split_choices_in_list(self):
        """
        Test splitting choices string
        """
        choices = 'v1;v2;v3'
        logger.info("Test _split_choices_in_list()")
        assert _split_choices_in_list(choices)

    def test_formset_list(self):
        """
        Test get_formset_list() method
        """
        prefix = "prefix"
        data = {
            '{}-TOTAL_FORMS'.format(prefix): '1',
            '{}-INITIAL_FORMS'.format(prefix): '0',
            '{}-MAX_NUM_FORMS'.format(prefix): '',
            '{}-0-col1'.format(prefix): 'v1',
            '{}-0-co'.format(prefix): '1904-106-16',
            '{}-0-ccc'.format(prefix): 'Plain text',
        }
        logger.info("Test get_formset_list()")
        assert get_formset_list(data)

    def test_formset_widget(self):
        """
        Test FormsetdWidget
        """
        choices_string = "col1({'type':'CustomSelectBoxField', 'choices':'v1;v2;v3'})#"\
                         "co({'type':'BaseDateField'})#"\
                         "ccc"
        prefix = "prefix"
        data = {
            '{}-TOTAL_FORMS'.format(prefix): '1',
            '{}-INITIAL_FORMS'.format(prefix): '0',
            '{}-MAX_NUM_FORMS'.format(prefix): '',
            '{}-0-col1'.format(prefix): 'v1',
            '{}-0-co'.format(prefix): '1904-106-16',
            '{}-0-ccc'.format(prefix): 'Plain text',
        }

        formset_field = self.create_field('CustomComplexTableField')[0]
        choices = _split_choices_in_list_canc(choices_string)
        formset_field.widget = FormsetdWidget(field_required=True,
                                              prefix=prefix,
                                              data=data,
                                              choices=choices)

        logger.info("Test form with formset widget (FormsetdWidget)")
        logger.info(get_formset_labeled_errors(formset_field.widget.formset.errors))
        assert formset_field.widget.get_js_template()
        assert formset_field.widget.make_readonly()
