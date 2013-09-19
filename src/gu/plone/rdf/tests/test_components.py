import unittest2 as unittest
from gu.z3cform.rdf.interfaces import IORDF
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


# test SubformAdapter lookup
# test ORDFUtility interface conformance


class ORDFUtilityTest(unittest.TestCase):

    def _getTargetClass(self):
        from gu.plone.rdf.component import ORDFUtility
        return ORDFUtility

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()()

    def test_class_conforms_to_IORDF(self):
        verifyClass(IORDF, self._getTargetClass())

    def test_instance_conforms_to_IORDF(self):
        verifyObject(IORDF, self._makeOne())
