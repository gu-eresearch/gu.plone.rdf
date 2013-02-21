import ConfigParser
import logging
from cStringIO import StringIO

from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory
from zope.component.hooks import getSite
from zope.annotation.interfaces import IAnnotations

from ordf.handler import init_handler
from ordf.vocab.fresnel import Fresnel
#from org.ausnc.rdf.interfaces import IFresnelLensesModified
from gu.z3cform.rdf.interfaces import IORDF
from gu.plone.rdf.interfaces import IRDFSettings
from rdflib import URIRef, RDFS, ConjunctiveGraph
from rdflib import plugin


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
            registry = getUtility(IRegistry)
            settings = registry.forInterface(IRDFSettings, check=False)
            conf_str = "[ordf]\n" + settings.ordf_configuration
            cp = ConfigParser.SafeConfigParser()
            cp.readfp(StringIO(conf_str.encode('utf-8')))
            config = dict(cp.items('ordf'))
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

    def getFresnelGraph(self):
        if self.fresnel is None:
            LOG.info("reading fresnel graph form triple store")
            rdfhandler = self.getHandler()
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
        self.fresnel = None
