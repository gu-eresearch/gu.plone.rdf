from zope.lifecycleevent.interfaces import IObjectAddedEvent
from gu.repository.content.interfaces import IRepositoryMetadata
from gu.repository.content.interfaces import IRepositoryContainer, IRepositoryItem
from zope.component import getUtility
from gu.z3cform.rdf.interfaces import IORDF
from rdflib import RDF, RDFS, Namespace, Literal

import logging
LOG = logging.getLogger(__name__)

# FIXME: move these to central place
DCTERMS = Namespace(u"http://purl.org/dc/terms/")
CVOCAB = Namespace(u"http://namespaces.griffith.edu.au/collection_vocab#")


def InitialiseGraph(object, event):
    # TODO: make sure this is only done on initial creation (not move or similar)
    graph = IRepositoryMetadata(object)
    LOG.info("Got %d triples for New item %s", len(graph), graph.identifier)
    if IRepositoryItem.providedBy(object):
        graph.add((graph.identifier, RDF['type'], CVOCAB['Item']))
    elif IRepositoryContainer.providedBy(event.object):
        graph.add((graph.identifier, RDF['type'], CVOCAB['Collection']))
    else:
        return
    # FIXME: use only noe way to describ ethings ....
    #        see dc - rdf mapping at http://dublincore.org/documents/dcq-rdf-xml/
    #        maybe dc app profile not as good as it might sound, but translated to RDF is better (or even owl)
    graph.add((graph.identifier, DCTERMS['title'], Literal(object.title)))
    graph.add((graph.identifier, RDFS['label'], Literal(object.title)))
    graph.add((graph.identifier, DCTERMS['description'], Literal(object.description)))
    graph.add((graph.identifier, RDFS['comment'], Literal(object.description)))

    # FIXME: persist stuff here? (would be nice to make this part of normal transaction)
    handler = getUtility(IORDF).getHandler()
    LOG.info("Posting %d triples for New item %s", len(graph), graph.identifier)
    handler.put(graph)

    
