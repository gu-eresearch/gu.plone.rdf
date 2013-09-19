# maybe use own exceptions here?
from collective.z3cform.datetimewidget.interfaces import DateValidationError
from gu.z3cform.rdf.converter import BaseDataConverter
from rdflib import Literal
from ordf.namespace import XSD, DC
from datetime import date
import zope.interface
import zope.component
from isodate import parse_date


class RDFDateDataConverter(BaseDataConverter):
    '''
    converts between literal date field and collective.z3cform.datetimewidget .

    # TODO: this converter can be optimized. it only needs to reformat the 3
            supplied values.
    '''

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return ('', '', '')
        value = value.toPython()
        return (value.year, value.month, value.day)

    def toFieldValue(self, value):
        for val in value:
            if not val:
                return self.field.missing_value

        try:
            value = map(int, value)
        except ValueError:
            raise DateValidationError
        try:
            value = date(*value)
        except ValueError:
            raise DateValidationError
        return Literal(value, datatype=XSD['date'])


class RDFDateRangeConverter(BaseDataConverter):

    def toWidgetValue(self, value):
        ret = {'start': ('', '', ''),
               'end': ('', '', '')}
        if value is self.field.missing_value:
            return ret
        # TODO: check literal datatype?
        period = Period(value)
        # TODO: check encoding scheme in case of period
        if period.start:
            start = parse_date(period.start)
            ret['start'] = (start.year, start.month, start.day)
        if period.end:
            end = parse_date(period.end)
            ret['end'] = (end.year, end.month, end.day)
        return ret

    def toFieldValue(self, value):
        for val in value['start']:
            if not val:
                return self.field.missing_value
        for val in value['end']:
            if not val:
                return self.field.missing_value

        try:
            value = {'start': map(int, value['start']),
                     'end': map(int, value['end'])}
        except ValueError:
            raise DateValidationError
        try:
            value = {'start': date(*value['start']),
                     'end': date(*value['end'])}
        except ValueError:
            raise DateValidationError
        # FIXEM: generate correct dcmi period here
        litval = Period('')
        litval.start = value['start'].isoformat()
        litval.end = value['end'].isoformat()
        litval.scheme = 'W3C-DTF'
        return Literal(unicode(litval), datatype=DC['Period'])




import re


class Period(object):
    """
    Parse DCMI period strings and provide values as attributes.

    Format set period values as valid DCMI period.

    FIXME: currently uses date strings as is and does not try to interpret
           them.
           the same for formatting. date's have to be given as properly
           formatted strings.
    """

    start = end = scheme = name = None

    def __init__(self, str):
        '''
        TODO: assumes str is unicode
        '''
        sm = re.search(r'start=(.*?);', str)
        if sm:
            self.start = sm.group(1)
        sm = re.search(r'scheme=(.*?);', str)
        if sm:
            self.scheme = sm.group(1)
        sm = re.search(r'end=(.*?);', str)
        if sm:
            self.end = sm.group(1)
        sm = re.search(r'name=(.*?);', str)
        if sm:
            self.name = sm.group(1)

    def __unicode__(self):
        parts = []
        if self.start:
            parts.append("start=%s;" % self.start)
        if self.end:
            parts.append("end=%s;" % self.end)
        if self.name:
            parts.append("name=%s;" % self.name)
        if self.scheme:
            parts.append("scheme=%s;" % self.scheme)
        return u' '.join(parts)
