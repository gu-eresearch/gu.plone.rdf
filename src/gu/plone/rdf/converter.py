# maybe use own exceptions here?
from collective.z3cform.datetimewidget.interfaces import DateValidationError
from gu.z3cform.rdf.converter import BaseDataConverter
from gu.z3cform.rdf.utils import Period
from rdflib import Literal
from ordf.namespace import XSD, DC
import zope.interface
import zope.component
from zope.schema import ValidationError
import re

splitdate = re.compile(r'^(\d\d\d\d)(-(\d\d))?(-(\d\d))?$').match


class DateRangeValidationError(ValidationError):
    __doc__ = u'Please supply either date values or textual description.'


class RDFDateDataConverter(BaseDataConverter):
    '''
    converts between literal date field and collective.z3cform.datetimewidget .

    # TODO: this converter can be optimized. it only needs to reformat the 3
            supplied values.
    '''

    def toWidgetValue(self, value):
        if value is self.field.missing_value:
            return ('', '', '')
        parts = splitdate(value)
        if parts:
            return (parts.group(1), parts.group(3) or '', parts.group(5) or '')
        return ('', '', '')

    def toFieldValue(self, value):
        found_none = False
        for val in value:
            if not val:
                found_none = True
            elif found_none:
                # We had an essential value skippd. e.g. no month, but date was given.
                # TODO: better error message please
                raise ValueError('Skipped wrong element of date values.')
        # TODO: could validate here and throw ValidationError as well
        value = ['{:0>2s}'.format(v) for v in filter(bool, value)]
        if not value:
            return self.field.missing_value
        return Literal(u'-'.join(value), datatype=DC['W3CDTF'])


class RDFDateRangeConverter(BaseDataConverter):

    def toWidgetValue(self, value):
        ret = {'start': ('', '', ''),
               'end': ('', '', ''),
               'starttext': '',
               'endtext': ''}
        if value is self.field.missing_value:
            return ret
        # TODO: check literal datatype?
        period = Period(value)
        # TODO: check encoding scheme in case of period
        if period.scheme in (None, 'W3C-DTF'):
            if period.start:
                start = splitdate(period.start)
                if start:
                    ret['start'] = (start.group(1), start.group(3) or '', start.group(5) or '')
            if period.end:
                end = splitdate(period.end)
                if end:
                    ret['end'] = (end.group(1), end.group(3) or '', end.group(5) or '')
        else:
            if period.start:
                ret['starttext'] = period.start
            if period.end:
                ret['endtext'] = period.end
        return ret

    def _check_date_bits(self, value):
        found_none = False
        for val in value:
            if not val:
                found_none = True
            elif found_none:
                raise ValueError('Skipped wrong element of date values.')

    def toFieldValue(self, value):
        # preference of text or date fields?
        if ((any(value['start']) or any(value['end'])) and
            (value['starttext'] or value['endtext'])):
            raise DateRangeValidationError
        # check above sholud ensure we have either text or date values.
        period = Period('')
        if (value['starttext'] or value['endtext']):
            # text dates
            period.start = value['starttext']
            period.end = value['endtext']
            period.scheme = 'Textual description'
        elif (any(value['start']) or any(value['end'])):
            # date values
            self._check_date_bits(value['start'])
            self._check_date_bits(value['end'])
            startvalue = ['{:0>2s}'.format(v) for v in filter(bool, value['start'])]
            period.start = u'-'.join(startvalue)
            endvalue = ['{:0>2s}'.format(v) for v in filter(bool, value['end'])]
            period.end = u'-'.join(endvalue)
            period.scheme = 'W3C-DTF'
        else:
            return self.field.missing_value
        return Literal(unicode(period), datatype=DC['Period'])
