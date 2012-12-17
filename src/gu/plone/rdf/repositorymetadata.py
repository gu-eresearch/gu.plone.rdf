from gu.repository.content.interfaces import IRepositoryMetadata
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from gu.z3cform.rdf.interfaces import IORDF

import logging

LOG = logging.getLogger(__name__)


def RepositoryMetadataAdapter(context):
    #1. determine subject uri for context
    # FIXME: use property, attribute, context absolute url
    uuid = IUUID(context)
    #url = portal.url + /@@redirect-to-uuid/<uuid>
    #uri = context.subjecturi

    portal_url = getToolByName(context, "portal_url")
    #portal = portal_url.getPortalObject()
    contenturi = "%s/%s" % (portal_url(), uuid)

    handler = getUtility(IORDF).getHandler()
    graph = handler.get(contenturi)

    LOG.info('retrieved %d triples for %s', len(graph), graph.identifier)

    return graph

    
