from . import Routine
from datetime import datetime
import os
from ..utils import mkdir

class ReadCSV(Routine):
    """
    This routine is to read a plate with barcode,
    then read the sample tubes on the plate,
    the samples read are not verified against anything.
    then save the result to a flat txt file.    
    """
    _pages = ['BarcodePage','DTMXPage','SavePage']
    _msgs = ['Scan barcode on the side of sample plate.',             
             'Click Read to scan sample IDs',             
             'Review the results and click Save']
    btnName = 'To CSV'
    def __init__(self, master):
        super().__init__(master)
        self.plate = None
        self.tubes = []

    @property
    def plateId(self):
        "the plate ID is used for DTMX page to save snap shot."        
        return f'ReadCSV_{self.plate}'

    def validateResult(self,code):
        pageNbr = self.currentPage
        if pageNbr == 0:
            self.plate = code
            return True, f"Plate ID: {code}", False
        elif pageNbr == 1:
            valid = [self.master.validate(i,codeType='sample') for _,i in code]
            self.tubes = code
            return valid,'Manual check before proceed',True


    def displayResult(self):
        valid = [self.master.validate(i,codeType='sample') for _,i in self.tubes]
        msg = [
            f'Plate ID : {self.plate}',
            f"Total valid samples: {sum(valid)} / {len(self.tubes)}",
            "Make sure valid sample # is correct before save."
        ]
        return '\n'.join(msg)
    def saveResult(self):
        yield 'Saving result to ./export folder...'
        file = mkdir('readCSV') / f"{self.plate}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        with open(file,'wt') as f:
            f.write('Well,ID\n')
            f.write('\n'.join(f"{w},{i}" for w,i in self.tubes ))
        yield 'Results saved.'
        yield from self.goHomeDelay(5)
        
        
