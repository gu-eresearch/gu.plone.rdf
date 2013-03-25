# maybe use own exceptions here?
from collective.z3cform.datetimewidget.interfaces import DateValidationError
from gu.z3cform.rdf.converter import BaseDataConverter, RDFObjectSubForm
from rdflib import Literal
from ordf.namespace import XSD
from datetime import date
from plone.app.z3cform.interfaces import IPloneFormLayer
import zope.interface
import zope.component
from z3c.form.interfaces import ISubformFactory
from gu.z3cform.rdf.interfaces import IRDFObjectField
from gu.z3cform.rdf.widgets.interfaces import IRDFObjectWidget


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


class SubformAdapter(object):
    """Most basic-default subform factory adapter"""

    zope.interface.implements(ISubformFactory)
    zope.component.adapts(zope.interface.Interface,  # widget value
                          IPloneFormLayer,  # IFormLayer,    #request
                          zope.interface.Interface,  # widget context
                          zope.interface.Interface,  # form
                          IRDFObjectWidget,  # widget
                          IRDFObjectField,  # field
                          zope.interface.Interface)  # field.schema
    factory = RDFObjectSubForm

    def __init__(self, context, request, widgetContext, form,
                 widget, field, schema):
        self.context = context  # context for this form
        self.request = request  # request
        self.widgetContext = widgetContext  # main context
        self.form = form  # main form
        self.widget = widget  # the widget tha manages this form
        self.field = field  # the field to attach the whole thing to
        self.schema = schema  # we don't use this

    def __call__(self):
        obj = self.factory(self.context, self.request, self.widget)
        return obj
