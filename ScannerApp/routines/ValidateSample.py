from ..utils.validators import Sample88_2NTC_3PTC_3IAB
from . import Routine


class ValidateSample(Routine):
    """
    This is to validate all samples on the plate matches existing sample barcode in the database.
    currently forced to validate the 88 sample layout.
    """
    _pages = [  'DTMXPage']
    _titles =  [ 'Place Samples on Reader']
    _msgs = [ 'Click read to start.']
    btnName = 'Validate'

    def __init__(self, master):
        super().__init__(master)
        self.plate = Sample88_2NTC_3PTC_3IAB(self)
    
    @property
    def plateId(self):
        "the plate ID is used for DTMX page to save snap shot."        
        return f'validateSample'

    @property
    def totalSampleCount(self):
        return 96

    def nextPage(self):       
        self.pages[0].resetState()
        self.showNewPage(cp=0, np=0)

    def validateResult(self, result):       
        validlist = [self.master.validate(id, 'sample') for (wn, id) in result]
        if not all(validlist):
            return validlist, 'Not all barcodes read. Keep reading plate.', False
        wells = [i[1] for i in result]
        res = self.master.db.get('/samples', json={'sampleId': {'$in': wells}})
       
        wellLabels = ['Barcode Read ERROR. Mark Down Codes']
        if res.status_code == 200:
            plateIds = {}
            for s in res.json():
                plateIds[s['sampleId']] = s['sWell']
            for idx, (wn, id) in enumerate(result):
                sWell = plateIds.get(id,  None)
                if  sWell!=wn:
                    validlist[idx] = False
                    wellLabels.append(f"Wrong {wn} = {id}")
            if all(validlist):
                return validlist, 'All barcodes are valid.', True
            else:

                return validlist, '\n'.join(wellLabels), True
        else:
            return [False]*len(wells), f'Server Response {res.status_code}', False
