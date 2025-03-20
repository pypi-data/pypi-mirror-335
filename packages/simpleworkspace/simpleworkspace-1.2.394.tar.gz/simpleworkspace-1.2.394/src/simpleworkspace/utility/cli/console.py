import os as _os
from simpleworkspace.utility import strings as _strings
import abc as _abc
from simpleworkspace.settingsproviders import SettingsManager_BasicConfig as _SettingsManager_BasicConfig


def LevelPrint(level:int, msg="", flush=False, end='\n'):
    print(_strings.IndentText(msg, level, indentStyle='  '), flush=flush, end=end)

def LevelInput(level:int, msg="", flush=False, end=''):
    LevelPrint(level,msg=msg,flush=flush,end=end)
    return input()

def Clear():
    _os.system("cls" if _os.name == "nt" else "clear")
    return

def Dialog_EnterToContinue(msg="", indentLevel=0):
    if msg != "":
        msg += " - "
    msg += "Press enter to continue..."
    LevelInput(indentLevel, msg)

def Dialog_YesOrNo(question:str, indentLevel=0) -> bool:
    '''
    prompts user indefinitely until one of the choices are picked

    output style: "<question> [Y/N]:"
    @return: boolean yes=True, no=False
    '''
    
    while(True):
        answer = LevelInput(indentLevel, question + " [Y/N]:").upper()
        if(answer == "Y"):
            return True
        elif(answer == "N"):
            return False

def Dialog_SelectFiles(message="Enter File Paths", indentLevel=0) -> list[str]|None:
    import shlex
    LevelPrint(indentLevel, message)
    filepathString = LevelInput(indentLevel, "-")
    filepaths = shlex.split(filepathString)
    if(len(filepaths) == 0):
        return None
    return filepaths

