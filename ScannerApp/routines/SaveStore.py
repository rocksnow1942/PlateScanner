import requests
from . import Routine


class SaveStore(Routine):
    """
    save a sample storage plate to database
    if an empty position is available, will give the new location to store.
    if storage is full, will find the oldese plate and ditch that plate.
    """
    _pages = ['BarcodePage','BarcodePage','SavePage']
    _titles = ['Scan Barcode on Sample Plate','*','Save Plate Storage Location']
    _msgs =['Scan barcode on sample plate.',"*","Review the results then click save."]
    _colors = ['black','red','black']
    btnName = 'Store'
    def __init__(self, master):
        super().__init__(master)
        self.toRemove = None
        self.emptySpot = None
    def validateResult(self, result):
        if self.currentPage == 0:
            
            valid = self.master.validateInDatabase(result,'samplePlate','not-exist')
            if valid is None:
                return False, 'Validation failed, server error.', False
            elif valid:
                # then find an empty spot.
                try:
                    res = requests.get(self.master.URL + '/store/empty')
                    if res.status_code == 200:
                        self.emptySpot = res.json()['location']
                        return True, 'Sample Plate ID valid',False
                    elif res.status_code == 400: # no more empty position
                        res = requests.get(self.master.URL + '/store')
                        if res.status_code == 200:
                            self.toRemove = res.json()[0]['location']
                            return True, 'Sample Plate ID valid',False
                        else:
                            return False, "ID valid, cannot find empty spot", False
                except Exception as e:
                    self.error(f'AddStorageRoutine.validateResult error find empty: {e}')
                    return False, 'Error in looking for empty spot', False
            else:
                return valid, 'Sample plate ID is invalid',False
        elif self.currentPage == 1:
            try:
                res = requests.get(self.master.URL + '/store',json={'plateId':result})
                if res.json() and res.json()[0]['location'] == self.toRemove:
                    return True, 'Discard the sample plate to bioharzard container.',False
                elif res.json():
                    id = res.json()[0]['plateId']
                    loc = res.json()[0]['location']
                    return False, f'Found plate <{id}> @ <{loc}>. Re-check plate location / Re-Scan',False
                else:
                    return False, f"Plate {result} not in database,Re-check with Admin", True
            except Exception as e:
                self.error(f'AddStorageRoutine.validateResult error: {e}')
                return False, f'Error:{e}', False
    def returnHomePage(self):
        self.toRemove = None
        self.emptySpot = None
        return super().returnHomePage()
    def prevPage(self):
        cp = self.currentPage
        if self.toRemove is not None:
            np = self.currentPage - 1
        elif self.emptySpot is not None:
            np = self.currentPage - 2
        else:
            np = cp
        if self.currentPage == 0:
            self.returnHomePage()
            return
        self.showNewPage(cp,np)

    def nextPage(self,):
        cp = self.currentPage
        if self.toRemove is not None:
            np = self.currentPage + 1
        elif self.emptySpot is not None:
            np = self.currentPage + 2
        else:
            np = cp
        self.showNewPage(cp,np)
            
    def showNewPage(self, cp, np):
        self.currentPage = np
        if cp is not None:
            self.results[cp],self.states[cp] = self.pages[cp].readResultState()
        self.pages[np].setResultState(self.results[np],self.states[np])
        if cp is not None:
            self.pages[cp].closePage()
        kwargs = {i[1:-1]:getattr(self,i)[np] for i in ['_titles','_msgs','_colors'] if getattr(self,i)}
        if np == 1: # going to remove page
            kwargs['title'] = f'Remove plate from <{self.toRemove}>'
            kwargs['msg'] = f"Scan the plate removed from {self.toRemove}."
        
        self.pages[np].showPage(**kwargs)

    def displayResult(self):
        if self.emptySpot:
            return f"Place plate at location <{self.emptySpot}>.\nThen click save."
        elif self.toRemove:
            return f"Discard plate at location <{self.toRemove}>.\nPlace new plate at location <{self.toRemove}>.\nThen click save."
        else:
            return  'Unable to find storage location.\nPlease check with administrator.'
    
    def saveResult(self):
        sampleId = self.results[0]
        loc = self.toRemove or self.emptySpot
        if not loc:
            raise RuntimeError(f"Can't store plate <{sampleId}>. No storage location available.")
        yield f'Saving plate {sampleId} to location {loc}...'
        res = requests.put(self.master.URL + '/store',json={'location':loc,'plateId':sampleId,"removePlate":True})
        if res.status_code == 200:
            yield f'Saved plate to location{loc}\nResponse: {res.json()}.'
        else:
            yield "Save plate error."
            raise RuntimeError(f"Save plate failed, server response <{res.status_code}>, json:{res.json()}")
        yield from self.goHomeDelay(3)

