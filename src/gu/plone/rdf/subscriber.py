from zope.lifecycleevent.interfaces import IObjectAddedEvent, IObjectModifiedEvent, IObjectRemovedEvent
from zope.component import getUtility
from gu.z3cform.rdf.interfaces import IORDF, IGraph
from rdflib import RDF, OWL
from zope.component import getUtilitiesFor
from gu.plone.rdf.interfaces import IRDFContentTransform
from Acquisition import aq_parent, aq_inner, aq_base
from zope.publisher.interfaces.browser import IBrowserRequest

import logging
LOG = logging.getLogger(__name__)


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
    graph = IGraph(object)
    LOG.info("Got %d triples for New item %s", len(graph), graph.identifier)
    # lookup all transform utilities and call them
    transformers = getUtilitiesFor(IRDFContentTransform)
    for transname, transtool in transformers:
        transtool.tordf(object, graph)
    handler = getUtility(IORDF).getHandler()
    # ... check for temporary folder...
    LOG.info("Initialise new item %s at %s", repr(object), repr(event.newParent))
    LOG.info("Posting %d triples for New item %s", len(graph), graph.identifier)
    handler.put(graph)


def ModifyGraph(object, event):
    # FIXME: might need to update other graph triples here too :) ... e.g. map plone dc fields to graph fields
    # FIXME: use transformers here too?
    LOG.info("Item: %s has been edited: %s", repr(object), repr(event))
    graph = IGraph(object)
    LOG.info("Got %d triples for item %s", len(graph), graph.identifier)
    transformers = getUtilitiesFor(IRDFContentTransform)
    for transname, transtool in transformers:
        transtool.tordf(object, graph)
    handler = getUtility(IORDF).getHandler()
    LOG.info("Posting %d triples for New item %s", len(graph), graph.identifier)
    handler.put(graph)


def RemoveGraph(object, event):
    LOG.info("Item: %s has been deleted: %s", repr(object), repr(event))
    # TODO: clean up removed triples ...
    #       1. remove Graph itself
    #       2. remove all relations pointing from here
    #       3. remove all relations pointing to here (might be hard to do for )
    try:
        graph = IGraph(object)
    except TypeError:
        # object doesn't have right interface, so ignore
        return
    # Note: just remove the graph. In theory it can be reconstructed by all the changesets that refer to it.
    handler = getUtility(IORDF).getHandler()
    # FIXME: happens when we remove the site
    # if handler is None:
    #     return
    handler.remove(graph)
    # 2. query all triples where graph.identifier is object and clear those too
    #    -> generates changeset
    #    if this is part of a relation document, clear the whole document?
