from plone.dexterity.browser.edit import DefaultEditForm
from plone.dexterity.browser.add import DefaultAddForm
from gu.z3cform.rdf.objectproperty import RDFObjectPropertySubForm
from gu.z3cform.rdf.objectproperty import RDFObjectPropertySubformFactory
from zope.interface import Interface
from zope.component import adapter
from z3c.form.interfaces import IFormLayer
from z3c.form import button
from gu.z3cform.rdf.interfaces import IRDFObjectPropertyField
from gu.z3cform.rdf.widgets.interfaces import IRDFObjectPropertyWidget


class DexterityEditRDFObjectPropertySubForm(RDFObjectPropertySubForm):

    @button.handler(DefaultEditForm.buttons['save'])
    def handleApply(self, action):
        super(DexterityEditRDFObjectPropertySubForm, self).handleApply(action)


@adapter(Interface,
         IFormLayer,
         DefaultEditForm,
         IRDFObjectPropertyWidget,
         IRDFObjectPropertyField)
class DexterityEditRDFObjectPropertySubformFactory(RDFObjectPropertySubformFactory):
    subformclass = DexterityEditRDFObjectPropertySubForm


class DexterityAddRDFObjectPropertySubForm(RDFObjectPropertySubForm):

    @button.handler(DefaultAddForm.buttons['save'])
    def handleApply(self, action):
        super(DexterityAddRDFObjectPropertySubForm, self).handleApply(action)


@adapter(Interface,
         IFormLayer,
         DefaultAddForm,
         IRDFObjectPropertyWidget,
         IRDFObjectPropertyField)
class DexterityAddRDFObjectPropertySubformFactory(RDFObjectPropertySubformFactory):
    subformclass = DexterityAddRDFObjectPropertySubForm
