from plone.indexer import indexer
from plone.uuid.interfaces import IUUIDAware
from gu.plone.rdf.repositorymetadata import getContentUri

import logging
LOG = logging.getLogger(__name__)

@indexer(IUUIDAware)
def subjectURIIndexer(context):
    # do somechecking here, e.g. only do this if the mimetype is
    # suitable for indexing etc..
    contenturi = getContentUri(context)
    #LOG.info('Index subjecturi for %s' % contenturi)
    return unicode(contenturi)
