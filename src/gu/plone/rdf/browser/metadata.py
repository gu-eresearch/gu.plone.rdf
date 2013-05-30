from gu.z3cform.rdf.fresnel.edit import FieldsFromLensMixin, RDFGroupFactory, getFieldsFromFresnelLens, getLens
from gu.repository.content.interfaces import IRepositoryMetadata
from z3c.form import form, field, group
from z3c.form.interfaces import DISPLAY_MODE, HIDDEN_MODE, INPUT_MODE
from plone.app.layout.viewlets import ViewletBase
from Acquisition import aq_inner
from zope.interface import alsoProvides
from z3c.form.interfaces import IFormLayer
#from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.browserpage import ViewPageTemplateFile
from plone.z3cform import z2
# from Acquisition.interfaces import IAcquirer
# from Acquisition import aq_base
# from zope.component import createObject
# from plone.dexterity.utils import addContentToContainer
import logging

LOG = logging.getLogger(__name__)


# starting from 0.6.0 version plone.z3cform has IWrappedForm interface
try:
    from plone.z3cform.interfaces import IWrappedForm
    HAS_WRAPPED_FORM = True
except ImportError:
    HAS_WRAPPED_FORM = False


class EditMetadataForm(FieldsFromLensMixin, group.GroupForm, form.EditForm):
    """
    An edit form which uses a fresnel lens to generate fields for current context.
    """

    _graph = None

    # def getContent(self):
    #     # make sure to load graph only once. Otherwise, we might reload
    #     # data from store after applying changes.
    #     if self._graph is None:
    #         self._graph = IRepositoryMetadata(self.context)
    #     return self._graph

    # def getContentGraph(self):
    #     # groups expect this method.
    #     # allows to work with two different content objects at once. (content, vs. graph)
    #     # Might need to clean this up a bit, because this is only necessary for adding / editing 
    #     # content fields and rdf fields at once.
    #     return self.getContent()

    def update(self):
        self.updateFields()
        super(EditMetadataForm, self).update()


class ViewMetadataForm(FieldsFromLensMixin, group.GroupForm, form.Form):
    """
    A display form which uses a fresnel lens to generate fields for current context.
    """


    id = 'view_metadata'

    _graph = None

    mode = DISPLAY_MODE

    # def getContent(self):
    #     # make sure to load graph only once. Otherwise, we might reload
    #     # data from store after applying changes.
    #     if self._graph is None:
    #         self._graph = IRepositoryMetadata(self.context)
    #     return self._graph

    # def getContentGraph(self):
    #     # groups expect this method.
    #     # allows to work with two different content objects at once. (content, vs. graph)
    #     # Might need to clean this up a bit, because this is only necessary for adding / editing 
    #     # content fields and rdf fields at once.
    #     return self.getContent()

    def update(self):
        self.updateFields()
        super(ViewMetadataForm, self).update()


class ViewMetadataViewlet(ViewletBase):
    """
    A viewlet that uses ViewMetadataForm to show rdf metadata about given context
    """

    index = ViewPageTemplateFile('rdfviewlet.pt')
    label = 'Metadata'

    def update(self):
        super(ViewMetadataViewlet, self).update()
        z2.switch_on(self, request_layer=IFormLayer)
        self.form = ViewMetadataForm(aq_inner(self.context), self.request)
        if HAS_WRAPPED_FORM:
            alsoProvides(self.form, IWrappedForm)
        self.form.update()


# TODO: Formextender ... might be useful for Add / Edit Forms.
#   turned out to be not useful at all, becuse it is very hard to separate
#   aspects (content vs. Graph) wit this method.

from plone.z3cform.fieldsets.extensible import FormExtender

