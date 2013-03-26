from zope.interface import implementsOnly, implementer
from zope.component import adapter
from z3c.form.interfaces import IFieldWidget, NO_VALUE
from z3c.form.browser.widget import HTMLFormElement
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
             'end': ('', '', '')}

    def __init__(self, request):
        super(DateRangeWidget, self).__init__(request)
        self.widgets = {'start': DateWidget(request),
                        'end': DateWidget(request)}
        # name, label, mode, required, error, value, template, layout, ignoreRequest, ignoreRequiredOnValidation, setErrors, showDefault
        # context, ignoreContext, form, field
        #self.name = ????
        #
        #form sets:
        # name, id, context, form, (IFormAware), ignoreContext, ignoreRequest, showDefault, mode -> update()
        #
    def updateWidgets(self):
        self.widgets['start'].name = self.name + '.start'
        self.widgets['end'].name = self.name + '.end'
        self.widgets['start'].id = self.id + '-start'
        self.widgets['end'].id = self.id + '-end'
        self.widgets['start'].label = u'Start'
        self.widgets['end'].label = u'End'
        self.widgets['start'].mode = self.widgets['end'].mode = self.mode
        self.widgets['start'].ignoreRequest = self.widgets['end'].ignoreRequest = self.ignoreRequest
        self.widgets['start'].ignoreContext = self.widgets['end'].ignoreContext = self.ignoreContext
        self.widgets['start'].form = self.widgets['end'].form = self
        self.widgets['start'].context = self.widgets['end'].context = self.context
        

    def update(self):
        self.updateWidgets()
        #self.widgets['start'].update()
        #self.widgets['end'].update()
        super(DateRangeWidget, self).update()
        if self.value is not None and self.value != NO_VALUE:
            self.widgets['start'].value = self.value['start']
            self.widgets['end'].value = self.value['end']

    def extract(self):
        start = self.widgets['start'].extract()
        end = self.widgets['end'].extract()
        if (start == NO_VALUE or end == NO_VALUE):
            return NO_VALUE
        return {'start': start,
                'end': end}


@adapter(IRDFDateRangeField, IPloneFormLayer)
@implementer(IFieldWidget)
def DateRangeFieldWidget(field, request):
    """IFieldWidget factory for DateWidget."""
    return FieldWidget(field, DateRangeWidget(request))
