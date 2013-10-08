from zope.interface import implementsOnly, implementer
from zope.component import adapter
from z3c.form.interfaces import IFieldWidget, NO_VALUE
from z3c.form.browser.widget import HTMLFormElement
from z3c.form.browser.text import TextWidget
from z3c.form.widget import Widget, FieldWidget
from gu.plone.rdf.widget.widget_date import DateWidget
from gu.plone.rdf.interfaces import IDateRangeWidget
from gu.z3cform.rdf.interfaces import IRDFDateRangeField
from plone.app.z3cform.interfaces import IPloneFormLayer


class DateRangeWidget(HTMLFormElement, Widget):
    """
    Date Range Widget

    allows to enter a start and end date

    """

    implementsOnly(IDateRangeWidget)

    value = {'start': ('', '', ''),
             'end': ('', '', ''),
             'starttext': '',
             'endtext': ''}

    def __init__(self, request):
        super(DateRangeWidget, self).__init__(request)
        self.widgets = {'start': DateWidget(request),
                        'starttext': TextWidget(request),
                        'end': DateWidget(request),
                        'endtext':  TextWidget(request)}

        # name, label, mode, required, error, value, template, layout, ignoreRequest, ignoreRequiredOnValidation, setErrors, showDefault
        # context, ignoreContext, form, field
        #self.name = ????
        #
        #form sets:
        # name, id, context, form, (IFormAware), ignoreContext, ignoreRequest, showDefault, mode -> update()
        #
    def updateWidgets(self):
        self.widgets['start'].name = self.name + '.start'
        self.widgets['starttext'].name = self.name + '.starttext'
        self.widgets['end'].name = self.name + '.end'
        self.widgets['endtext'].name = self.name + '.endtext'
        self.widgets['start'].id = self.id + '-start'
        self.widgets['starttext'].id = self.id + '-starttext'
        self.widgets['end'].id = self.id + '-end'
        self.widgets['endtext'].id = self.id + '-endtext'
        self.widgets['start'].label = u'Start'
        self.widgets['starttext'].label = u'Start text'
        self.widgets['end'].label = u'End'
        self.widgets['endtext'].label = u'End text'
        self.widgets['start'].mode = self.widgets['end'].mode = self.mode
        self.widgets['starttext'].mode = self.widgets['endtext'].mode = self.mode
        self.widgets['start'].ignoreRequest = self.widgets['end'].ignoreRequest = self.ignoreRequest
        self.widgets['starttext'].ignoreRequest = self.widgets['endtext'].ignoreRequest = self.ignoreRequest
        self.widgets['start'].ignoreContext = self.widgets['end'].ignoreContext = self.ignoreContext
        self.widgets['starttext'].ignoreContext = self.widgets['endtext'].ignoreContext = self.ignoreContext
        self.widgets['start'].form = self.widgets['end'].form = self
        self.widgets['starttext'].form = self.widgets['endtext'].form = self
        self.widgets['start'].context = self.widgets['end'].context = self.context
        self.widgets['starttext'].context = self.widgets['endtext'].context = self.context

    def update(self):
        self.updateWidgets()
        #self.widgets['start'].update()
        #self.widgets['end'].update()
        super(DateRangeWidget, self).update()
        if self.value is not None and self.value != NO_VALUE:
            self.widgets['start'].value = self.value['start']
            self.widgets['starttext'].value = self.value['starttext']
            self.widgets['end'].value = self.value['end']
            self.widgets['endtext'].value = self.value['endtext']

    def extract(self):
        start = self.widgets['start'].extract()
        starttext = self.widgets['starttext'].extract()
        end = self.widgets['end'].extract()
        endtext = self.widgets['endtext'].extract()
        if (start == NO_VALUE and end == NO_VALUE and
            starttext == NO_VALUE and endtext == NO_VALUE):
            return NO_VALUE
        return {'start': start,
                'starttext': starttext,
                'end': end,
                'endtext': endtext}


@adapter(IRDFDateRangeField, IPloneFormLayer)
@implementer(IFieldWidget)
def DateRangeFieldWidget(field, request):
    """IFieldWidget factory for DateWidget."""
    return FieldWidget(field, DateRangeWidget(request))
