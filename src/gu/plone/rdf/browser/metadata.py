from gu.z3cform.rdf import schema
from gu.z3cform.rdf.fresnel.edit import FieldsFromLensMixin
from gu.repository.content.interfaces import IRepositoryMetadata
from z3c.form import form
from z3c.form.interfaces import DISPLAY_MODE


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

    # def __call__(self):
    #     self.update()
    #     return self.render()

    # def render(self):
    #     '''See interfaces.IForm'''
    #     # render content template
    #     import zope.component
    #     from zope.pagetemplate.interfaces import IPageTemplate

    #     if self.template is None:
    #         template = zope.component.getMultiAdapter((self, self.request),
    #             IPageTemplate)
    #         return template(self)
    #     return self.template()

