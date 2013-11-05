from plone.app.layout.viewlets import ViewletBase
from zope.browserpage import ViewPageTemplateFile
from plone.z3cform import z2
from plone.z3cform.fieldsets.extensible import ExtensibleForm
from z3c.form import form
from z3c.form.interfaces import DISPLAY_MODE, IFormLayer, IDisplayForm
from zope.browserpage import ViewPageTemplateFile
from zope.interface import alsoProvides, implementer
from Acquisition import aq_inner

# starting from 0.6.0 version plone.z3cform has IWrappedForm interface
try:
    from plone.z3cform.interfaces import IWrappedForm
    HAS_WRAPPED_FORM = True
except ImportError:
    HAS_WRAPPED_FORM = False


@implementer(IDisplayForm)
class ViewMetadataForm(ExtensibleForm, form.Form):
    """
    A display form which uses a fresnel lens to generate fields for current context.
    """

    id = 'view_metadata'

    mode = DISPLAY_MODE

    def update(self):
        super(ViewMetadataForm, self).update()


class ViewMetadataViewlet(ViewletBase):
    """
    A viewlet that uses ViewMetadataForm to show rdf metadata about given context
    """

    #index = ViewPageTemplateFile('rdfviewlet.pt')
    label = 'Metadata'

    def update(self):
        super(ViewMetadataViewlet, self).update()
        z2.switch_on(self, request_layer=IFormLayer)
        self.form = ViewMetadataForm(aq_inner(self.context), self.request)
        if HAS_WRAPPED_FORM:
            alsoProvides(self.form, IWrappedForm)
        self.form.update()
