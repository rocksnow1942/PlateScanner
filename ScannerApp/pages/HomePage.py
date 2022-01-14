import tkinter as tk
from threading import Thread
import os
import requests,time,json
import time
from datetime import datetime

class HomePage(tk.Frame):
    def __init__(self,parent,master):
        super().__init__(parent)
        self.master = master
        self.buttons = []
        self.currentPage = 0
        self.maxPage = len(self.master.enabledRoutine)//4 + bool(len(self.master.enabledRoutine) % 4)
        self.create_widgets()
        Thread(target=self.checkUpdate,daemon=True).start()
        self.createTimerWidget()

    def createTimerWidget(self):
        self._timeVar = tk.StringVar()
        tk.Label(self,textvariable=self._timeVar,font=('Arial',14)).place(x=580,y=5)
        
        self.after(100,self._updateTimer)

    def _updateTimer(self):
        self._timeVar.set(datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
        self.after(1000,self._updateTimer)
    
    def checkUpdate(self):
        'check update every 1 hour'
        githubURL = 'https://raw.githubusercontent.com/rocksnow1942/PlateScanner/master/ScannerApp/__version__.py'
        while True:
            try:                
                res = requests.get(githubURL)
                ver = res.text.strip().split('\n')[0].split('=')[1].strip('"\' ')
                if  self.master.__version__ != ver:
                    self.versionVar.set(f'Update {self.master.__version__} -> {ver}')
                else:                    
                    self.versionVar.set(f'Appp Ver. {self.master.__version__}')
            except Exception as e:                
                self.versionVar.set('Check Update Error')
            time.sleep(3600)
            
     
        
    def create_widgets(self):
        "4 buttons Maximum"
        # rtBtnNames = {r.__name__:r.btnName for r in Routines}
        self.versionVar = tk.StringVar()
        self.versionVar.set(self.master.__version__)
        # tk.Label(self,textvariable=self.versionVar,).place(x=780,y=10,anchor='ne')
        tk.Label(self,textvariable=self.versionVar).place(x=350,y=0,height=30, width=100)

        tk.Button(self,text='Exit',font=('Arial',35),command=self.master.on_closing).place(
            x=630,y=400,height=50,width=150)

        self.pageVar = tk.StringVar()
        self.pageVar.set(f'1 / {self.maxPage}')
        tk.Label(self,textvariable=self.pageVar,font=('Arial',25)).place(x=350,y=400,width=100,height=50)

        self.prevBtn = tk.Button(self,text='<',font=('Arial',40),command=self.prevPage)
        self.prevBtn.place(x=300,y=400,width=50,height=50)
        self.prevBtn['state'] = 'disabled'

        self.nextBtn = tk.Button(self,text='>',font=('Arial',40),command=self.nextPage)
        self.nextBtn.place(x=450,y=400,width=50,height=50)
        if self.maxPage ==1:
            self.nextBtn['state'] = 'disabled'

        self.serverVar = tk.StringVar()
        
        self.serverStatus = tk.Label(self,textvariable=self.serverVar,font=('Arial',18))
        self.serverStatus.place(x=50,y=395,width=200,height=30)       

        self.dbHistoryVar = tk.StringVar()
        self.dbHistoryStatus = tk.Label(self,textvariable=self.dbHistoryVar,font=('Arial',18))
        self.dbHistoryStatus.place(x=50,y=425,width=200,height=30)       

        self.showBtnPage(self.currentPage)
        
        Thread(target = self.pollServer,daemon=True).start()
    
    def pollServer(self):
        while True:            
            # try:
            #     t0=time.perf_counter()                
            #     requests.get('https://www.google.com',timeout=1)
            #     dt = time.perf_counter() - t0
            #     internet = f"{int((dt) * 1000)}ms"
            #     self.master.firebase.offline=False
            # except:                
            #     internet = "Offline"
            #     self.master.firebase.offline=True
            try:                
                t0=time.perf_counter()
                requests.get(self.master.URL,timeout=1)
                dt = time.perf_counter() - t0
                mongo = f"{int((dt) * 1000)}ms"
                self.master.db.offline=False
            except:          
                self.master.db.offline=True                
                mongo='Offline'

            # fbL = self.master.firebase.requestHistoryLenth 
            dbL = self.master.db.requestHistoryLenth 
            if  dbL==0:
                self.dbHistoryVar.set('All saved')
                self.dbHistoryStatus.config(fg='green')
            else:
                # self.dbHistoryVar.set(f'G:{fbL} A:{dbL} To Save')
                self.dbHistoryVar.set(f'A:{dbL} To Save')
                self.dbHistoryStatus.config(fg='red')

            self.serverVar.set(f'A:{mongo}')
            color = 'red' if  mongo=='Offline' else 'green'
            self.serverStatus.config(fg=color)
            time.sleep(3)

    def showBtnPage(self,n):
        self.pageVar.set(f'{n+1} / {self.maxPage}')
        for btn in self.buttons:
            btn.destroy()
        self.buttons = []
        for i,rtName in enumerate(self.master.enabledRoutine[n*4:n*4+4]):
            r = i//2
            c = i%2            
            btn = tk.Button(self,text=self.master.routine[rtName].btnName,font=('Arial',55),command=self.master.startRoutineCb(rtName))
            btn.place(x=20 + c*400,y=40+170*r,height=150,width=360)
            self.buttons.append(btn)

    def prevPage(self):
        self.currentPage -= 1
        self.showBtnPage(self.currentPage)
        if self.currentPage==0:
            self.prevBtn['state'] = 'disabled'
        if self.currentPage < self.maxPage -1:
            self.nextBtn['state'] = 'normal'

    def nextPage(self):
        self.currentPage +=1
        self.showBtnPage(self.currentPage)
        if self.currentPage==self.maxPage-1:
            self.nextBtn['state'] = 'disabled'
        if self.currentPage > 0:
            self.prevBtn['state'] = 'normal'
    
    def showPage(self):
        self.tkraise()
        self.focus_set()

