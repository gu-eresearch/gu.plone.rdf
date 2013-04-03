import zope.schema.interfaces
import z3c.form.interfaces
import z3c.form.widget
from z3c.form.browser.orderedselect import OrderedSelectWidget
from zope.interface import implements
from gu.plone.rdf.interfaces import IDiscoverFacetWidget


# TODO: this widget should probably go inte terranova site package
class DiscoverFacetWidget(OrderedSelectWidget):
    """
    used as display widget to generate links to search page.
    """

    implements(IDiscoverFacetWidget)


@zope.component.adapter(zope.schema.interfaces.IField,
                        z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def DiscoverFacetFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, DiscoverFacetWidget(request))
