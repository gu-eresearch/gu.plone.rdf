from z3c.form.interfaces import IWidget
from zope.interface import Interface


class IRDFContentTransform(Interface):
    """
    A component implementing this interface can map between content objects
    and rdf graph instances.
    """

    def tordf(content, graph):
        """
        add tew triples to graph based on given content
        """


class IDateWidget(IWidget):
    """ Date widget. """


class IDateRangeWidget(IWidget):
    """ Date range widget. """


class IDiscoverFacetWidget(IWidget):
    """ Used to render facet search links. """
