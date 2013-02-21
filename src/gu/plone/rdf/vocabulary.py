from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implements
from zope.component import getUtility
from gu.z3cform.rdf.interfaces import IORDF
from gu.z3cform.rdf.vocabulary import QuerySimpleVocabulary
from ordf.graph import ConjunctiveGraph


class LocalGraphVocabularyFactory(object):

    implements(IVocabularyFactory)

    def __call__(self, context):
        h = getUtility(IORDF)
        store = h.getLocalStore()
        g = ConjunctiveGraph(store)
        uris = sorted([ctx.identifier for ctx in g.contexts()])
        # this here would be the natural way when parsing a sparql-xml-result
        #uris = sorted([item['g'] for item in g])
        return QuerySimpleVocabulary.fromValues(uris)
