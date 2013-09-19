from App.config import getConfiguration
import ConfigParser
import logging
from cStringIO import StringIO

from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import implements
from zope.component.hooks import getSite
from zope.annotation.interfaces import IAnnotations

from ordf.handler import init_handler
from gu.z3cform.rdf.fresnel.fresnel import Fresnel
#from org.ausnc.rdf.interfaces import IFresnelLensesModified
from gu.z3cform.rdf.interfaces import IORDF
from gu.plone.rdf.interfaces import IRDFSettings
from rdflib import plugin, URIRef
import uuid


LOG = logging.getLogger(__name__)

PROPLABELQUERY =  """
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:<http://www.w3.org/2002/07/owl#>

SELECT DISTINCT ?p ?l
WHERE {
  {
    ?p rdf:type rdf:Property .
    ?p rdfs:label ?l .
  } UNION {
    ?p rdf:type owl:ObjectProperty .
    ?p rdfs:label ?l .
  } UNION {
    ?p rdf:type owl:DatatypeProperty .
    ?p rdfs:label ?l .
  } UNION {
    ?p rdf:type owl:AnnotationProperty .
    ?p rdfs:label ?l .
  } UNION {
    ?p rdf:type owl:SymmetricProperty .
    ?p rdfs:label ?l .
  }
}
"""

#### Utilites

class ORDFUtility(object):
    # TODO: rethink this utility, and maybe make it easier to fetch content, or fresnel lenses based on context / browser layer.
    #       e.g. make this utility the central API entry point
    implements(IORDF)

    # TODO: need to find a way to reset this even in a multi-ZEO client setup
    fresnel = None
    handler = None

    # TODO: check if it is ok to cache handler forever (e.g... connection to store not closed or unexpectedly closed on graph.glose()?)
    def getHandler(self):
        if self.handler is None:
            zconfig = getConfiguration()
            zconfig = zconfig.product_config.get('gu.plone.rdf', dict())
            ordfini = zconfig.get('inifile')
            cp = ConfigParser.SafeConfigParser()
            cp.read(ordfini)
            config = dict(cp.items('ordf'))
            if config.get('rdflib.store', None) ==  'ZODB':
                # TODO: this here could be optimised
                #   for ZODB there is no need to go through handler
                #   as read write is protected by transactions
                portal = getSite()
                # FIXME: happens when we remove the portal
                # if portal is None:
                #     return None
                portal_annotations = IAnnotations(portal)
                store = portal_annotations.get('gu.plone.rdf.store')
                if store is None:
                    store = portal_annotations['gu.plone.rdf.store'] = plugin.get('ZODB', plugin.Store)()
                from ordf.handler import Handler
                from ordf.handler.rdf import RDFLib
                handler = Handler()
                reader = RDFLib(store=store)
                handler.reader = reader
                reader.handler = handler
                handler.register_reader(reader)
                writer = RDFLib(store=store)
                handler.writer = writer
                writer.handler = handler
                handler.register_writer(writer)
                return handler
                self.handler = handler
            else:
                self.handler = init_handler(config)
        return self.handler

    def getLocalStore(self):
        portal = getSite()
        # next step could be necessary
        # portal = getToolByName(portal, 'portal_url').getPortalObject()
        portal_annotations = IAnnotations(portal)
        store = portal_annotations.get('gu.plone.rdf')
        if store is None:
            store = portal_annotations['gu.plone.rdf'] = plugin.get('ZODB', plugin.Store)()
        return store

    def getFresnel(self):
        if self.fresnel is None:
            LOG.info("reading fresnel graph from triple store")
            #rdfhandler = self.getHandler()
            registry = getUtility(IRegistry)
            settings = registry.forInterface(IRDFSettings, check=False)
            formatgraphuri = URIRef(settings.fresnel_graph_uri)
            store = self.getLocalStore()
            # TODO: make it optional to store application data in ZODB or external triple store
            formatgraph = Fresnel(store=store,
                                  identifier=formatgraphuri)
            LOG.info("compiling fresnel graph")
            formatgraph.compile()

            # TODO: maybe cache property labels from external store in formatgraph
            # proplabels = rdfhandler.query(PROPLABELQUERY)
            # for row in proplabels:
            #     formatgraph.add((row['p'], RDFS.label, row['l']))
            #
            #
            #    an alternative to deal with multiple data sources
            #    >>> unionGraph = ReadOnlyGraphAggregate([g1, g2])
            #    >>> uniqueGraphNames = set(
            #    ...     [graph.identifier for s, p, o, graph in unionGraph.quads(
            #    ...     (None, RDF.predicate, None))])
            #    >>> len(uniqueGraphNames)

            # FIXME: compiled graph is cached until restart of instance
            self.fresnel = formatgraph
        return self.fresnel

    def getURI(self, context, request=None):
        # TODO: implement this:
        #       check request for parameters / uri elements and look at content to determine URI
        #       for rdf-graph.
        raise NotImplementedError()

    def getGraph(self, context, request=None):
        # TODO: implement this:
        #       fetch graph with current handler and return it.
        raise NotImplementedError()

    def clearCache(self):
        # TODO: update all other instances too ... maybe store fresnel in memcached?
        self.fresnel = None

    def getBaseURI(self):
        """ return the base uri to be used for all content """
        settings = getConfiguration().product_config.get('gu.plone.rdf', dict())
        return settings.get('baseuri')

    def generateURI(self):
        """ generate a new unique uri using base uri """
        contenturi = "{}{}".format(self.getBaseURI(), uuid.uuid1())
        return URIRef(contenturi)
