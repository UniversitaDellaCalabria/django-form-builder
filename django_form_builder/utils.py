import json
import re

from django.conf import settings
from django.utils import timezone
from django.utils.html import strip_tags

from . settings import (ATTACHMENTS_DICT_PREFIX,
                        MANAGEMENT_FORMSET_STRINGS)


ATTACHMENTS_DICT_PREFIX = getattr(settings, 'ATTACHMENTS_DICT_PREFIX',
                                  ATTACHMENTS_DICT_PREFIX)
MANAGEMENT_FORMSET_STRINGS = getattr(settings, 'MANAGEMENT_FORMSET_STRINGS',
                                     MANAGEMENT_FORMSET_STRINGS)


def get_labeled_errors(form):
    d = {}
    for field_name in form.errors:
        field = form.fields[field_name]
        d[field.label] = form.errors[field_name]
    return d


def get_formset_labeled_errors(formset_errors):
    d = {}
    for err in formset_errors:
        for k,v in err.items():
            d[k] = strip_tags(v)
    return d


def _split_choices(choices_string):
    """
    Riceve una stringa e la splitta ogni ';'
    creando una tupla di scelte
    """
    str_split = choices_string.split(';')
    choices = tuple((x, x) for x in str_split)
    return choices


def _split_choices_in_list(choices_string):
    """
    Riceve una stringa e la splitta ogni ';'
    creando una lista di scelte
    """
    str_split = choices_string.split(';')
    return str_split


def _split_choices_in_list_canc(choices_string):
    """
    Riceve una stringa e la splitta ogni '#'
    creando una lista di scelte
    """
    str_split = choices_string.split('#')
    return str_split


def _successivo_ad_oggi(data_da_valutare):
    """
    Ci dice se una data è successiva alla data di oggi
    """
    oggi = timezone.localdate()
    if data_da_valutare:
        return data_da_valutare > oggi


# Unused formset method
def get_formset_dict(data, clean=False):
    """data: dict

    returns for example:
        {'date_data_dyn': '2019-05-10',
         'date_minuti_dyn': '25',
         'date_ore_dyn': '5',
         'formsets': {'form-0': {'ccc': 'dfgdfgdfg',
           'co': 'sono',
           'col1': 'un',
           'data': '2019-04-03'},
          'form-1': {'ccc': '234234',
           'co': 'son44o',
           'col1': 'un333',
           'data': '2016-04-03'}},
         'ticket_description': 'dfgdfg',
         'ticket_subject': 'fgdfg'}
    """
    # crea la lista se nei campi esistono formsets
    _re = '(?P<prefix_type>.*)-(?P<prefix_index>[0-9]+)-(?P<name>.*)'
    fields_to_be_removed = []
    d = data.copy()

    formset_dict = {}

    formset_dict_catalog = {}
    for i in d:
        r =  re.match(_re, i)
        if not r: continue
        r = r.groupdict()
        formset_name = '{}-{}'.format(r['prefix_type'],
                                      r['prefix_index'])
        if not formset_dict.get(formset_name):
            formset_dict[formset_name] = {}
        formset_dict[formset_name][r['name']] = d[i]
        fields_to_be_removed.append(i)

    # clean up
    if clean:
        for i in fields_to_be_removed:
            d.pop(i)

    d['formsets'] = formset_dict
    return d


def get_formset_list(data):
    """
    return a list like
    [{'form-0-ccc': 'dfgdfgdfg',
      'form-0-co': 'sono',
      'form-0-col1': 'un',
      'form-0-data': '2019-04-03'},
     {'form-1-ccc': '234234',
      'form-1-co': 'son44o',
      'form-1-col1': 'un333',
      'form-1-data': '2016-04-03'}]
    """
    d = get_formset_dict(data, clean=True)
    l = []
    for i in d.get('formsets'):
        formd = dict()
        for e in d['formsets'][i]:
            k = e #'{}-{}'.format(i,e)
            v = d['formsets'][i][e]
            formd[k] = v
        l.append(formd)
    return l


def get_as_dict(compiled_module_json={},
                allegati=True, formset_management=True):
    """
    torna il dizionario con gli allegati raggruppati in 'allegati'
    """
    # d = json.loads(self.modulo_compilato)
    if compiled_module_json.get(ATTACHMENTS_DICT_PREFIX):
        if not allegati: del compiled_module_json[ATTACHMENTS_DICT_PREFIX]

    to_be_removed = []
    # Corregge i campi inseriti con spazi prima e dopo
    for k,v in compiled_module_json.items():
        # Se non vogliamo che si porti dietro
        # i field input del management del formset (vedi parametri)
        # crea una lista di to_be_removed
        if not formset_management:
            # Nel settings definiamo le parole chiave
            # per identificare i field di management
            for word in MANAGEMENT_FORMSET_STRINGS:
                if word in k:
                    to_be_removed.append(k)
                    break

        if isinstance(compiled_module_json[k],str):
            compiled_module_json[k] = compiled_module_json[k].strip()

    # Se 'formset_management=False', elimina dal dict i to_be_removed
    if not formset_management:
        for r in to_be_removed:
            del compiled_module_json[r]

    return compiled_module_json

def get_allegati_dict(compiled_module, pure_text=False):
    json_dict = compiled_module if pure_text else json.loads(compiled_module.modulo_compilato)
    allegati_dict = get_as_dict(json_dict).get(ATTACHMENTS_DICT_PREFIX)
    if allegati_dict:
        return allegati_dict
    else:
        return {}

def get_allegati(compiled_module):
    """
    torna un lista di file path contenenti gli allegati su filesystem
    """
    allegati = get_allegati_dict(compiled_module)
    if allegati:
        return allegati.items()
    else:
        return []

def get_as_dict_with_allegati(compiled_module, pure_text=False):
    """
    torna il dizionario senza la chiave ATTACHMENTS_DICT_PREFIX
    per gli allegati
    """
    json_dict = compiled_module if pure_text else json.loads(compiled_module.modulo_compilato)
    d = get_as_dict(json_dict)

    # ricostruisco la struttura con gli allegati
    allegati = d.get(ATTACHMENTS_DICT_PREFIX)
    if allegati:
        del d[ATTACHMENTS_DICT_PREFIX]
        d.update(allegati)
    return d

def set_as_dict(obj, modulo_compilato_dict, fields_to_pop=[], indent=False):
    for field in fields_to_pop:
        modulo_compilato_dict.pop(field)
    obj.modulo_compilato = json.dumps(modulo_compilato_dict) \
                           if not indent \
                           else json.dumps(modulo_compilato_dict, indent=2)
    obj.save()

def get_POST_as_json(request, fields_to_pop=[], indent=False):
    data = {}
    for k in request.POST:
        value_list = request.POST.getlist(k)
        if len(value_list) > 1:
            data[k] = value_list
        else:
            data[k] = request.POST[k]
    # data = {k:v for k,v in request.POST.items()}
    for field_name in fields_to_pop:
        if field_name in data:
            data.pop(field_name)
    if "csrfmiddlewaretoken" in data: data.pop("csrfmiddlewaretoken")
    json_data = json.dumps(data) if not indent else json.dumps(data, indent=2)
    return json_data
