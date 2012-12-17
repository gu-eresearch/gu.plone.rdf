import ConfigParser
import logging
from cStringIO import StringIO

from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory

from ordf.handler import init_handler
from ordf.vocab.fresnel import Fresnel
#from org.ausnc.rdf.interfaces import IFresnelLensesModified
from gu.z3cform.rdf.interfaces import IORDF
from gu.plone.rdf.interfaces import IRDFSettings
from rdflib import URIRef, RDFS


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

    def getFresnelGraph(self):
        if self.fresnel is None:
            LOG.info("reading fresnel graph form triple store")
            rdfhandler = self.getHandler()
            registry = getUtility(IRegistry)
            settings = registry.forInterface(IRDFSettings, check=False)
            fresnelgraph = URIRef(settings.fresnel_graph_uri)
            formatgraph = rdfhandler.get(fresnelgraph)
            # turn it into a Fresnel graph
            formatgraph = Fresnel(store=formatgraph.store,
                                  identifier=formatgraph.identifier)
            LOG.info("compiling fresnel graph")
            formatgraph.compile()
            # cache property labels in formatgraph
            proplabels = rdfhandler.query(PROPLABELQUERY)
            for row in proplabels:
                formatgraph.add((row['p'], RDFS.label, row['l']))
            self.fresnel = formatgraph
        return self.fresnel
