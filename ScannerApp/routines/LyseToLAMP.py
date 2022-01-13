import requests
from ..utils.validators import n7PlateToRP4Plate
from . import Routine,GetColorMixin


class LyseToLAMP(Routine,GetColorMixin):
    """This routine transfer samples after lyse to lamp reaction plate.
    First scan the sample lyse plate, then scan the N7 primer plate, then scan the RP4 primer plate.
    then the lyse plate in dabase will be updated with N7 primer plate barcode,
    a new plate for RP4 reaction is created.
    """
    _pages = ['BarcodePage','BarcodePage','BarcodePage',"SavePage"]    
    _msgs = ['Scan barcode on the side of lyse plate.',
        'Scan barcode on the side of LAMP-N7 plate',
        'Scan barcode on the side of LAMP-RP4 plate',
        'Review results and click save']
    btnName = 'Plate'
    requireAuthorization = 'testing'
    @property
    def _titles(self):
        return [f'Scan Barcode On Lyse Plate {self.getColorText("lyse")}',
        f'Scan Barcode On LAMP-N7 Plate {self.getColorText("lampN7")}',
        f'Scan Barcode On LAMP-RP4 Plate {self.getColorText("lampRP4")}',
        'Save Linked Plates']

    @property
    def _colors(self):
        return [self.getColor('lyse'),self.getColor('lampN7'),self.getColor('lampRP4'),'black']

    def displayResult(self):
        return f"Lyse plate: {self.results[0]} \nLAMP-N7 plate: {self.results[1]}\nLAMP-RP4 plate: {self.results[2]}"

    def saveResult(self):
        lyseId = self.results[0]
        n7Id = self.results[1]
        rp4Id = self.results[2]
        # save reulsts to server here:        
        yield 'Start saving...'
        
        res = self.master.db.put('/plates/link',json={'oldId':lyseId,'step':'lamp','newId':n7Id,'companion':rp4Id}) 
        if res.status_code == 200:
            yield 'LAMP - N7 plate updated.'
        else:
            self.error(f'LyseToLAMP.saveResult server response <{res.status_code}>@N7: json: {res.json()}')
            raise RuntimeError(f'Server respond with {res.status_code} when saving LAMP-N7 plate.')
        rp4doc = res.json()
        rp4doc.update(companion=n7Id,plateId=rp4Id,wells=n7PlateToRP4Plate(rp4doc['wells']),layout=rp4doc['layout']+'-RP4Ctrl')
        
        res = self.master.db.post('/plates',json=rp4doc)
        if res.status_code == 200:
            yield 'LAMP - RP4 plate saved.'
        else:
            self.error(f'LyseToLAMP.saveResult server response <{res.status_code}>@RP4: json: {res.json()}')
            raise RuntimeError(f'Server respond with {res.status_code} when saving LAMP-RP4 plate.')
        yield from self.goHomeDelay(5)

    def validationResultParse(self,valid,name):
        if valid is None: # server error
            return False, 'Validation failed, server error.', False
        else:
            return valid, f'{name.capitalize()} plate ID is ' + ('valid' if valid else 'invalid'),False


    def validateResult(self, result):
        page = self.currentPage
        if page == 0:
            valid = self.master.validateInDatabase(result,'lyse','exist')
            return self.validationResultParse(valid,'lyse')
        elif page == 1:
            valid = self.master.validateInDatabase(result,'lampN7','not-exist')
            return self.validationResultParse(valid,'LAMP-N7')
        elif page == 2:
            valid = self.master.validateInDatabase(result,'lampRP4','not-exist')
            return self.validationResultParse(valid,'LAMP-RP4')
