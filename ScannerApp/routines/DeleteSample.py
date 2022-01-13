import requests
from . import Routine


class DeleteSample(Routine):
    "Scan a rack of samples and delete their tube IDs."
    _pages = ['DTMXPage','SavePage']
    _titles = ['Scan Sample Plate barcode','Delete Sample IDs in database']
    _msgs = ['Scan Sample Plate barcode','Review the results and click Save']
    btnName = 'Delete'
    
    @property
    def totalSampleCount(self):
        "return totoal exptected sample count"        
        return 96

    @property
    def plateId(self):
        "the plate ID is used for DTMX page to save snap shot."        
        return f'Delete'

    def validateResult(self, wells):
        validlist = [self.master.validate(id,'sample') for (wn,id) in wells]
        msg = f'{sum(validlist)} / {len(validlist)} valid sample IDs found.'
        return validlist, msg ,True
    
    def displayResult(self,):
        wells = self.results[0]
        total = len(wells)
        valid = [None]
        invalid = [None]
        for (wn,id) in wells:
            if self.master.validate(id,'sample'):
                valid.append(f"{wn} : {id}" )
            else:
                invalid.append(f"{wn} : {id}")
        valid[0] = f"Total Valid Sample IDs: {len(valid)-1} / {total}"
        invalid[0] = f"Total Invalid Sample IDs: {len(invalid)-1} / {total}"
        return '\n'.join(invalid+valid)

    def saveResult(self):
        sampleurl = self.master.URL + '/samples'
        wells = self.results[0]
        valid = [{'sampleId':id} for (wn,id) in wells if self.master.validate(id,'sample')]
        yield f'Deleting {len(valid)} samples in database...'
        res = requests.delete(sampleurl,json=valid)
        if res.status_code == 200:
            yield 'Samples successfully deleted.'
            yield str(res.json())
        else:
            raise RuntimeError(f"Saving error: server respond with {res.status_code}, {res.json()}")
        yield from self.goHomeDelay(3)
