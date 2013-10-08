from zope import schema
from z3c.form.interfaces import IWidget
from zope.interface import Interface
from gu.plone.rdf import _


class IRDFSettings(Interface):
    """
    Describe settings interface for ORDF-Setup
    """
    ordf_configuration = schema.Text(
        title=_(u"ORDF configuration"),
        description=_(u"See ORDF for details. This text field is parsed as "
                      u"standard INI file."),
        required=True)

    fresnel_graph_uri = schema.URI(
        title=_(u"Fresnel Graph URI"),
        required=True
        )

    base_uri = schema.URI(
        title=_(u"Base URI"),
        description=_(u"URI preix used for locally generated content. "
                      u"It should end with # or /"),
        required=True)


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
