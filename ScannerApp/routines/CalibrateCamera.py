from . import Routine
from datetime import datetime
import os
from ..utils import mkdir

class CalibrateCamera(Routine):
    """
    This routine is to read a plate with barcode,
    then read the sample tubes on the plate,
    the samples read are not verified against anything.
    then save the result to a flat txt file.    
    """
    _pages = ['CalibratePage']
    _msgs = ['Calibrate Camera']
    btnName = 'Calibrate'
    def __init__(self, master):
        super().__init__(master)        
        self.tubes = []

    @property
    def plateId(self):
        "the plate ID is used for DTMX page to save snap shot."        
        return f'Calibrate'

    def validateResult(self,code):        
        valid = [self.master.validate(i,codeType='sample') for _,i in code]
        self.tubes = code
        return valid,'',True