# NOTE: the field extender is unusable for dexterity add forms. Dexterity tries to
#       apply the data to the object during add directly instead of relying on
#       the Group to decide which the proper content is. Furthermore, it would add
#       the data before the content has been added to the system, so there is no uuid
#       available yet.
class RDFFieldExtender(FieldsFromLensMixin, FormExtender):
    # TODO: This is an extender for add forms, which usually work on a non existent
    #       content object. the context here is the folder where the object will be
    #       added to.

    _graph = None
    groups = ()

    def getContent(self):
        # TODO: check parent / form for getContent and whether it's a temporaryitem
        # FIXME: don't assume this is an addform and need to customise initial rdf:type
        if self._graph is None:
            # import ipdb; ipdb.set_trace()
            # self._graph = IRepositoryMetadata(self.context)
            # if (None, RDF['type'], None) not in self._graph:
            #     import ipdb; ipdb.set_trace()
            #     self._graph.add((self._graph.identifier, RDF['type'], CVOCAB['Item']))
            self._graph = Graph()
            self._graph.add((self._graph.identifier, RDF['type'], CVOCAB['Item']))
        return self._graph


    def update(self):
        self.updateFields()
        self.add(self.fields)
        groups = list(self.form.groups)
        groups.extend(self.groups)
        self.form.groups = tuple(groups)

# TODO: below is a start for an pure RDF based add form. It won't work properly
#       to create actual content, and nedes refinement for creating RDF graphs.
#       esp.:
#       1. check for events to be fired (see dexterity add forms)
#       2. make sure URI is unique
#       3. needs fresnel group and at least one rdf:type

from plone.dexterity.browser.add import DefaultAddView, DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm
from ordf.graph import Graph
from ordf.namespace import RDF
from rdflib import Namespace
# from zope.component import getUtility
# from plone.dexterity.interfaces import IDexterityFTI
# from plone.dexterity.utils import createContent
CVOCAB = Namespace(u"http://namespaces.griffith.edu.au/collection_vocab#")

class RDFEditForm(FieldsFromLensMixin, DefaultEditForm):
    """
    An EditForm that mixes plone content fields and rdf fields (from a fresnel lens)
    """

    content = None

    # dexterity base update calls updateFields so we don't have to ourselvels
    # def update(self):
    #     self.updateFields()
    #     super(RDFEditForm, self).update()



