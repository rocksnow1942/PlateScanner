from datetime import datetime , timezone
from . import Routine
# import requests


class PatientAccession(Routine):
    _pages =['AccessionPage']
    _titles =['Scan QR Code']
    btnName='Accession'
    requireAuthorization = 'reception'
    def saveResult(self):
        result = self.pages[0].result
        
        # saving patient ID should be removed in the future if we don't want to save patient information.
        # this information is not used in the following process.
        
        # yield 'Saving patient ID to databse...'
        # res = self.master.db.post('/patients',json=[result])
        # if res.status_code == 200:
        #     self.info(f'Saved patient {result.get("name","no name")} - {result["extId"]} to database.')
        #     yield 'Patient ID saved successfully.'
        # else:
        #     self.error(f'{res.status_code},PatientAccession.saveResult Patient ID server response  json:{res.json()}')
        #     raise RuntimeError('Patient ID saving error')      
        
        
        yield 'Saving sample ID to database...'
        sampleId = result['sampleIds'][0]
        # save one sample to samples collection
        res = self.master.db.post('/samples/addOneSample',
            json={'sampleId':sampleId,"extId":result['extId'], 
                    "meta":{ "name": result['name'] } ,
                    "collected":datetime.now(timezone.utc).isoformat() 
                    })
        if res.status_code == 200:
            self.info(f'Saved Sample {sampleId} to database.')
            yield 'Sample ID saved successfully.'
        else:
            self.error(f'Save Sample error: {res.status_code}, {sampleId} PatientAccession.saveResult server response, json:{res.json()}')
            raise RuntimeError('Sample ID saving error')
        

    def validateResult(self,code):
        "validate the barcode code scanned."
        valid = self.master.validator(code,'sample')
        if not valid:
            return False, 'Invalid sample barcode, rescan.'
        return True,''
        
        # to validate if the barcode is already in database:
        # notExist = self.master.validateInDatabase(code,'sample','not-exist')
        # if notExist:
        #     return True,''
        # elif notExist is None:
        #     return False,"Mongo Server is down. Can't validate barcode."
        # else:
        #     return False, "Barcode already exists mongo server."

