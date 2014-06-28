import logging
from rdflib import Graph
from rdflib.resource import Resource
from zope.component import getUtility
from gu.z3cform.rdf.interfaces import IORDF

LOG = logging.getLogger(__name__)


def graph_for_content(content):
    # ... use uuid to generate URIs.
    # users may give additional URIs / identifiers to be stored as
    # dc:identifier subproperties. (makes them queryable)
    rdftool = getUtility(IORDF)
    contenturi = rdftool.getContentUri(content)
    graph = None
    try:
        graph = rdftool.getHandler().get(contenturi)
    except Exception as e:
        LOG.error('could not retrieve graph for %s, %s', contenturi, e)
    if graph is None:
        #LOG.info("generate empty graph for %s", contenturi)
        graph = Graph(identifier=contenturi)
    else:
        #LOG.info('retrieved %d triples for %s', len(graph), graph.identifier)
        pass
    return graph


def resource_for_content(content):
    graph = graph_for_content(content)
    return Resource(graph, graph.identifier)

