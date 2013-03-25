from zope.lifecycleevent.interfaces import IObjectAddedEvent, IObjectModifiedEvent, IObjectRemovedEvent
from gu.repository.content.interfaces import IRepositoryMetadata
from gu.repository.content.interfaces import IRepositoryContainer, IRepositoryItem
from zope.component import getUtility
from gu.z3cform.rdf.interfaces import IORDF
from rdflib import RDF, RDFS, Namespace, Literal, OWL

import logging
LOG = logging.getLogger(__name__)

# FIXME: move these to central place
DCTERMS = Namespace(u"http://purl.org/dc/terms/")
CVOCAB = Namespace(u"http://namespaces.griffith.edu.au/collection_vocab#")


from Acquisition import aq_parent, aq_inner, aq_base
from zope.publisher.interfaces.browser import IBrowserRequest

def isTemporaryItem(obj, checkId=True):
    """ check if the item has an acquisition chain set up and is not of
        temporary nature, i.e. still handled by the `portal_factory`;  if
        so return it, else return None """
    parent = aq_parent(aq_inner(obj))
    if parent is None:
        return True
    if IBrowserRequest.providedBy(parent):
        return True
    if checkId and getattr(obj, 'getId', None):
        parent = aq_base(parent)
        if getattr(parent, '__contains__', None) is None:
            return True
        elif obj.getId() not in parent:
            return True
    isTemporary = getattr(obj, 'isTemporary', None)
    if isTemporary is not None:
        try:
            if obj.isTemporary():
                return True
        except TypeError:
            return True # `isTemporary` on the `FactoryTool` expects 2 args
    return False

def InitialiseGraph(object, event):
    # TODO: make sure this is only done on initial creation (not move or similar)
    # FIXME: maybe restrict object types?
    # FIXME: this also fires on each update while creating the content :(
    if isTemporaryItem(object):
        LOG.info("skip added temporary item: %s", repr(object))
        return
    graph = IRepositoryMetadata(object)
    LOG.info("Got %d triples for New item %s", len(graph), graph.identifier)
    if IRepositoryItem.providedBy(object):
        graph.add((graph.identifier, RDF['type'], CVOCAB['Item']))
    elif IRepositoryContainer.providedBy(event.object):
        graph.add((graph.identifier, RDF['type'], CVOCAB['Collection']))
        
    graph.add((graph.identifier, RDF['type'], OWL['Thing']))
    # FIXME: use only noe way to describ ethings ....
    #        see dc - rdf mapping at http://dublincore.org/documents/dcq-rdf-xml/
    #        maybe dc app profile not as good as it might sound, but translated to RDF is better (or even owl)
    for prop, val in ((DCTERMS['title'], Literal(object.title)),
                      (RDFS['label'], Literal(object.title)),
                      (DCTERMS['description'], Literal(object.description)),
                      (RDFS['comment'], Literal(object.description)),
                      ):
        if not graph.value(graph.identifier, prop):
            graph.add((graph.identifier, prop, val))
    # FIXME: persist stuff here? (would be nice to make this part of normal transaction)
    handler = getUtility(IORDF).getHandler()
    # ... check for temporary folder...
    LOG.info("Initialise new item %s at %s", repr(object), repr(event.newParent))
    LOG.info("Posting %d triples for New item %s", len(graph), graph.identifier)
    handler.put(graph)


def ModifyGraph(object, event):
    # FIXME: might need to update other graph triples here too :) ... e.g. map plone dc fields to graph fields
    LOG.info("Item: %s has been edited: %s", repr(object), repr(event))
    graph = IRepositoryMetadata(object)
    oldlen = len(graph)  # good enought for the current type of changes we do
    LOG.info("Got %d triples for New item %s", len(graph), graph.identifier)
    graph.add((graph.identifier, RDF['type'], OWL['Thing']))
    if len(graph) != oldlen:
        # FIXME: make persistence part of transaction commit
        handler = getUtility(IORDF).getHandler()
        LOG.info("Posting %d triples for New item %s", len(graph), graph.identifier)
        handler.put(graph)


# FIXME: this DataManager should go into a base package
# in the long term, this should be done via a datamanager that works within the current transaction,
# and supprots savepoints too
import transaction
        
def RemoveGraph(object, event):
    LOG.info("Item: %s has been deleted: %s", repr(object), repr(event))
    # TODO: clean up removed triples ...
    #       1. remove Graph itself
    #       2. remove all relations pointing from here
    #       3. remove all relations pointing to here (might be hard to do for )
    graph = IRepositoryMetadata(object)
    # Note: just remove the graph. In theory it can be reconstructed by all the changesets that refer to it.
    handler = getUtility(IORDF).getHandler()
    handler.remove(graph)
    # 2. query all triples where graph.identifier is object and clear those too
    #    -> generates changeset
    #    if this is part of a relation document, clear the whole document?