class ConsoleWidgets:
    class View(_abc.ABC):
        def __init__(self, parent:'ConsoleWidgets.View'=None):
            self.name = self.__class__.__name__
            '''The title displayed in namespaces and parent menus'''
            self.views:list[ConsoleWidgets.View] = []
            '''Child views that will be shown as selectable options'''

            self.view_header:str = None
            '''Adds a message right below the namespace of the view'''
            self.view_tmp_message:str = None
            '''Adds a temporary message that is shown once, mainly for child views to give feedback'''
            self.level = 0
            self.parent = parent
            self.selectors:list[str] = None
            '''Normally subviews are selectable by a numeric index, this specifies one or multiple indexes instead, 
               eg instead of picking a view with number "1" it can be picked by any name such as "Save"'''

        @property
        def namespace(self):
            if(self.parent):
                return [*self.parent.namespace, self.name]
            return [self.name]
        
        def Menu_Init(self):
            """Menu hook that is called before menu renders"""

        def Menu_Show(self):
            """
            Sets up ui with current namespace view and child views as options if specified. 
            If there are menu options to choose from it becomes a blocking call until a valid choice is made or user goes back.
            Menu_Init() is used before every refresh to dynamically render the menu
            """
            while True:
                Clear()
                self.Menu_Init()
                namespaceString = '/' + '/'.join(self.namespace)
                if(len(namespaceString) > 100):
                    namespaceString = '/...' + namespaceString[-96:]
                LevelPrint(0, namespaceString)
                self.level = 1
                if(self.view_header):
                    LevelPrint(self.level, self.view_header, end='\n\n')
                if(self.view_tmp_message):
                    LevelPrint(self.level, f'[{self.view_tmp_message}]')
                    self.view_tmp_message = None
                if not self.views:
                    return
                choices:dict[str, ConsoleWidgets.View] = {}
                i = 1
                for view in self.views:
                    selectors = view.selectors if view.selectors else [str(i)]
                    for selector in selectors:
                        choices[selector] = view
                    if len(selectors) > 1:
                        selectorHintMsg = f"[{', '.join(selectors)}]"
                    else:
                        selectorHintMsg = selectors[0]
                    LevelPrint(self.level, f'{selectorHintMsg}. {view.name}')
                    i += 1

                if(self.parent is None):
                    LevelPrint(self.level, f'0. Quit')
                else:
                    LevelPrint(self.level, f'0. Go Back')

                answer = LevelInput(self.level, "- Input: ")
                if(answer == '0'):
                    return
                elif(answer in choices):
                    view = choices[answer]
                    view.level = self.level + 1
                    view.Start()
                    view.Close()
                else:
                    LevelInput(self.level + 1, "* Invalid input...")
            
        def Start(self):
            '''Start hook, can perform an action and return to parent view right away or call initview to make it interactive'''
            self.Menu_Show()

        def Close(self): ...
    
    class SettingsView(View):
        def __init__(self, settingsManager: _SettingsManager_BasicConfig, parent:'ConsoleWidgets.View'=None):
            class ChangeView(ConsoleWidgets.View):
                class AddNewSettingView(ConsoleWidgets.View):
                    def __init__(self, parent: ConsoleWidgets.View = None):
                        super().__init__(parent)
                        self.name = "Add New Setting"

                    def Start(self):
                        self.Menu_Show()
                        key = LevelInput(self.level, "Setting Name: ")
                        value = LevelInput(self.level, "Setting Value: ")
                        settingsManager.Settings[key] = value

                        self.parent.view_tmp_message = f"Added setting: {key}={value}"

                class RemoveASettingView(ConsoleWidgets.View):
                    def __init__(self, parent: ConsoleWidgets.View = None):
                        super().__init__(parent)
                        self.name = "Delete Setting"

                    def Start(self):
                        self.Menu_Show()
                        key = LevelInput(self.level, "Setting Name: ")
                        if(key in settingsManager.Settings):
                            del settingsManager.Settings[key] 
                            self.parent.view_tmp_message = f"Removed setting: {key}"
                        else:
                            self.parent.view_tmp_message = f"Setting not found: {key}"

                class ChangeASettingView(ConsoleWidgets.View):
                    def __init__(self, settingName:str, parent: ConsoleWidgets.View = None):
                        super().__init__(parent)
                        self.name = f'{settingName} = {settingsManager.Settings[settingName]}'
                        self.settingName = settingName
                    
                    def Start(self):
                        self.Menu_Show()
                        LevelPrint(self.level, f'Current: {self.name}')
                        newValue = LevelInput(self.level, "- New Value: ")
                        settingsManager.Settings[self.settingName] = newValue
                        self.parent.view_tmp_message = f"Changed setting: {self.settingName}={newValue}"
                        
                def __init__(self, parent: ConsoleWidgets.View = None):
                    super().__init__(parent)
                    self.name = "Change"
                    self.Menu_Init()

                def Menu_Init(self):
                    self.views = [
                        ChangeView.AddNewSettingView(parent=self),
                        ChangeView.RemoveASettingView(parent=self),
                        *[ChangeView.ChangeASettingView(key, parent=self) for key in settingsManager.Settings]
                    ]

                def Start(self):
                    self.Menu_Show()

            class ResetSettingsAction(ConsoleWidgets.View):
                def __init__(self, parent: ConsoleWidgets.View = None):
                    super().__init__(parent)
                    self.name = "Reset"
                def Start(self):
                    settingsManager.ClearSettings()
                    self.parent.view_tmp_message = "* Settings resetted, save settings to persist this change"

            class SaveSettingsAction(ConsoleWidgets.View):
                def __init__(self, parent: ConsoleWidgets.View = None):
                    super().__init__(parent)
                    self.name = 'Save'

                def Start(self):
                    settingsManager.SaveSettings()
                    self.parent._settingsHash = hash(frozenset(settingsManager.Settings.__dict__.items()))
                    self.parent.view_tmp_message = "* Settings Saved"
            
            super().__init__(parent)
            self.settingsManager = settingsManager
            self.name = "Settings"
            self.view_header = settingsManager.dataSource
            if not isinstance(settingsManager.dataSource, str):
                self.view_header = str(type(settingsManager.dataSource))
            self._settingsHash = hash(frozenset(settingsManager.Settings.__dict__.items()))
            self.defaultViewHeader = self.view_header
            self.views = [
                ChangeView(parent=self),
                ResetSettingsAction(parent=self),
                SaveSettingsAction(parent=self)
            ]

        def Menu_Init(self):
            if(hash(frozenset(self.settingsManager.Settings.__dict__.items())) != self._settingsHash):
                self.view_header = self.defaultViewHeader + " (Modified, save to persist)"
            else:
                self.view_header = self.defaultViewHeader
  
        def Start(self):
            self.Menu_Show()

                
        def Close(self):
            self.settingsManager.LoadSettings()