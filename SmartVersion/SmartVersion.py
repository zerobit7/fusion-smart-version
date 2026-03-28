import adsk.core, adsk.fusion, traceback, os, re

app = None
ui = None
_handlers = []
_skip_next_save = False

PARAM = 'version'
PARAM_OLD = 'version_major'

def get_or_create_param(design, initial_value=0):
    params = design.userParameters
    p = params.itemByName(PARAM)
    if p is None:
        old = params.itemByName(PARAM_OLD)
        start_value = int(round(old.value)) if old else initial_value
        p = params.add(PARAM, adsk.core.ValueInput.createByReal(start_value), '', 'Version')
        if old:
            old.deleteMe()
    return p

class OnActivateHandler(adsk.core.DocumentEventHandler):
    def notify(self, args):
        try:
            design = args.document.products.itemByProductType('DesignProductType')
            if design is None:
                return
            get_or_create_param(design, initial_value=0)
        except:
            pass

class OnSaveHandler(adsk.core.DocumentEventHandler):
    def notify(self, args):
        global _skip_next_save
        try:
            if _skip_next_save:
                _skip_next_save = False
                return
            design = args.document.products.itemByProductType('DesignProductType')
            if design is None:
                return
            p = get_or_create_param(design, initial_value=0)
            p.expression = str(int(round(p.value)) + 1)
        except:
            if ui:
                ui.messageBox('SmartVersion – save error:\n' + traceback.format_exc())

class ResetCreated(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        h = ResetExecute()
        args.command.execute.add(h)
        _handlers.append(h)

class ResetExecute(adsk.core.CommandEventHandler):
    def notify(self, args):
        global _skip_next_save
        try:
            design = app.activeProduct
            if not isinstance(design, adsk.fusion.Design):
                ui.messageBox('Please open a Design first.'); return
            p = get_or_create_param(design)
            current = int(round(p.value))
            result = ui.messageBox(
                f'Current version: v{current}\nReset to v1?\n\nThis action cannot be undone.',
                'SmartVersion – Reset',
                adsk.core.MessageBoxButtonTypes.YesNoButtonType,
                adsk.core.MessageBoxIconTypes.WarningIconType
            )
            if result == adsk.core.DialogResults.DialogYes:
                p.expression = '0'
                _skip_next_save = True
                ui.messageBox('Reset complete.\n\nSave the file to confirm: version will become v1.')
        except:
            ui.messageBox(traceback.format_exc())

class Export3MFCreated(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        h = Export3MFExecute()
        args.command.execute.add(h)
        _handlers.append(h)

class Export3MFExecute(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            design = app.activeProduct
            if not isinstance(design, adsk.fusion.Design):
                ui.messageBox('Please open a Design first.'); return

            p = get_or_create_param(design)
            version = int(round(p.value))
            doc_name = app.activeDocument.name
            doc_name_clean = re.sub(r'\s+v\d+$', '', doc_name).strip()
            suggested_name = f"{doc_name_clean}_v{version}.3mf"

            dialog = ui.createFileDialog()
            dialog.title = 'Export 3MF with version'
            dialog.filter = '3MF Files (*.3mf)'
            dialog.initialFilename = suggested_name
            dialog.isMultiSelectEnabled = False

            if dialog.showSave() != adsk.core.DialogResults.DialogOK:
                return

            filepath = dialog.filename
            if not filepath.lower().endswith('.3mf'):
                filepath += '.3mf'

            export_mgr = design.exportManager
            options = export_mgr.createC3MFExportOptions(design.rootComponent, filepath)
            export_mgr.execute(options)

            ui.messageBox(f'Exported successfully:\n{os.path.basename(filepath)}')

        except:
            ui.messageBox('SmartVersion – export error:\n' + traceback.format_exc())

def add_button(panel, cmd_id, label, tooltip, handler_created):
    defn = ui.commandDefinitions.itemById(cmd_id)
    if defn:
        defn.deleteMe()
    defn = ui.commandDefinitions.addButtonDefinition(cmd_id, label, tooltip)
    h = handler_created()
    defn.commandCreated.add(h)
    _handlers.append(h)
    panel.controls.addCommand(defn)

def run(context):
    global app, ui
    app = adsk.core.Application.get()
    ui  = app.userInterface

    h_save = OnSaveHandler()
    app.documentSaving.add(h_save)
    _handlers.append(h_save)

    h_open = OnActivateHandler()
    app.documentActivated.add(h_open)
    _handlers.append(h_open)

    panel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
    add_button(panel, 'SmartVersionReset', 'Reset Version to 1',
               'Reset version to 1', ResetCreated)
    add_button(panel, 'SmartVersionExport3MF', 'Export 3MF with version',
               'Export 3MF with version number in filename', Export3MFCreated)

def stop(context):
    panel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
    for cmd_id in ['SmartVersionReset', 'SmartVersionExport3MF']:
        ctrl = panel.controls.itemById(cmd_id)
        if ctrl: ctrl.deleteMe()
        defn = ui.commandDefinitions.itemById(cmd_id)
        if defn: defn.deleteMe()
    _handlers.clear()