from gu.repository.content.interfaces import IRepositoryMetadata
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from gu.z3cform.rdf.interfaces import IORDF
from gu.plone.rdf.interfaces import IRDFSettings
from plone.registry.interfaces import IRegistry
from rdflib import Graph, URIRef
import logging

LOG = logging.getLogger(__name__)


def RepositoryMetadataAdapter(context):
    # ... use uuid to generate URIs.
    # users may give additional URIs / identifiers to be stored as dc:identifier subproperties. (makes them queryable)
    
    #1. determine subject uri for context
    # FIXME: use property, attribute, context absolute url
    uuid = IUUID(context)
    #url = base_uri + /@@redirect-to-uuid/<uuid>
    #uri = context.subjecturi

    registry = getUtility(IRegistry)
    settings = registry.forInterface(IRDFSettings, check=False)

    contenturi = "%s%s" % (settings.base_uri, uuid)

    handler = getUtility(IORDF).getHandler()
    try:
        graph = handler.get(contenturi)
    except Exception as e:
        LOG.error('could not retrieve graph for %s, %s', contenturi, e)
        graph = Graph(identifier=URIRef(contenturi))
    else:
        LOG.info('retrieved %d triples for %s', len(graph), graph.identifier)

    return graph
