import tkinter as tk
from .pages import AllPAGES
from .utils.camera import Camera
from .routines import Routines
import configparser
from .utils.logger import createFileHandler,Logger
from .utils.validators import BarcodeValidator
import json
from os import path
from .utils import decode,mkdir
import json
from .utils import AMS_Database
from .utils.config import defaultConfig
import sys
from pathlib import Path
from .__version__ import version
import platform

isRunningOnPi = platform.platform().startswith('Linux')

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

        if isRunningOnPi:
            geo = '800x480-30-30'
        else:
            geo = '800x480+100+100'
        self.geometry(geo)#-30
        
        self.camera = Camera(scanConfig=self.scanConfig,                        
                            dmtxConfig=self.dataMatrixConfig,
                            master = self)
        
        # initialize database
        self.db = AMS_Database(self,self.URL)        
        # self.firebase = Firebase(logger=self)

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
        print("CONNECTED TO: " + self.config['appConfig']['databaseURL'])
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
        self.__version__ = version
        folder = Path(__file__).parent.parent
        folder = mkdir('userConfig')
        config = configparser.ConfigParser()
        config.optionxform = str # to perserve cases in option names.
                        
        config.read(folder / 'config.ini')

        configdict = defaultConfig
        for section in config.sections():
            if section not in configdict:
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
    

