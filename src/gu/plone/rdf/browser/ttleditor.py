from plone.directives import form
from zope import schema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from gu.z3cform.rdf.interfaces import IORDF
from rdflib import URIRef
from zope.component import getUtility
from Products.statusmessages.interfaces import IStatusMessage
from ordf.graph import Graph
from gu.repository.content.interfaces import IRepositoryMetadata

# TODO: make this form work on a context :)
#       -> allow to browse to related items ... e.g. render a list of outgoing links to edit
class ITTLEditor(form.Schema):

    #form.widget(graph='collective.z3cform.chosen.ChosenFieldWidget')
    graph = schema.Choice(
        title=u"Graph",
        vocabulary="gu.z3cform.rdf.GraphVocabulary",
        required=True,
        )

    ttl = schema.Text(title=u"Data",
                      required=False)

    
class TTLEditForm(form.SchemaForm):

    ignoreContext = True
    template = ViewPageTemplateFile("ttleditform.pt")

    schema = ITTLEditor

    enable_form_tabbing = False

    def update(self):
        super(form.SchemaForm, self).update()
        try:
            g = IRepositoryMetadata(self.context)
            self.widgets['ttl'].value = g.serialize(format='turtle')
            self.widgets['ttl'].rows = 20
            term = self.widgets['graph'].terms.getTerm(g.identifier)
            #self.widgets['graph'].value = term
            self.widgets['graph'].value = [term.token]
            self.widgets['graph'].style = u"width:500px"
        except Exception, e:
            msg = u"can't load current context: %s" % str(e)
            msg_type = 'error'
            self.request.response.setStatus(status=400, reason='Import failed')
            IStatusMessage(self.request).add(msg, type=msg_type)    
        
        

    @button.buttonAndHandler(u'Fetch')
    def handleFetch(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        graphuri = URIRef(data['graph'])
        import transaction
        transaction.abort()
        handler = getUtility(IORDF).getHandler()
        graph = handler.get(graphuri)
        try:
            self.widgets['ttl'].value = graph.serialize(format="turtle")
        except Exception, e:
            msg = u"RDF load failed: %s" % str(e)
            msg_type = 'error'
            self.request.response.setStatus(status=400, reason='Import failed')
        else:
            msg = u"RDF load successful"
            msg_type = 'info'
        IStatusMessage(self.request).add(msg, type=msg_type)

    @button.buttonAndHandler(u'Save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        graphuri = URIRef(data['graph'])
        graph = Graph(identifier=graphuri)
        handler = getUtility(IORDF).getHandler()
        try:
            graph.parse(data=data['ttl'], format='turtle')
            handler.put(graph)
        except Exception, e:
            msg = u"RDF upload failed: %s" % str(e)
            msg_type = 'error'
            self.request.response.setStatus(status=400, reason='Import failed')
        else:
            msg = u"RDF upload successful"
            msg_type = 'info'
        IStatusMessage(self.request).add(msg, type=msg_type)
