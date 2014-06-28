from App.config import getConfiguration
import ConfigParser
import logging

from zope.interface import implements
from zope.component.hooks import getSite
from zope.annotation.interfaces import IAnnotations
from zope.component import queryUtility
from ordf.handler import init_handler
from gu.z3cform.rdf.interfaces import IORDF
from rdflib import plugin, URIRef
import uuid
from Acquisition import aq_base
from plone.uuid.interfaces import IUUID


LOG = logging.getLogger(__name__)


PROPLABELQUERY = """
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

    handler = None

    def __init__(self):
        # init handler so that all threads see the same handler
        self.getHandler()
        # TODO: this needs to become thread safe.
        #       two threads might grab a handler
        #       they would overwrite each others handler.
        #       when re-getting a handler from here, the other thread might work with the wrong handler

    # TODO: check if it is ok to cache handler forever (e.g... connection to store not closed or unexpectedly closed on graph.glose()?)
    def getHandler(self):
        if self.handler is None:
            try:
                zconfig = getConfiguration()
                zconfig = zconfig.product_config.get('gu.plone.rdf', dict())
                ordfini = zconfig.get('inifile')
                cp = ConfigParser.SafeConfigParser()
                cp.read(ordfini)
                config = dict(cp.items('ordf'))
            except Exception as e:
                # FIXME: be specific about exceptions
                #   e.g.: AttributeError('product_config',) ... happens during test
                config = {'rdflib.store': 'ZODB'}
                LOG.warn("No valid product configuration found: using "
                         "default ZODB store (%s)", e)
            if config.get('rdflib.store', None) == 'ZODB':
                # TODO: this here could be optimised
                #   for ZODB there is no need to go through handler
                #   as read write is protected by transactions
                portal = getSite()
                # FIXME: happens when we remove the portal
                #        and during test setup
                if portal is None:
                    return None
                portal_annotations = IAnnotations(portal)
                store = portal_annotations.get('gu.plone.rdf.store')
                if store is None:
                    store = portal_annotations['gu.plone.rdf.store'] = plugin.get('ZODB', plugin.Store)()
                from ordf.handler import Handler
                from ordf.handler.rdf import RDFLib
                # For testing we use ZODB storage, let Zope transaction manager manage this
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

    def getBaseURI(self):
        """ return the base uri to be used for all content """
        settings = getConfiguration().product_config.get('gu.plone.rdf', dict())
        return settings.get('baseuri')

    def generateURI(self):
        """ generate a new unique uri using base uri """
        contenturi = "{}{}".format(self.getBaseURI(), uuid.uuid1())
        return URIRef(contenturi)

    def getContentUri(self, context):
        #1. determine subject uri for context
        # FIXME: use property, attribute, context absolute url
        from Products.ZCatalog.interfaces import ICatalogBrain
        if ICatalogBrain.providedBy(context):
            uuid = context.UID
        else:
            context = aq_base(context)
            uuid = IUUID(context, None)
        if uuid is None:
            # we probably deal with a new contet object that does not have an
            # uuid yet let's generate one
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

        # FIXME: shouldn't consult config here, IORDF does this.
        try:
            settings = getConfiguration().product_config.get('gu.plone.rdf', dict())
            baseuri = settings['baseuri']
        except Exception as e:
            # FIXME: be specific about exceptions
            baseuri = 'urn:plone:'
            LOG.warn("No baseuri configured: using %s (%s)", baseuri, e)
        contenturi = "%s%s" % (baseuri, uuid)
        return contenturi

