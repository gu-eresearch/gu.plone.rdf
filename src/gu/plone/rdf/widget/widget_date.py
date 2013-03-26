from collective.z3cform.datetimewidget import DateWidget as BaseDateWidget
import zope.component
import zope.interface
import zope.schema.interfaces
import z3c.form.interfaces
import z3c.form.widget


class DateWidget(BaseDateWidget):

    # TODO: try to find a way to set parameters like below in RDF

    show_today_link = True
    show_jquerytools_dateinput = True

    # @property
    # def formatted_value(self):
    #     try:
    #         date_value = date(*map(int, self.value))
    #     except ValueError:
    #         return ''
    #     formatter = self.request.locale.dates.getFormatter("date", "short")
    #     if date_value.year > 1900:
    #         return formatter.format(date_value)
    #     # due to fantastic datetime.strftime we need this hack
    #     # for now ctime is default
    #     return date_value.ctime()


@zope.component.adapter(zope.schema.interfaces.IField,
                        z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def DateFieldWidget(field, request):
    """IFieldWidget factory for DateWidget."""
    return z3c.form.widget.FieldWidget(field, DateWidget(request))
