import adsk.core, adsk.fusion, traceback

app = None
ui = None
_handlers = []
_skip_next_save = False

PARAM = 'version_major'

# ── Utility ──────────────────────────────────────────────

def get_or_create_param(design):
    p = design.userParameters.itemByName(PARAM)
    if p is None:
        p = design.userParameters.add(PARAM, adsk.core.ValueInput.createByReal(1), '', 'Version')
    return p

# ── Save handler ─────────────────────────────────────────

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
            p = get_or_create_param(design)
            p.expression = str(int(round(p.value)) + 1)
        except:
            if ui:
                ui.messageBox('SmartVersion – save error:\n' + traceback.format_exc())

# ── Comando: Reset ───────────────────────────────────────

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
                p.expression = '1'
                _skip_next_save = True
                ui.messageBox('Reset to v1 complete.\n\nSave the file to confirm.')
        except:
            ui.messageBox(traceback.format_exc())

# ── Setup UI ──────────────────────────────────────────────

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

    h = OnSaveHandler()
    app.documentSaving.add(h)
    _handlers.append(h)

    panel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
    add_button(panel, 'SmartVersionReset', 'Reset Version to 1',
               'Reset version_major to 1', ResetCreated)

def stop(context):
    panel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
    ctrl = panel.controls.itemById('SmartVersionReset')
    if ctrl: ctrl.deleteMe()
    defn = ui.commandDefinitions.itemById('SmartVersionReset')
    if defn: defn.deleteMe()
    _handlers.clear()