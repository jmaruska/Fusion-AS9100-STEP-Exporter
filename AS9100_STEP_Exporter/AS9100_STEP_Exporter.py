import adsk.core #type: ignore
import traceback
from datetime import datetime
import re, os

# Global application and user interface objects
app = adsk.core.Application.get()
ui = app.userInterface

# Button properties defined as a dictionary
button_properties = {
    'id': 'jm_STEPExporterCommand',
    'name': 'Export STEP (AS9100)',
    'description': 'Export current design as STEP file with AS9100 compliant naming options.',
    'resources': 'resources'
}

# List to keep track of event handlers to prevent garbage collection
handlers = []

def run(context):
    try:
        cleanupUI()  # Unregister any existing UI elements
        registerUI()  # Register UI elements
    except:
        ui.messageBox('Run Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        cleanupUI()  # Ensure UI elements are unregistered when the script stops
        # app.log('Stop Add-in')  # Log message indicating the add-in has stopped
    except:
        ui.messageBox('Stop Failed:\n{}'.format(traceback.format_exc()))

def registerUI():
    global button_properties
    try:
        scriptPath = os.path.dirname(__file__)  # Get the path of the current script
        button_properties['resources'] = os.path.join(scriptPath, 'resources')  # Path to the resources folder
        
        cmdDefs = ui.commandDefinitions  # Get the command definitions collection
        
        # Check if the command definition already exists
        cmdDef = cmdDefs.itemById(button_properties['id'])
        if cmdDef:
            cmdDef.deleteMe()  # Delete the existing command definition if it exists
        
        # Create a new button command definition
        cmdDef = cmdDefs.addButtonDefinition(button_properties['id'], button_properties['name'], button_properties['description'], button_properties['resources'])

        onCommandCreated = CommandCreatedEventHandler()  # Create an instance of the command created event handler
        cmdDef.commandCreated.add(onCommandCreated)  # Connect the event handler
        handlers.append(onCommandCreated)  # Add the handler to the list to prevent garbage collection

        designWorkspace = ui.workspaces.itemById('FusionSolidEnvironment')  # Get the "DESIGN" workspace
        addInsPanel = designWorkspace.toolbarPanels.itemById('SolidScriptsAddinsPanel')  # Get the "ADD-INS" panel

        # Check if the command control already exists
        cmdControl = addInsPanel.controls.itemById(button_properties['id'])
        if cmdControl:
            cmdControl.deleteMe()  # Delete the existing command control if it exists
        
        # Add the command to the "ADD-INS" panel
        cmdControl = addInsPanel.controls.addCommand(cmdDef)

        if cmdControl:
            cmdControl.isPromotedByDefault = True  # Make the button available in the panel by default
            cmdControl.isPromoted = True

    except:
        ui.messageBox('Register UI Failed:\n{}'.format(traceback.format_exc()))

def cleanupUI():
    try:
        designWorkspace = ui.workspaces.itemById('FusionSolidEnvironment')  # Get the "DESIGN" workspace
        addInsPanel = designWorkspace.toolbarPanels.itemById('SolidScriptsAddinsPanel')  # Get the "ADD-INS" panel

        cmdDef = ui.commandDefinitions.itemById(button_properties['id'])  # Attempt to remove the command definition
        if cmdDef:
            cmdDef.deleteMe()

        cmdControl = addInsPanel.controls.itemById(button_properties['id'])  # Attempt to remove the button control
        if cmdControl:
            cmdControl.deleteMe()

        for handler in handlers:  # Remove event handlers to prevent memory leaks
            if hasattr(handler, 'remove'):
                handler.remove()
        handlers.clear()  # Clear the handlers list

    except:
        ui.messageBox('Cleanup UI Failed:\n{}'.format(traceback.format_exc()))

class CommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        try:
            cmd = args.command  # Get the command object
            
            # Set the initial size of the command dialog
            cmd.setDialogInitialSize(350, 280)  # Set width to 350 pixels and height to 280 pixels

            onExecute = CommandExecuteHandler()  # Create an instance of the command execute event handler
            cmd.execute.add(onExecute)  # Connect the event handler
            handlers.append(onExecute)  # Add the handler to the list to prevent garbage collection
            
            onInputChanged = CommandInputChangedEventHandler()  # Create an instance of the input changed event handler
            cmd.inputChanged.add(onInputChanged)  # Connect the event handler
            handlers.append(onInputChanged)  # Add the handler to the list to prevent garbage collection
            
            inputs = cmd.commandInputs  # Get the command inputs collection
            # Add inputs for user interaction
            inputs.addBoolValueInput('includeProjectName', 'Include Project Name', True, '', True)
            inputs.addBoolValueInput('versionHandling', 'Fusion Version Number', True, '', True)
            inputs.addStringValueInput('arbitraryText', 'Author', '')
            inputs.addBoolValueInput('dateAppending', 'Append Date', True, '', True)
            
            # Add dropdown for delimiter choices
            delimiterDropdown = inputs.addDropDownCommandInput('delimiterChoice', 'Delimiter', adsk.core.DropDownStyles.TextListDropDownStyle)
            delimiterDropdown.listItems.add('Underscores', True)
            delimiterDropdown.listItems.add('Dashes', False)
            delimiterDropdown.listItems.add('Dots', False)
            delimiterDropdown.listItems.add('Spaces', False)
            
            fileNameInput = inputs.addTextBoxCommandInput('fileNamePreview', 'File Name Preview', '', 3, True)
            fileNameInput.isFullWidth = True  # Make the text box full width
            updateFileNamePreview(inputs)  # Update the file name preview based on the current inputs
        except:
            ui.messageBox('Command Created Event Failed:\n{}'.format(traceback.format_exc()))

class CommandInputChangedEventHandler(adsk.core.InputChangedEventHandler):
    def notify(self, args):
        try:
            updateFileNamePreview(args.inputs)  # Update the file name preview when an input changes
        except:
            ui.messageBox('Input Changed Event Failed:\n{}'.format(traceback.format_exc()))

def updateFileNamePreview(inputs):
    includeProjectNameInput = inputs.itemById('includeProjectName')
    dataFile = app.activeDocument.dataFile
    if dataFile and dataFile.parentProject and dataFile.parentProject.name:
        includeProjectNameInput.isEnabled = True  # Enable the input if a project name is available
    else:
        includeProjectNameInput.isEnabled = False  # Disable the input if no project name is available
        includeProjectNameInput.value = False  # Automatically uncheck if not applicable
        ui.messageBox('File not saved. Please save the file to include the project name in the file name preview.')

    includeProjectName = includeProjectNameInput.value
    versionHandling = inputs.itemById('versionHandling').value
    arbitraryText = inputs.itemById('arbitraryText').value
    dateAppending = inputs.itemById('dateAppending').value
    selectedItem = inputs.itemById('delimiterChoice').selectedItem
    delimiterChoice = selectedItem.name if selectedItem else 'Underscores'
    
    design = app.activeProduct  # Get the active design
    fileName = design.rootComponent.name  # Start with the root component name

    if includeProjectName:
        projectName = dataFile.parentProject.name
        fileName = projectName + " " + fileName
    
    if not versionHandling:
        fileName = re.sub(r'\s+v\d+$', '', fileName)
    else:
        versionMatch = re.search(r'(\s+)(v\d+)$', fileName)
        if versionMatch:
            fileName = re.sub(r'(\s+)(v\d+)$', " " + r'\2', fileName)
    
    if arbitraryText:
        fileName += " " + arbitraryText
    
    if dateAppending:
        fileName += " " + datetime.now().strftime('%Y-%m-%d')
    
    fileName += ".step"

    delimiter_map = {
        'Underscores': '_',
        'Dashes': '-',
        'Dots': '.',
        'Spaces': ' '
    }
    selected_delimiter = delimiter_map[delimiterChoice]
    fileName = fileName.replace(' ', selected_delimiter)

    inputs.itemById('fileNamePreview').text = fileName

class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, args):
        try:
            inputs = args.command.commandInputs  # Get the command inputs collection
            fileName = inputs.itemById('fileNamePreview').text  # Get the file name from the preview input            
            fileDialog = ui.createFileDialog()  # Create a file dialog
            fileDialog.isMultiSelectEnabled = False
            fileDialog.title = "Save STEP File"
            fileDialog.filter = 'STEP files (*.stp;*.step)'
            fileDialog.initialDirectory = os.path.expanduser('~/Documents')
            fileDialog.initialFilename = fileName
            dialogResult = fileDialog.showSave()
            
            if dialogResult == adsk.core.DialogResults.DialogOK:
                design = app.activeProduct  # Get the active design
                exportOptions = design.exportManager.createSTEPExportOptions(fileDialog.filename, design.rootComponent)
                design.exportManager.execute(exportOptions)
                ui.messageBox('Export Successful!')
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))