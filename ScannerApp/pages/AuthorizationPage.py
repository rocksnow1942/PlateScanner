import tkinter as tk
from . import BaseViewPage
import time
from ..utils import decode
import sys


class AuthorizationPage(BaseViewPage):    
    def __init__(self, parent, master):      
        super().__init__(parent,master)           
        self.createDefaultWidgets()
        self.placeDefaultWidgets()
        self.create_widgets()
        self.initKeyboard(type='lag',lag=1)
        self.state = ['validationStatus', ]
        self.lastInputTime = 0
        if not self.master.devMode:
            self.disableNextBtn()
    
    def placeDefaultWidgets(self):        
        self._msg.place(x=20, y=430, width=740)        
        self._prevBtn.place(x=340 , y=300,  height=90 ,width=130,)
        
        self._title.place(x=0,y=20,width=800,height=30)

    def create_widgets(self):
        self.scanVar = tk.StringVar()
        # self.scanVar1.set('1234567890')
        self.scan = tk.Label(
            self, textvariable=self.scanVar, font=('Arial', 65), )
        l1 = tk.Label(self, text='User Name', font=('Arial', 35)
                 )
        self.scan.place(x=100, y=160,width=600)  # grid(column=1,row=0,)
        l1.place(x=200, y=110,width=400)
       
    def showPage(self,):
        self.setTitle('Please Scan Your Badge','black')
        self.keySequence = []        
        self.tkraise()
        self.focus_set()        
        self.displaymsg('Scan Your Badge Before Proceed')
        

    def closePage(self):        
        self.resetState()
        

    def resetState(self):
        self.result  = self.resultType()
        self.scanVar.set("")
        self.keySequence = []        
     
    def prevPageCb(self):
        "return to previous page in the current routine"
        self.resetState()
        self.master.currentRoutine.prevPage()

    def keyboardCb(self,code):
        self.result = code      
        if sys.argv[-1] == '--dev':
            self.master.db.setUser({'username':'Hui Dev'})
            self.displaymsg(f'User is in dev mode.','green')
            self.after(500,self.startRoutine)
            return
        try:
            res = self.master.db.get(f'/user/{code}')            
            if res.status_code == 200:
                requirement = self.master.currentRoutine.requireAuthorization 
                user = res.json()
                self.scanVar.set(user.get('username','Unknown User'))
                if self.authorize(res.json(), requirement):
                    self.master.db.setUser(res.json())
                    self.after(500,self.startRoutine)
                    self.displaymsg(f'User is authorized.','green')
                else:
                    self.displaymsg(f'You are not authorized for this task.','red')
            else:
                self.scanVar.set('Invalid User')
                self.displaymsg('Invalid user ID.')
        except Exception as e:
            self.error(f'Authorization error: {e}')
            self.displaymsg(f'Auth error:{e}','red')

    def authorize(self,userObj,requirement):
        role = userObj.get('role',[])
        return requirement in role

    def startRoutine(self):
        self.resetState()
        self.master.currentRoutine.startRoutine()


        
            

 

        
        
   