#class RDFAddForm(FieldsFromLensMixin, DefaultAddForm):
class RDFAddForm(DefaultAddForm):
    """
    An AddForm that mixes plone content fields and rdf fields (from a fresnel lens)
    """
    # this form allows to add content + rdf metadat in one go.
    # the normal content fields are generated as usual, but the rdf
    # fields need to be in (form) Groups. Otherwise it would be impossible
    # to provide two different contexts. Z3c.forms relies on getContent() to
    # return the current content object. If rdf and plone fields are mixed in one
    # group, one or the other would fetch the wrong type of content.

    _graph = None
    content = None

    # def getContent(self):
    #     # satisfy standard forms we use super.applyChanges and not form.applyChanges.
    #     # super looks here for the actual content
    #     if self.content is None: # this crudge is necessary, because not all parts clearly distinguish between context and content
    #         return self.context
    #     return self.content

    # def getContentGraph(self):
    #     # we are an add form. there is no conent:
    #     if self._graph is None:
    #         if self.content is None:
    #             # two possibilities here. either don't store this temporary graph, or 
    #             # set self._graph to None when we create the real content (in create())
    #             _graph = Graph()
    #             _graph.add((_graph.identifier, RDF['type'], CVOCAB['Item']))
    #             return _graph
    #         self._graph = IRepositoryMetadata(self.content)
    #     return self._graph

    def getEmptyGraph(self):
        # need some minimal graph to work on. can't get graph for current context,
        # because this is an add form and current context is the place where we add stuff to.
        # not what we are going to create.
        # FXME: maybe just specify Lens, and ignore empty graph?
        if self._graph is None:
            _graph = Graph()
            # TODO: can I use the TypeMapper utility to find the correct rdf:type?
            _graph.add((_graph.identifier, RDF['type'], CVOCAB['Item']))
            self._graph = _graph
        return self._graph
            

    def updateFields(self):
        super(RDFAddForm, self).updateFields()

        from gu.z3cform.rdf.interfaces import IIndividual
        # FIXME: check why this is not reusable form the FieldsFromFresnelMixin. (is it the getEmptyGraph thingy?)
        individual = IIndividual(self.getEmptyGraph())
        lens = getLens(individual)
        LOG.info('individual types: %s', individual.type)
        LOG.info('picked lens: %s', lens)
        fields = []
        groups = ()
        if lens is not None:
            groups, fields = getFieldsFromFresnelLens(lens, individual.graph,
                                                      individual.identifier)

        if hasattr(self, 'groups'):
            if (self.groups or groups) and fields:
                g = RDFGroupFactory('Default_RDF_Lens', field.Fields(*fields),
                                    'RDF Metadata', None)
                fields = ()
                groups = (g, ) + groups
            self.groups += groups

        if self.fields is not None:
            self.fields += field.Fields(*fields)
        else:
            self.fields = field.Fields(*fields)

        # apply widgetFactories here
        for g in (self, ) + tuple(self.groups):
            for f in g.fields.values():
                if hasattr(f.field, 'widgetFactory'):
                    LOG.info('apply costum widgetFactory %s to for field %s', str(f.field.widgetFactory), f.field.__name__)
                    if isinstance(f.field.widgetFactory, dict):
                        for key, value in f.field.widgetFactory.items():
                            f.widgetFactory[key] = value
                    else:
                        f.widgetFactory = f.field.widgetFactory

    # def create(self, data):
    #     fti = getUtility(IDexterityFTI, name=self.portal_type)
    #     content = createObject(fti.factory)

    #     # Note: The factory may have done this already, but we want to be sure
    #     # that the created type has the right portal type. It is possible
    #     # to re-define a type through the web that uses the factory from an
    #     # existing type, but wants a unique portal_type!

    #     # TODO: how can it be that fti.getId() would be different for the same portal_type?
    #     #if hasattr(content, '_setPortalTypeName'):
    #     #    content._setPortalTypeName(fti.getId())
    #     if hasattr(content, '_setPortalTypeName'):
    #         content._setPortalTypeName(self.portal_type)

    #     return aq_base(content)

    # def add(self, object):
    #     fti = getUtility(IDexterityFTI, name=self.portal_type)
    #     container = aq_inner(self.context)
    #     new_object = addContentToContainer(container, object)
    #     # now we have a full content object we can work with; with real location etc...
    #     self.content = new_object
        
    #     if fti.immediate_view:
    #         self.immediate_view = "%s/%s/%s" % (container.absolute_url(), new_object.id, fti.immediate_view,)
    #     else:
    #         self.immediate_view = "%s/%s" % (container.absolute_url(), new_object.id)

    # def createAndAdd(self, data):

    #     import ipdb; ipdb.set_trace()
    #     new_object = super(RDFAddForm, self).createAndAdd(data)
    #     # everything is created and added, we can apply all of our data now
    #     # self.applyChanges(data)
    #     # another way to make this apply work, would be to defer the data update in an event listener.
    #     # this way one could use the default forms for all content fields, and use the event handler
    #     # to apply the rest. (relationfield works in a similar way, where a relation can only be finalised
    #     # when the actual objects exist)
    #     return new_object



class RDFAddView(DefaultAddView):

    form = RDFAddForm

# ++add++<name> traverser searches for:
#  1. (context, request, fti ), name -> usually None
#  2. (context, request, fti)  -> usually dexterity default add view (unnamed generic addview for fti based objects)
# if not ++add++ namespace is used, you could use any form....

# extender lookup:
# happens after schemata have been processed (in method updateFields)
#  1. (context, request, self(addform)) -> IFormExtender
