import tkinter as tk
from .pages import AllPAGES
from .utils.camera import Camera,Mock
from .routines import Routines
import configparser
from .utils.logger import createFileHandler,Logger
from .utils.validators import BarcodeValidator
import json
from os import path
from .utils import decode
import json
from .utils import AMS_Database,Firebase
import sys
from pathlib import Path

class ScannerApp(tk.Tk,Logger):
    def __init__(self):
        super().__init__()
        self.loadConfig()
        self.validator = BarcodeValidator(self)

        # initialzie loggger
        self.fileHandler = createFileHandler('ScannerApp.log')
        Logger.__init__(self,'ScannerApp',logLevel=self.LOGLEVEL,
            fileHandler=self.fileHandler)
        self.title('Scanner App')
        self.resizable(0,0)

        if self.devMode:
            self.geometry('800x480+100+30')#-30
        else:
            self.geometry('800x480+0+-30')#-30

        if self.hasCamera:
            self.camera = Camera(scanConfig=self.scanConfig,
                            cameraConfig=self.cameraConfig,
                            dmtxConfig=self.dataMatrixConfig,
                            master = self)
        else:
            self.camera = Mock()
        
        # initialize database
        self.db = AMS_Database(self,self.URL)        
        self.firebase = Firebase(logger=self,**self.FirebaseConfig)

        container = tk.Frame(self)    
        container.pack(side='top',fill='both',expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # load routine first without initialize
        self.routine = {}
        for rName in self.enabledRoutine:
            self.routine[rName] = Routines[rName]

        # load pages
        self.pages = {}
        
        for F in AllPAGES:
            self.pages[F.__name__] = F(parent=container,master=self)
            self.pages[F.__name__].grid(row=0, column=0, sticky="nsew")
        
        # initialize routines        
        for rName in self.routine:
            self.routine[rName] = Routines[rName](master=self)

        # initialzie home page        
        self.showHomePage()
    
    # config properties delegated to properties, instead of directly access
    # So that when altering config.ini structure, only need to change it here.
    @property
    def URL(self):
        return self.config['appConfig']['databaseURL']
    @property
    def FirebaseConfig(self):
        # load the firebase credential from firebaseConfig.
        # the credential  is a json string.
        key = self.config['firebaseConfig']['firebaseKey']
        token = self.config['firebaseConfig']['firebaseToken']        
        res = json.loads(decode(key,token))
        res.update(url=self.config['firebaseConfig']['firebaseURL'])
        return res
    @property
    def cameraConfig(self):
        return self.config['cameraConfig']
    @property
    def scanConfig(self):
        return self.config['scanConfig']
    @property
    def devMode(self):
        return self.config['debugConfig']['appMode'] == 'dev'
    @property
    def LOGLEVEL(self):
        return self.config['debugConfig']['LOGLEVEL']

    @property
    def enabledRoutine(self):
        return self.config['appConfig']['routines']
    @property
    def useCamera(self):
        return self.config['BarcodePage']['useCamera']
    @property
    def hasCamera(self):
        return self.config['debugConfig']['hasCamera']
    @property
    def codeValidationRules(self):
        return self.config['codeValidation']
    @property
    def dataMatrixConfig(self):
        return self.config['dataMatrixConfig']
    @property
    def currentUser(self):
        "return the current login username"
        return self.db.username


    def plateColor(self,plateType):
        return self.config['plateColors'].get(plateType,('',''))


    def validate(self,code,codeType=None):
        return self.validator(code,codeType)
    
    def validateInDatabase(self,code,codeType,validationType=None):
        return self.validator.validateInDatabase(code,codeType,validationType)

    def loadConfig(self):
        "load configuration from .ini"
        # load version from package.json
        with open('../package.json','rt') as f:
            self.__version__ = json.load(f).get('version')
        folder = Path(__file__).parent.parent
        config = configparser.ConfigParser()
        config.optionxform = str # to perserve cases in option names.
        inis = [folder / 'defaultConfig.ini',]
        if path.exists(folder / 'config.ini'):
            inis.append(folder / 'config.ini')
        if path.exists(folder / 'cameraConfig.ini'):
            inis.append(folder / 'cameraConfig.ini')
        config.read(inis)
        configdict = {}
        for section in config.sections():
            configdict[section]={}
            for key in config[section].keys():
                configdict[section][key] = eval(config[section][key])
        self.config = configdict

    def showHomePage(self):
        self.currentRoutine = None
        self.pages['HomePage'].showPage()
    
    def startRoutineCb(self, routineName):
        def cb():
            self.currentRoutine = self.routine[routineName]
            # if routine require authentication, check if user is logged in. Or show login page if run in devMode.
            if self.currentRoutine.requireAuthorization and sys.argv[-1] != '-dev':
                self.pages['AuthorizationPage'].showPage()            
            else:
                self.currentRoutine.startRoutine()
        return cb
 
    def on_closing(self):
        self.destroy()
    

