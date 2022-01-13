import tkinter as tk
from threading import Thread
import requests
from ..utils import parseISOTime,convertTubeID
import time
from datetime import datetime,timezone
from . import BaseViewPage


class AccessionPage(BaseViewPage):
    resultType = dict
    # result key consist of:
    # name: patient name, 
    # extId: for booking, is /booking/asdfasdg
    # sampleId: sample Id linked to the patient.
    def __init__(self, parent, master):
        super().__init__(parent, master)
        self.create_widgets()
        self.fb = self.master.firebase
        self.initKeyboard(type='lag',lag=1)
        self.bind("<Button-1>", lambda x:self.focus_set())
        self.lastInputTime = time.time()
        self.patientPageIndex = 0 # the index of currently showing patient search result
        self.patientPage = [] # patient results to show
        self._forget_to_save = False # a tag to indicate user forget to save, then prevent scan any new tube ID.
        

    def create_widgets(self):
        self._msgVar = tk.StringVar()
        self.nameVar = tk.StringVar()        
        self.timeVar = tk.StringVar() 
        self.dobVar = tk.StringVar() # store DOB of user
        self.checkVar = tk.StringVar() # store whether user is checked in
        self.codeVar = tk.StringVar() #store tube barcode         
        self.variables = [self.nameVar,self.timeVar,self.dobVar,self.checkVar,self.codeVar]

        font = ('Arial',30)
        self._msg = tk.Label(self, textvariable=self._msgVar, font=('Arial',20))
        self.name = tk.Entry(self, textvariable=self.nameVar, font=font)
        self.time = tk.Label(self, textvariable=self.timeVar, font=font)
        self.dob = tk.Label(self, textvariable=self.dobVar, font=font)
        self.check = tk.Label(self, textvariable=self.checkVar, font=font)
        self.code = tk.Label(self, textvariable=self.codeVar, font=('Arial',30))
        self.home = tk.Button(self,text='Home',font=('Arial',32),command=self.prevPageCb)
        self.save = tk.Button(self,text='Save',font=('Arial',32),command=self.saveCb)        
        self.search = tk.Button(self,text='Search',font=('Arial',32),command=self.searchCb)
        self.prev = tk.Button(self,text='<',font=('Arial',32),command=self.searchPagerCb(-1))
        self.next = tk.Button(self,text='>',font=('Arial',32),command=self.searchPagerCb(1))

        # plate widgets
        Y_DIS = 63
        Y_START = 20
        X = 20        
        tk.Label(self,text='Name:',font=('Arial',30)).place(x=X,y=Y_START)        
        tk.Label(self,text='DoB:',font=('Arial',30)).place(x=X,y=Y_START+Y_DIS*1)
        tk.Label(self,text='Time:',font=('Arial',30)).place(x=X,y=Y_START+Y_DIS*2)
        tk.Label(self,text='Check In:',font=('Arial',30)).place(x=X,y=Y_START+Y_DIS*3)
        tk.Label(self,text='Sample ID:',font=('Arial',30)).place(x=X,y=Y_START+Y_DIS*4)        
        X+=230
        self.name.place(x=X,y=Y_START,width=500)
        self.dob.place(x=X,y=Y_START+Y_DIS*1)
        self.time.place(x=X,y=Y_START+Y_DIS*2)        
        self.check.place(x=X,y=Y_START+Y_DIS*3)
        self.code.place(x=X,y=Y_START+Y_DIS*4)

        self._msg.place(x=20, y=420, width=760,)
        BY=350
        self.home.place(x=40 , y=BY,  height=60 ,width=130,)
        self.save.place(x=630 , y=BY, height=60, width=130)
        self.search.place(x=330,y=BY, height=60,width=140)
        self.prev.place(x=240,y=BY,height=60,width=60)
        self.next.place(x=500,y=BY,height=60,width=60)

    def searchPagerCb(self,step):
        'generate change result page call back.'
        def cb():
            N = len(self.patientPage)
            nextPage = self.patientPageIndex + step
            if nextPage<0 or nextPage>=N:
                return
            self.patientPageIndex +=step
            self.showPatient(self.patientPage[self.patientPageIndex])
            self.displaymsg(f"Result {self.patientPageIndex+1} / {N}")
        return cb
 
    # def scanlistener(self,e):    
    #     "need to handle the special case in QR code."
    #     char = e.char
    #     if time.time() - self.lastInputTime >1:
    #         # if the last input is more than 1 seconds ago, reset keySequence.
    #         self.keySequence=[]
    #     if char=='\r':
    #         if self.keySequence:
    #             self.keyboardCb(''.join(self.keySequence))
    #         self.keySequence=[]            
    #     else:
    #         self.keySequence.append(char)
    #     self.lastInputTime = time.time()
    #     #return 'break' to stop keyboard event propagation.
    #     return 'break'

    def showPatient(self,data):
        """
        show the patient information from data dictionary to display.
        also update self.result
        self.result format :{
            name: patient Name,
            extId: /booking/docID
            sampleIds:[ list of sample ID ]            
        }

        """
        name = data.get('name','No Name!!!')
        dob = data.get('dob','No DoB')
        self.nameVar.set(name)
        self.dobVar.set(dob)
        if data.get('date',None) and data.get('time',None):
            self.timeVar.set( f"{parseISOTime(data['date']).strftime('%Y-%m-%d')} , {data['time']}" )
        else:
            self.timeVar.set('No appointment time found.')
        if data['checkin']:
            self.checkVar.set('Already Check In.')
        else:
            self.checkVar.set("Not Yet.")
        self.result.update(name=name,extId=data.get('docID'))

    def keyboardCb(self,code):
        "call back when a QR code is scanned."                
        def getInfo():       
             # first check if a tube is already scanned.     
            # if the code is a booking reservation:
            if self._forget_to_save:
                return
            
            if code.startswith('/booking'):
                if self.result.get('sampleIds',None):
                    self.displaymsg('Did you forget to save?','red')
                    self.debug(f'Forget to save triggered. Current result: {self.result}')
                    self._forget_to_save = True
                    return 
                # first reset state.
                self.resetState()
                try:
                    self.displaymsg('Validating with server...','green')
                    res = self.fb.get(f'/booking/info{code}')
                    if res.status_code == 200:
                        data = res.json()
                        self.showPatient(data)
                        self.debug(f'Validate Patient with firebase: {code}')
                        self.displaymsg('Please confirm patient info.','green')                   
                    else:
                        self.error(f"keyboardCb: server response [{res.status_code}], {res.json()}")
                        self.nameVar.set("")
                        self.dobVar.set('')
                        self.timeVar.set('')
                        self.checkVar.set('')                    
                        self.displaymsg(f'Error: [{res.status_code}] {res.json().get("error","No response was returned.[102]")}')
                except requests.ReadTimeout:
                    self.error('keyboarCb: ReadTimeout.')
                    self.displaymsg('Server timeout. Slow internet?','red')
                except requests.ConnectionError as e:
                    self.error(f'keyboarCb: connection error: {e}')
                    self.displaymsg('Connection error. Check Wifi or wait and retry.','red')
                except Exception as e:
                    self.error(f'keyboarCb: Other exception {e}')
                    self.displaymsg('Read QR code error.[200]','red')
            else: 
                # otherwise the code should be tube barcode.
                # and we FORCE_UPPER_CASE for tube IDs
                converted = convertTubeID(code)
                self.codeVar.set(converted)
                valid,msg = self.master.currentRoutine.validateResult(converted)
                if valid:
                    self.save['state'] ='normal'
                    self.displaymsg('Sample Id read. Verify before save.','green')
                    self.result['sampleIds'] = [converted]
                    self.result['company'] = 'online-booking'
                    self.debug(f'Scanned valid tube barcode: {converted}')
                else:
                    self.save['state'] ='disabled'
                    self.displaymsg(msg,'red')
                    
        Thread(target=getInfo).start()

    def showPage(self,*_,**__ ):        
        self.keySequence = []        
        self.tkraise()
        self.focus_set()
        self.displaymsg('Scan QR code to start.')        
        self.save['state'] ='disabled'

    def closePage(self):        
        self.home['state']='normal'
        self.search['state']='normal'
        self.save['state'] ='normal'
        

    def resetState(self):
        for v in self.variables:
            v.set('')        
        self.result = self.resultType()
        self.patientPage = []
        self.patientPageIndex = 0
        self._forget_to_save = False

        
        
    def searchCb(self):
        self.focus_set()        
        name = self.nameVar.get()
        
        if not name.strip():
            self.displaymsg('Enter name to search.' , 'red')
            return

        def search():
            self.resetState()
            self.displaymsg('Searching name...','green')
            self.disableBtn()
            res = self.fb.post('/booking/query',json={"firstName":name,'lastName':""})
            if res.status_code == 200:
                self.patientPage = res.json()
                self.showPatient(self.patientPage[0])
                N = len(self.patientPage)
                self.displaymsg(f'Found {N} matching results. 1/{N}')
            else:
                self.displaymsg(res.json()['error'],'red')
            self.enableBtn()
        
        Thread(target=search).start()

    def enableBtn(self,):
        self.home['state']='normal'
        self.search['state']='normal'
       
    def disableBtn(self):
        self.home['state'] = 'disabled'
        self.save['state'] ='disabled'
        self.search['state'] ='disabled'

    def saveCb(self):
        self.focus_set()
        def save():
            # save self.result
            if self.result.get('extId',None) == None:
                self.displaymsg('Nothing to save. Scan QR code to start.','red')
            elif self.result.get('sampleIds',None) == None:
                self.displaymsg('Scan sample tube ID before save.','red')            
            elif self.checkVar.get() == 'Already Check In.':
                self.displaymsg('This patient already submitted sample.','red')
            else:
                try:
                    # save result to firebase
                    for msg in self.master.currentRoutine.saveResult():
                        self.displaymsg(msg)                    
                    # check this patient in on firestore so that we know he already submitted sample.                     
                    self.displaymsg('Writing back to cloud...')     
                    sampleId = self.result['sampleIds'][0]               
                    res = self.fb.post('/booking/checkin',
                            json={'docID':self.result['extId'],
                                #   use server time to update. 
                                  "collectedAt":datetime.now(timezone.utc).isoformat(), 
                                  'accession_id':sampleId})
                    if res.status_code==200:
                        self.displaymsg('Saved successfully.','green')
                        self.info(f'Saved {sampleId} to firebase successfully.')
                        self.resetState()
                    else:
                        self.error(f'Save {sampleId} to firebase error {res.status_code}.')
                        self.displaymsg('Save result to cloud error.','red')        
                except Exception as e:
                    self.error(f"AccessionPage.saveCb error: {e}")
                    self.displaymsg(f'Error in saving: {str(e)[0:40]}','red')
            self.enableBtn()            
        Thread(target=save).start()
        self.displaymsg('Saving results...','green')
        
        self.disableBtn()


