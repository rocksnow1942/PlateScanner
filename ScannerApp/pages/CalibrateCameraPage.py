import tkinter as tk
from threading import Thread
from . import BaseViewPage
from ..utils import convertTubeID
import configparser
from pathlib import Path


class CalibratePage(BaseViewPage):
    resultType = list
    def __init__(self, parent, master):
        super().__init__(parent,master)
        self.specimenError = []        
        self.master = master
        self.create_widgets()
        self.camera = master.camera
        self.initKeyboard()
        self.state = ['specimenError']
        self.currentSelection = 0
        self.tempResult = []
        

    def resetState(self):
        self.result=self.resultType()        
        self.specimenError = []
        self.currentSelection = 0
        self.tempResult = []
        self.currentSelection = 0        
        self._prevBtn['state'] = 'normal'        
        self.readBtn['state'] = 'normal'        
        self.saveState.set('Save')

    def create_widgets(self):
        self._msgVar = tk.StringVar()
        self._msg = tk.Label(self, textvariable=self._msgVar, font=('Arial', 20))
        self._msg.place(x=20, y=430, width=740)
        self._titleVar = tk.StringVar()
        self._title = tk.Label(self,textvariable=self._titleVar, font=("Arial",20))
        self._title.place(x=40,y=20,width=720,height=30)
        self._prevBtn = tk.Button(self,text='Back',font=('Arial',32),command=self.prevPageCb)
        self._prevBtn.place(x=640, y=300,  height=90 ,width=130,)



        self.readBtn = tk.Button(self, text='Read', font=(
            'Arial', 32), command=self.read)
        self.readBtn .place(x=340, y=300, height=90, width=130)

        
        self.saveState = tk.StringVar()
        self.saveState.set('Save')
        self.saveBtn = tk.Button(self, textvariable=self.saveState, font=(
            'Arial', 28), command=self.save)
        self.saveBtn .place(x=490, y=300, height=90, width=130)
        
        X = 380
        Y = 100
        btnSize = 50
        self.upBtn = tk.Button(self, text='↑',    font=('Arial', 20), command=self.moveSelection('up'))
        self.downBtn = tk.Button(self, text='↓',  font=('Arial', 20), command=self.moveSelection('down'))
        self.leftBtn = tk.Button(self, text='←',  font=('Arial', 20), command=self.moveSelection('left'))
        self.rightBtn = tk.Button(self, text='→', font=('Arial', 20), command=self.moveSelection('right'))
        self.upBtn   .place(x=X,y=Y,width=btnSize,height=btnSize)
        self.downBtn .place(x=X,y=Y + btnSize * 2,width=btnSize,height=btnSize)
        self.leftBtn .place(x=X - btnSize,y=Y + btnSize,width=btnSize,height=btnSize)
        self.rightBtn.place(x=X + btnSize,y=Y + btnSize,width=btnSize,height=btnSize)

        X = X + btnSize * 3 + 20
        Y = 100
        btnSize = 50
        self.upBtn2 = tk.Button(self, text='↑',    font=('Arial', 20), command=self.moveSelection('up',1))
        self.downBtn2 = tk.Button(self, text='↓',  font=('Arial', 20), command=self.moveSelection('down',1))
        self.leftBtn2 = tk.Button(self, text='←',  font=('Arial', 20), command=self.moveSelection('left',1))
        self.rightBtn2 = tk.Button(self, text='→', font=('Arial', 20), command=self.moveSelection('right',1))
        self.upBtn2   .place(x=X,y=Y,width=btnSize,height=btnSize)
        self.downBtn2 .place(x=X,y=Y + btnSize * 2,width=btnSize,height=btnSize)
        self.leftBtn2 .place(x=X - btnSize,y=Y + btnSize,width=btnSize,height=btnSize)
        self.rightBtn2.place(x=X + btnSize,y=Y + btnSize,width=btnSize,height=btnSize)

        tk.Label(self,text='Brightness',font=('Arial',16)).place(x=X + btnSize * 2 + 20,y=Y)
        tk.Button(self, text='+', font=('Arial',20),command=self.adjustBrightness('+')).place(x=X + btnSize * 2 + 20,y=Y + btnSize, height=btnSize, width=btnSize)
        tk.Button(self, text='-', font=('Arial',20),command=self.adjustBrightness('-')).place(x=X + btnSize * 2 + 20,y=Y + btnSize * 2, height=btnSize, width=btnSize)

        tk.Button(self, text='Z', font=('Arial',20),command=self.zoom).place(x=X + btnSize * 2 + 20,y= Y - btnSize - 20, height=btnSize, width=btnSize)
    
    def zoom(self):
        self.camera.toggleZoom()

    def save(self,):
        "save a temp copy"
        if self.result and not (self.specimenError):
            self.tempResult = [i for i in self.result]
            self.saveState.set('Saved')
            self.displaymsg('Plate saved')
        else:
            self.displaymsg('Please read the whole plate without error.')

        
    def showPage(self,title="Calibrate Camera",msg="Place plate on reader and click read.",color='black'):
        self.setTitle(title,color)
        self.keySequence = []
        self.tkraise()
        self.focus_set()
        self.camera.start()
        self.camera.drawOverlay(self.specimenError)         
        self.displaymsg(msg)
        self.showPrompt()

    def closePage(self):
        self.master.camera.stop()
        #clean off keystrokes
        self.keySequence = []        

    def validateResult(self):
        "send the result to routein for validation"
        newerror = []        
        validlist,msg,bypass = self.master.currentRoutine.validateResult(self.result)
        # valid list is a boolean list to indicate if a well is valid or not
        # it can also be a string, = 'valid', 'invalid', 'non-exist', 'conflict'
        for i,valid in enumerate(validlist):
            if not valid:
                newerror.append((i,'red','invalid'))            
            elif self.tempResult:
                currentCode = self.result[i][1]
                savedCode = self.tempResult[i][1]
                if currentCode != savedCode:
                    newerror.append((i,'purple','conflict'))
        
        self.specimenError = newerror
        self.currentSelection =self.specimenError[0][0] if self.specimenError else None
        

    def keyboardCb(self, code):
        ""
        if code == 'snap':
            self.camera.snapshot()
            return
        if self.specimenError:
            idx = self.currentSelection
            if idx is None or idx >= len(self.result) or idx < 0:
                self.displaymsg('Select a proper sample')
                return
            posi = self.camera.indexToGridName(idx)
            self.result[idx] = (posi,code)
            self.validateResult()            
            self.camera.drawOverlay(self.specimenError,self.currentSelection)
            self.showPrompt()

        elif self.result:
            self.displaymsg('All specimen scaned.')
        else:
            self.displaymsg('Read specimen to start.')

    def read(self,):
        "read camera"        
        self._prevBtn['state'] = 'disabled'
        self.readBtn['state'] = 'disabled'
        self.specimenError = []
        self.result = []

        def read():            
            total = self.camera._scanGrid[0] * self.camera._scanGrid[1]                        
            for i, res in enumerate(self.camera.scanDTMX([],[],0,96,'calibrate')):
                position = self.camera.indexToGridName(i) # A1 or H12 position name
                convertedTubeID  = convertTubeID(res)
                self.displaymsg(
                    f'{"."*(i%4)} Scanning {i+1:3} / {total:3} {"."*(i%4)}')
                self.result.append((position,convertedTubeID))            
            self.validateResult()
            
            self.camera.drawOverlay(self.specimenError,self.currentSelection)
            self.showPrompt()
            self._prevBtn['state'] = 'normal'
            self.readBtn['state'] = 'normal'
            
        Thread(target=read,).start()

    def showPrompt(self):
        "display in msg box to prompt scan the failed sample."
        if self.specimenError:
            # idx = self.specimenError[0][0]
            idx = self.currentSelection
            text = 'valid'
            for error in self.specimenError:
                if idx == error[0]:
                    text = error[2]
                    break
            self.displaymsg(
                f"Rescan {self.result[idx][0]} {text}: current={self.result[idx][1]}", 'green' if text == 'valid' else 'red')
             
        elif self.result:
            self.displaymsg('All specimen scaned.', 'green')
            
    def adjustBrightness(self,direction):
        "adjust brightness"
        def cb():
            vol = 3 if direction == '+' else -3
            self.camera.adjustBrightness(vol)
            self.saveCameraConfig()
        return cb

    def saveCameraConfig(self):
        "save camera config"
        path = Path(__file__).parent.parent.parent
        file = path / 'cameraConfig.ini'
        config = configparser.ConfigParser()
        config.optionxform = str # to perserve cases in option names.
        config["scanConfig"]={}
        config["scanConfig"]['scanWindow'] = str(self.camera._scanWindow)
        config['cameraConfig'] = {}
        config["cameraConfig"]['brightness'] = str(self.camera.brightness)
        with open(file, 'w') as f:
            config.write(f)


    def moveSelection(self,direction,corner=0):
        def cb():
            x,y = 0,0
            if direction == 'left':
                y = -5
            elif direction == 'right':
                y = 5
            elif direction == 'up':
                x = -5
            elif direction == 'down':
                x = 5
            if corner == 0:
                adjustment = [x,y,0,0]
            if corner == 1:
                adjustment = [0,0,x,y]
            self.camera.adjustScanWindow(*adjustment)
            self.camera.drawOverlay(self.specimenError)
            self.saveCameraConfig()
        return cb