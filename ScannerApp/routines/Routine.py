from ..utils import warnImplement
import time
from ..utils.logger import Logger
import sys

class Routine(Logger):
    "routine template"
    _pages = [] # pages to include. Should the the Name of page class.
    _titles = [] # title on each page
    _msgs = [] # message to display on each page at bottom.
    _colors = [] # color of title on each page.
    btnName = 'Routine' # button Name to display on home page
    requireAuthorization = False # by default, not require authorization
    def __init__(self,master):
        self.master = master
        super().__init__(self.__class__.__name__,
        logLevel=self.master.LOGLEVEL,
        fileHandler=self.master.fileHandler)
       
        self.currentPage = 0
                
    @property
    def totalSampleCount(self):
        warnImplement('Need to implement your own total sample count for DTMX page.',self)
        return 96

    @property
    def pages(self,):
        return [self.master.pages[i] for i in self._pages]
    
    def startRoutine(self):
        "define how to start a routine"
        self.results = [i.resultType() for i in self.pages]
        self.states = [{} for i in self.pages]
        self.showNewPage(None,0)
        
    def returnHomePage(self):
        self.pages[self.currentPage].closePage()
        for p in self.pages:
            p.resetState()
        self.master.showHomePage()

    def prevPage(self):
        cp = self.currentPage
        np = self.currentPage -1
        if self.currentPage == 0:
            self.returnHomePage()
            return
        self.showNewPage(cp,np)
    
    def nextPage(self):
        cp = self.currentPage
        np = self.currentPage + 1
        
        self.showNewPage(cp,np)
        
    def showNewPage(self,cp=None,np=None):
        "close current page and show next page"
            # if the next page already have result stored, update with current stored result.  
        self.currentPage = np
        if cp is not None:
            self.results[cp],self.states[cp] = self.pages[cp].readResultState()
        self.pages[np].setResultState(self.results[np],self.states[np])
        if cp is not None:
            self.pages[cp].closePage()
        kwargs = {i[1:-1]:getattr(self,i)[np] for i in ['_titles','_msgs','_colors'] if getattr(self,i)}
        self.pages[np].showPage(**kwargs)
        
    def validateResult(self,result):
        """
        this method is called by routine's pages when they need to validate result.
        normally return True/False to indicate whether result is valid, 
        a message to display, 
        and whether bypass the error check (for example enable next button).
        """
        warnImplement('validateResult',self)
        return (True, 'validation not implemented',False)

    def displayResult(self):
        "return formatted display of all current results"
        warnImplement('displayResult',self)
        return str(self.results)
    def saveResult(self):
        "save results to database"
        warnImplement('saveResult',self)
        for i in range(5):
            yield 'not implement saveResult'
            time.sleep(0.5)
        yield from self.goHomeDelay(3)
    
    def goHomeDelay(self,seconds):
        "go back to home page after seconds"
        yield f'Return to home page in {seconds} seconds.'
        for i in range(int(seconds)):
            time.sleep(1)
            yield f'Return in {seconds - i}s'
        yield f'Return Home.'
        self.returnHomePage()

    @property
    def isDev(self):
        "by pass validation and go to next page"
        if sys.argv[-1] == '-dev':
            return True
        return False