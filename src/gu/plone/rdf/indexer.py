from plone.indexer import indexer
from plone.uuid.interfaces import IUUIDAware
from zope.component import getUtility
from gu.z3cform.rdf.interfaces import IORDF
import logging


LOG = logging.getLogger(__name__)


@indexer(IUUIDAware)
def subjectURIIndexer(context):
    # do somechecking here, e.g. only do this if the mimetype is
    # suitable for indexing etc..
    contenturi = getUtility(IORDF).getContentUri(context)
    #LOG.info('Index subjecturi for %s' % contenturi)
    return unicode(contenturi)
