import logging

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from five import grok
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.directives import form
from plone.namedfile.field import NamedFile
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.component import getUtility
from zope.schema.vocabulary import SimpleVocabulary
from zope.event import notify
from rdflib import Graph, URIRef
from plone.registry.interfaces import IRegistry
from cStringIO import StringIO
from gu.plone.rdf import _
from gu.z3cform.rdf.interfaces import IORDF

LOG = logging.getLogger(__name__)

# FIME: move this somewhere generic e.g. into rdf base package ... a geniric func to determine input file format based on filename and/or mime-type
import os.path
def guessRDFFileFormat(format, contentType, filename):
    """
    determine file format:

    if format is not known, check contentType and filename

    TODO: take contentType into account
    """
    if format.lower() not in ('n3', 'xml'):
        ext = os.path.splitext(filename)[1].lower()
        if ext in ('.n3',):
            return u"n3"
        elif ext in ('.rdf', '.owl'):
            return u"xml"
        return None
    return format



class IManageGraphs(form.Schema):  # Interface):

    form.fieldset('upload',
                  label=u"Upload stuff",
                  fields=['replace', 'format', 'filedata']
                  )

    #form.widget(graph=CheckBoxFieldWidget)
    graph = schema.List(title=_(u"Graphs"),
        value_type=schema.Choice(
            title=_(u"Graph"),
            vocabulary="gu.z3cform.rdf.GraphVocabulary",
            )
        )

    newgraph = schema.URI(
        title=_(u"New Graph"),
        description=_(u"Enter a new graph URI here"),
        required=False,
        )

    replace = schema.Bool(
        title=_(u"Replace Graph"),
        required=True,
        default=False)

    format = schema.Choice(
        title=u'Format',
        vocabulary=SimpleVocabulary(
            [SimpleVocabulary.createTerm('auto', 'auto', u"Auto"),
             SimpleVocabulary.createTerm('n3', 'n3', u"N3"),
             SimpleVocabulary.createTerm('xml', 'xml', u"RDF/XML")]),
        required=True,
        default='auto',
        )

    filedata = NamedFile(
        title=_(u"RDF Data"),
        description=_(u"Please upload a file"),
        required=False,
        )
    downloadurl = schema.URI(
        title=_(u"File URL"),
        description=_(u"RDF data location"),
        required=False,
        )


    # TODO: file upload, (also in form)
    #       add / remove triples...
    #       query store


class RDFManageGraphsForm(form.SchemaForm):

    # TODO: allow for graph creation?
    #       download a graph
    #       execute a query?
    #       move file upload into separate tool... (see also rdf_upload.py)

    grok.context(INavigationRoot)
    grok.require('cmf.ManagePortal')
    grok.name('plone_rdf_managegraphs')

    ignoreContext = True
    template = ViewPageTemplateFile('managegraphs.pt')

    schema = IManageGraphs

    enable_form_tabbing = False

    #fields = field.Fields(IGraphManagement)

    def updateActions(self):
        super(RDFManageGraphsForm, self).updateActions()
        #self.actions['clearfresnel'].addClass("context")
        self.actions['clear'].addClass("standalone")
        self.actions['upload'].addClass("standalone")

    # @button.buttonAndHandler(u'Clear Fresnel Cache', name="clearfresnel")
    # def handleClearFresnelCache(self, action):
    #     notify(FresnelLensesModifiedEvent())

    @button.buttonAndHandler(u'Clear')
    def handleClear(self, action):
        # TODO: clear selected list on success.... (refresh from backend?)
        #       also change from add/remove widget to multi checkbox?
        data, errors = self.extractData()
        h = getUtility(IORDF).getHandler()
        for graphid in data.get('graph', []):
            g = Graph(identifier=URIRef(graphid))
            # TODO: that's not going via the queue. should it?
            h.remove(g)
            #self.notifyChanges(g)
            IStatusMessage(self.request).addStatusMessage(
                _(u"Graph %s deleted." % g), "info")
        self.request.response.redirect(self.request.getURL())

    def getGraph(self, data):
        """
        parse Graph from request
        """
        graphuri = self.getGraphURI(data)
        #g = Graph(store='TmpDiskStore', identifier=graphuri)
        g = Graph(identifier=graphuri)

        if data['filedata']:
            # uploaded file ...
            fmt = guessRDFFileFormat(data['format'],
                                     data['filedata'].contentType,
                                     data['filedata'].filename)
            g.parse(StringIO(data['filedata'].data), format=fmt)
        elif data['downloadurl']:
            # TODO: would be nice to check graph for graphuri, but it is
            #       already a bit late here... needs improvement
            g.parse(data['downloaduri'])
        return g

    def getGraphURI(self, data):
        """
        determine graphuri from request data
        """
        if data['newgraph']:
            return URIRef(data['newgraph'])
        if data['graph'][0]:
            return URIRef(data['graph'][0])
        return URIRef(data['downloadurl'])
        #3. check graph namespace?
        #    e.g.: - check for owl:Ontology:about ???
        #          - sorted([(len(x), x) for x in g.subjects()])[0]

    @button.buttonAndHandler(u'Upload')
    def handleUpload(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        error = None

        if not data.get('newgraph', None):
            if len(data.get('graph', [])) != 1:
                error = "Please select exactly one Graph to upload data to"
        if (not data.get('filedata', None)
            and not data.get('downloadurl', None)):
            error = "Please supply one data soure (file upload or downloadurl)"
        if not error:
            try:
                g = None  # ensure g is defined (in case getGraph throws exception)
                g = self.getGraph(data)
                rdftool = getUtility(IORDF)
                h = rdftool.getHandler()
                if data['replace']:
                    h.put(g)
                else:
                    h.append(g)
                # We went until here so it should all be fine
                #self.notifyChanges(g)
            except Exception, e:
                error = e
            finally:
                if g is not None:
                    g.close()
        if error:
            msg = u"RDF upload failed: %s" % str(error)
            msg_type = 'error'
            self.request.response.setStatus(status=400, reason=str(msg))
        else:
            msg = _(u"RDF upload successful")
            msg_type = 'info'
            self.request.response.redirect(self.request.getURL())
        IStatusMessage(self.request).add(msg, type=msg_type)

    # def notifyChanges(self, graph):
    #     registry = getUtility(IRegistry)
    #     settings = registry.forInterface(IRDFSettings, check=False)
    #     fresnelgraph = URIRef(settings.fresnel_graph_uri)
    #     if graph.identifier == fresnelgraph:
    #         notify(FresnelLensesModifiedEvent())
