import requests
from . import Routine




class FindStore(Routine):
    """
    Find a plate from position. if the plate taken out is matching the result,
    will then remove that plate.
    if the plate taken out doesn't match, will try to find the correct position of that plate.
    then prompt user.
    """
    _pages = ['BarcodePage','BarcodePage','SavePage']
    btnName = 'Find'
    def __init__(self, master):
        super().__init__(master)
        self.loc = None
        self.plate = None
    def returnHomePage(self):
        self.loc = None
        self.plate = None
        return super().returnHomePage()

    def validateResult(self, result):
        if self.currentPage == 0:            
            res = self.master.validator.samplePlateExist(result)
            if res is None:
                return False, f'Database Server Error.', False
            elif res == False:
                return False, f"Plate {result} not found,Re-check with Admin / Re-enter", False
            else:
                self.plate = result
                self.loc = res
                return True, f'Plate <{result}> found @ <{res}>',False
        elif self.currentPage == 1:            
            if result == self.plate:
                return True, f"Plate <{result}> matches query <{self.plate}>.", False
            else:
                res = self.master.validator.samplePlateExist(result)
                if res is None:
                    return False, f'Database Server Error.', False
                elif res == False:
                    return False, f"Found:<{result}> not in DB, query:<{self.plate}>,Re-check / Re-scan", False
                else:
                    return False, f'Plate <{result}> should be @ <{res}>, Re-Check',False
    @property
    def _msgs(self):
        return ['Scan Plate barcode or enter plate ID to start',
                f'Take plate from <{self.loc}> and Scan to confirm ID',
                f"Confirm Taking Out <{self.plate}> @ <{self.loc}> by click save"]
    @property
    def _titles(self):
        return ['Enter Plate ID to query',
                f'Take Plate <{self.plate}> from <{self.loc}>',
                f"Confirm Take <{self.plate}> from <{self.loc}>"]

    def displayResult(self):
        return f"Taking Out Plate: {self.plate}\nFrom location:{self.loc}"
    
    def saveResult(self):
        loc = self.loc
        if not loc:
            raise RuntimeError('No location provided.')
        yield f"Removing {self.plate} from {loc}..."
        res = requests.put(self.master.URL + '/store',json={'location':loc,'plateID':""})
        if res.status_code == 200:
            yield f"Removed {self.plate} from {loc}."
        else:
            yield "Save result error."
            raise RuntimeError(f'Save results failed server response {res.status_code},json:{res.json()}')
        yield from self.goHomeDelay(3)


