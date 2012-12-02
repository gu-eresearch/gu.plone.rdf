from zope.component import getUtility
from z3c.form import button
from five import grok
from plone.directives import form
from plone.registry.interfaces import IRegistry
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from gu.plone.rdf import _
from gu.plone.rdf.interfaces import IRDFSettings

# TODO:
# -> value update events ...-> ORDFTool

class RDFControlPanelForm(form.SchemaEditForm):

    control_panel_view = "plone_control_panel"
    schema_prefix = None

    schema = IRDFSettings
    template = ViewPageTemplateFile('ordfsettings.pt')

    def getContent(self):
        return getUtility(IRegistry).forInterface(self.schema,
                                                  prefix=self.schema_prefix)

    def updateWidgets(self):
        super(RDFControlPanelForm, self).updateWidgets()
        self.widgets['ordf_configuration'].rows = 20

    def updateActions(self):
        super(RDFControlPanelForm, self).updateActions()
        self.actions['save'].addClass("context")
        self.actions['cancel'].addClass("standalone")

    @button.buttonAndHandler(_(u"Save"), name='save')
    def handleSave(self, action):
        # TODO: validate configuration,.....
        #       -> check for parse errors, and create handler,....
        data, errors = self.extractData()
        if errors:
            #view = zope.component.getMultiAdapter(
            #        (error(exc), self.request, widget(None), widget.field(None),
            #         self.form, self.content), interfaces.IErrorViewSnippet)
            #view appended to errors
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_(u"Changes saved."),
                                                      "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  self.control_panel_view))

    @button.buttonAndHandler(_(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_(u"Edit cancelled."),
                                                      "info")
        self.request.response.redirect("%s/%s" % (self.context.absolute_url(),
                                                  self.control_panel_view))
