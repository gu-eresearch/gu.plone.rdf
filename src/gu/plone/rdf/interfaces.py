from zope import schema
from zope.interface import Interface
from gu.plone.rdf import _

class IORDF(Interface):
    """
    Ann interface for the global ORDF Utility.
    """

    def getHandler(self):
        """ return an ORDF handler """

    def getFresnelGraph(self):
        """ return a pre compiled Fresnel implementation """

    def resetCaches(self):
        """ reset all cached values """


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
        required=True,
        )
