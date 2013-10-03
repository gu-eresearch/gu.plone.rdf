import xml.etree.ElementTree as ET
from zope.component import getUtility
from gu.z3cform.rdf.interfaces import IORDF
from ordf.graph import Graph, ConjunctiveGraph

import logging
logger = logging.getLogger(__name__)

# TODO: create export step as well


def importLocalRDF(context):
    # TODO: allow to replace / add
    #       clear whole store
    #       clear single graphs
    #       support not just turtle

    xml = context.readDataFile('ontologies.xml')
    if xml is None:
        logger.debug('Nothing to import.')
        return

    logger.info('Import RDF data into local triple store')
    root = ET.fromstring(xml)

    tool = getUtility(IORDF)
    store = tool.getLocalStore()
    local = ConjunctiveGraph(store=store)

    for node in root:
        if node.tag not in('local', 'external'):
            raise ValueError('Unknown node: {}'.format(node.tag))
        file = node.get('file')
        uri = node.get('uri')

        filename = 'ontologies/{}'.format(file)
        data = context.readDataFile(filename)
        if data is None:
            raise ValueError('File missing: {}'.format(filename))
        if not uri:
            raise ValueError('Missing URI for graph: {}'.format(filename))

        if node.tag == 'local':
            logger.info('load {} into local store.'.format(file))
            local.parse(data=data, publicID=uri, format='turtle')
        elif node.tag == 'external':
            logger.info('load {} into external store.'.format(file))
            graph = Graph(identifier=uri)
            graph.parse(data=data, format='turtle')
            tool.getHandler().put(graph)
    tool.clearCache()