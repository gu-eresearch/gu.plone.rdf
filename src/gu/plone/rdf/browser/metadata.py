from gu.z3cform.rdf import schema
from gu.z3cform.rdf.fresnel.edit import FieldsFromLensMixin
from gu.repository.content.interfaces import IRepositoryMetadata
from z3c.form import form
from z3c.form.interfaces import DISPLAY_MODE
from plone.app.layout.viewlets import ViewletBase
from Acquisition import aq_inner
from zope.interface import alsoProvides
from z3c.form.interfaces import IFormLayer
#from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.browserpage import ViewPageTemplateFile
from plone.z3cform import z2

# starting from 0.6.0 version plone.z3cform has IWrappedForm interface 
try:
    from plone.z3cform.interfaces import IWrappedForm 
    HAS_WRAPPED_FORM = True 
except ImportError: 
    HAS_WRAPPED_FORM = False


class EditMetadataForm(FieldsFromLensMixin, form.EditForm):

    _graph = None

    def getContent(self):
        # make sure to load graph only once. Otherwise, we might reload
        # data from store after applying changes.
        if self._graph is None:
            self._graph = IRepositoryMetadata(self.context)
        return self._graph

    def update(self):
        self.updateFields()
        super(EditMetadataForm, self).update()



class ViewMetadataForm(FieldsFromLensMixin, form.Form):

    id = 'view_metadata'

    _graph = None

    mode = DISPLAY_MODE

    def getContent(self):
        # make sure to load graph only once. Otherwise, we might reload
        # data from store after applying changes.
        if self._graph is None:
            self._graph = IRepositoryMetadata(self.context)
        return self._graph

    def update(self):
        self.updateFields()
        super(ViewMetadataForm, self).update()





class ViewMetadataViewlet(ViewletBase):

    index = ViewPageTemplateFile('rdfviewlet.pt')
    label = 'Metadata'

    def update(self):
        super(ViewMetadataViewlet, self).update()
        z2.switch_on(self, request_layer=IFormLayer)
        self.form = ViewMetadataForm(aq_inner(self.context), self.request)
        if HAS_WRAPPED_FORM: 
            alsoProvides(self.form, IWrappedForm)        
        self.form.update()
