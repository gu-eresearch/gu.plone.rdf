from plone.uuid.interfaces import IUUID
from zope.component import getUtility, queryUtility
from gu.z3cform.rdf.interfaces import IORDF
from ordf.graph import Graph
import logging
from Acquisition import aq_base
from App.config import getConfiguration


LOG = logging.getLogger(__name__)


def RepositoryMetadataAdapter(context):
    # ... use uuid to generate URIs.
    # users may give additional URIs / identifiers to be stored as dc:identifier subproperties. (makes them queryable)
    contenturi = getContentUri(context)
    graph = None
    try:
        handler = getUtility(IORDF).getHandler()
        graph = handler.get(contenturi)
    except Exception as e:
        LOG.error('could not retrieve graph for %s, %s', contenturi, e)
    if graph is None:
        #LOG.info("generate empty graph for %s", contenturi)
        graph = Graph(identifier=contenturi)
    else:
        #LOG.info('retrieved %d triples for %s', len(graph), graph.identifier)
        pass

    return graph


def getContentUri(context):
    #1. determine subject uri for context
    # FIXME: use property, attribute, context absolute url

    context = aq_base(context)
    uuid = IUUID(context, None)
    if uuid is None:
        # we probably deal with a new contet object that does not have an uuid yet
        # let's generate one
        from plone.uuid.interfaces import IMutableUUID, IUUIDGenerator
        generator = queryUtility(IUUIDGenerator)
        if generator is None:
            return  # TODO: raise error
        uuid = generator()
        if not uuid:
            return  # TODO: raise error
        IMutableUUID(context).set(uuid)

    #url = base_uri + /@@redirect-to-uuid/<uuid>
    #uri = context.subjecturi

    settings = getConfiguration().product_config.get('gu.plone.rdf', dict())

    contenturi = "%s%s" % (settings.get('baseuri'), uuid)
    return contenturi
