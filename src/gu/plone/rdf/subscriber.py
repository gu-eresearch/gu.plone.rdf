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
    graph.add((graph.identifier, DCTERMS['title'], Literal(object.title)))
    graph.add((graph.identifier, RDFS['label'], Literal(object.title)))
    graph.add((graph.identifier, DCTERMS['description'], Literal(object.description)))
    graph.add((graph.identifier, RDFS['comment'], Literal(object.description)))

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
    # FIXME: let handler be transaction aware ... this way we can get rid of all transaction specific
    #        code from plone, and make transaction awareness configurable
    transaction.get().join(RDFDataManager(object, event))


from transaction.interfaces import ISavepointDataManager, IDataManagerSavepoint
from zope.interface import implements
import transaction

# /Users/gerhard/Downloads/buildout/eggs/alm.solrindex-1.1.1-py2.7.egg/alm/solrindex/index.py
# /Users/gerhard/Downloads/buildout/eggs/collective.indexing-2.0a3-py2.7.egg/collective/indexing/transactions.py
# /Users/gerhard/Downloads/buildout/eggs/p01.fsfile-0.6.0-py2.7.egg/p01/fsfile/storage.py
# /Users/gerhard/Downloads/buildout/eggs/p01.fsfile-0.6.0-py2.7.egg/p01/fsfile/tm.py
# /Users/gerhard/Downloads/buildout/eggs/p01.tmp-0.6.0-py2.7.egg/p01/tmp/file.py
# /Users/gerhard/Downloads/buildout/eggs/z3c.indexer-0.6.0-py2.7.egg/z3c/indexer/interfaces.py
# /Users/gerhard/Downloads/buildout/eggs/zope.sendmail-3.7.5-py2.7.egg/zope/sendmail/delivery.py

class RDFDataManager(object):

    implements(ISavepointDataManager)

    transaction_manager = transaction.manager

    def __init__(self, object, event):
        self.object = object
        self.event = event

    def abort(self, transaction):
        LOG.info("TRANSACTION: abort %s", repr(self.object))
    
    # Two-phase commit protocol.  These methods are called by the ITransaction
    # object associated with the transaction being committed.  The sequence
    # of calls normally follows this regular expression:
    #     tpc_begin commit tpc_vote (tpc_finish | tpc_abort)

    def tpc_begin(self, transaction):
        """Begin commit of a transaction, starting the two-phase commit.

        transaction is the ITransaction instance associated with the
        transaction being committed.
        """
        LOG.info("TRANSACTION: tpc_begin %s", repr(self.object))
        # TODO: prepare whatever is necessary to commit transaction

    def commit(self, transaction):
        """Commit modifications to registered objects.

        Save changes to be made persistent if the transaction commits (if
        tpc_finish is called later).  If tpc_abort is called later, changes
        must not persist.

        This includes conflict detection and handling.  If no conflicts or
        errors occur, the data manager should be prepared to make the
        changes persist when tpc_finish is called.
        """
        LOG.info("TRANSACTION: commit %s", repr(self.object))
        # TODO: apply changes to underlying object (not store), make sure transaction will commit

    def tpc_vote(self, transaction):
        """Verify that a data manager can commit the transaction.

        This is the last chance for a data manager to vote 'no'.  A
        data manager votes 'no' by raising an exception.

        transaction is the ITransaction instance associated with the
        transaction being committed.
        """
        LOG.info("TRANSACTION: tpc_vote %s", repr(self.object))
        # TODO: last chance checks to see whether we sholud commit or not

    def tpc_finish(self, transaction):
        """Indicate confirmation that the transaction is done.

        Make all changes to objects modified by this transaction persist.

        transaction is the ITransaction instance associated with the
        transaction being committed.

        This should never fail.  If this raises an exception, the
        database is not expected to maintain consistency; it's a
        serious error.
        """
        LOG.info("TRANSACTION: tpc_finish %s", repr(self.object))
        # ok let's work it out here:
        graph = IRepositoryMetadata(self.object)
        if IObjectRemovedEvent.providedBy(self.event):
            # Note: just remove the graph. In theory it can be reconstructed by all the changesets that refer to it.
            handler = getUtility(IORDF).getHandler()
            handler.remove(graph)
            # 2. query all triples where graph.identifier is object and clear those too
            #    -> generates changeset
            #    if this is part of a relation document, clear the whole document?
        # TODO: finally persist data here to triple store, this should never ever fail

    def tpc_abort(self, transaction):
        """Abort a transaction.

        This is called by a transaction manager to end a two-phase commit on
        the data manager.  Abandon all changes to objects modified by this
        transaction.

        transaction is the ITransaction instance associated with the
        transaction being committed.

        This should never fail.
        """
        LOG.info("TRANSACTION: tpc_abort %s", repr(self.object))        
        # TODO: undo changes, make sure nothing get's written to store

    def sortKey(self):
        """Return a key to use for ordering registered DataManagers.

        ZODB uses a global sort order to prevent deadlock when it commits
        transactions involving multiple resource managers.  The resource
        manager must define a sortKey() method that provides a global ordering
        for resource managers.
        """
        # Alternate version:
        #"""Return a consistent sort key for this connection.
        #
        #This allows ordering multiple connections that use the same storage in
        #a consistent manner. This is unique for the lifetime of a connection,
        #which is good enough to avoid ZEO deadlocks.
        #"""
        return 'rdfdm' + str(id(self))

    def savepoint(self):
        """Return a data-manager savepoint (IDataManagerSavepoint).

        this is called by a transaction in in case a saveponit is requested.
        """
        LOG.info("TRANSACTION: savepoint %s", repr(self.object))        
        # TODO: return at least a Non RollBack Savepoint here.


class RDFSavePoint(object):

    implements(IDataManagerSavepoint)

    def rollback(self):
        """Rollback any work done since the savepoint.
        """
        pass


# class ISynchronizer(zope.interface.Interface):
#     """Objects that participate in the transaction-boundary notification API.
#     """

#     def beforeCompletion(transaction):
#         """Hook that is called by the transaction at the start of a commit.
#         """

#     def afterCompletion(transaction):
#         """Hook that is called by the transaction after completing a commit.
#         """

#     def newTransaction(transaction):
#         """Hook that is called at the start of a transaction.

#         This hook is called when, and only when, a transaction manager's
#         begin() method is called explictly.
#         """
