from zope.component import adapter
from zope.interface import implementer
#from zope.schema.interfaces import IField
from gu.z3cform.rdf.interfaces import IRDFDateField
from z3c.form.interfaces import IFormLayer, IFieldWidget, NO_VALUE
from z3c.form.widget import Widget, FieldWidget
from z3c.form.browser.widget import HTMLTextInputWidget, addFieldClass
from gu.plone.rdf.interfaces import IDateWidget


@implementer(IDateWidget)
class DateWidget(HTMLTextInputWidget, Widget):

    klass = u'date-widget'
    value = ('', '', '')

    @property
    def year(self):
        year = self.request.get(self.name + '-year', None)
        if year is not None:
            return year
        return self.value[0]

    @property
    def month(self):
        month = self.request.get(self.name + '-month', None)
        if month:
            return month
        return self.value[1]

    @property
    def day(self):
        day = self.request.get(self.name + '-day', None)
        if day is not None:
            return day
        return self.value[2]

    @property
    def hidden_value(self):
        return '/'.join(self.value)

    @property
    def formatted_value(self):
        return '/'.join(self.value)

    def update(self):
        super(DateWidget, self).update()
        addFieldClass(self)

    def extract(self, default=NO_VALUE):
        # get normal input fields
        day = self.request.get(self.name + '-day', default)
        month = self.request.get(self.name + '-month', default)
        year = self.request.get(self.name + '-year', default)

        if not default in (year, month, day):
            return (year, month, day)

        # get a hidden value
        hidden_date = self.request.get(self.name, '')
        hidden_date = hidden_date.split("/")
        if len(hidden_date) == 3:
            return hidden_date
        return default


@adapter(IRDFDateField, IFormLayer)
@implementer(IFieldWidget)
def DateFieldWidget(field, request):
    """IFieldWidget factory for DateWidget."""
    return FieldWidget(field, DateWidget(request))
