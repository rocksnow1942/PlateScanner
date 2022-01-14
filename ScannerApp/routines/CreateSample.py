import enum
from . import Routine
from datetime import datetime


class CreateSample(Routine):
    """Scan a rack of samples and store the valid sample tube IDs to database."""
    _pages = ['BarcodePage',"NumberInputPage", 'DTMXPage', 'SavePage']
    _titles = ['Scan Reception Barcode', 'Enter Position of Last Sample',
               'Place Plate on reader', 'Save Sample IDs to database']
    _msgs = ["Scan Reception Barcode", 
                "Enter Position of Last Sample",
            'Click Read to scan sample IDs',
             'Review the results and click Save']
    btnName = 'Create'
    requireAuthorization = 'reception'
    plateTime = None
    @property
    def totalSampleCount(self):
        "return totoal exptected sample count"        
        return self.pages[1].inputValue

    @property
    def plateId(self):
        "the plate ID is used for DTMX page to save snap shot."
        receptionCode = self.results[0]
        return f'createSample-{receptionCode[-6:]}-{self.plateTime}'

    def validateResult(self, result):
        if self.currentPage == 0:
            self.plateTime = datetime.now().strftime('%Y-%m-%d_%H%M%S')
            if self.isDev:
                return True, 'dev mode', True
            res = self.master.db.get('/batch', json={'_id': result})
            if res.status_code == 200:
                return True, 'Batch Reception Barcode Scanned', True
            else:
                return False, 'Batch Reception Barcode is inValid', False
        elif self.currentPage == 2:
            wells = result
            self.toUploadSamples = []
            self.toUpdateSamples = []
            validlist = [('green','valid') if self.master.validate(id, 'sample') else ('red','invalid ID') for (wn, id) in wells]
            idList = [id for (wn,id) in wells]
            for index, (id,validation) in enumerate(zip(idList, validlist)):
                if validation[1] != 'valid':
                    continue
                if idList.count(id) > 1:
                    validlist[index] = ('red','duplicate ID')
                    
                                
            totalValidIDs = validlist.count(('green','valid'))
            toValidateInDB = [id for (index,id) in enumerate(idList) if validlist[index][1] == 'valid']
            res = self.master.db.get(
                '/samples', json={'sampleId': {'$in': toValidateInDB}})
            if res.status_code == 200:
                # samples that is not created by batchDownload, this will mean the sample is already preexist in database.
                conflictSample = []
                validexist = []  # sample created by batchDownlaod
                for s in res.json():
                    # if the sample is not create by appCreated, or if the sample already have a well ID,
                    # that means the sample is already scanned and in our system before.
                    # then this sample is going to have conflict.
                    if s.get('meta', {}).get('from', None) == 'appCreated' and (not s.get('sWell', None)):
                        validexist.append(s.get('sampleId'))
                    else:
                        conflictSample.append(s.get('sampleId'))
                for idx, (wn, id) in enumerate(wells):
                    if validlist[idx][1] != 'valid':
                        continue
                    if id in conflictSample:
                        validlist[idx] = ('purple','DB conflict')
                    elif id not in validexist:
                        validlist[idx] = ('yellow','not in DB')
                nonExistCount = validlist.count(('yellow','not in DB'))
                # possible validate result in the validlist:
                # ('green','valid')  => need to update reception status in DB.
                # ('red','invalid ID')
                # ('red','duplicate ID')
                # ('purple','DB conflict')
                # ('yellow','not in DB')  => need to be uploaded to database
                # the green and yellow are valid samples and need to be uploaded.
                msg = f'{totalValidIDs} / {len(validlist)} valid sample IDs found. \n\
{len(validexist)}  / {len(validlist)} sampleIDs are downloaded from app\n\
{len(conflictSample)} / {len(validlist)} samples have conflict with existing sampleIDs\n\
{nonExistCount} / {len(validlist)} samples are not in our database.'

                self.toUploadSamples = [i for i, v in zip(wells, validlist) if (v[1] == 'not in DB')]
                self.toUpdateSamples = [i for i, v in zip(wells, validlist) if (v[1] == 'valid')]
                
                # can always go next page even if there is conflict.
                return validlist, msg, True
            else:
                return [False]*len(wells), f'Server Response {res.status_code}', False

    def displayResult(self,):
        return f"Valid Sample IDs to Create: {len(self.toUploadSamples)}.\nValid Sample IDs to Update: {len(self.toUpdateSamples)}"

    def saveResult(self):
        username = self.master.currentUser
        receptionCode = self.results[0]
        # don't need 'handler':username in the meta, because when posting, 
        # handler is set by the request header. 
        meta = {"receptionBatchId": receptionCode,}
        
        # valid = self.validatedWells
        valid = [{'sampleId': id, 'receivedAt': datetime.now().isoformat(
        ), 'sWell': wn, 'meta': meta} for (wn, id) in self.toUploadSamples]

        update = [{'sampleId': id, 'receivedAt': datetime.now().isoformat(
        ), 'sWell': wn, 'meta.receptionBatchId': receptionCode, 'meta.handler':username} for (wn, id) in self.toUpdateSamples]
        
        yield f'Saving {len(valid)} samples to database...'

        # update the count of reception in this batch
        res = self.master.db.post(
            '/batch/addsample', json={'id': receptionCode, "count": len(valid) + len(update)})
        if res.status_code == 200:
            yield f"Successfully updated batch reception."
        else:
            error = f'Update batch reception error, response: {res.status_code},{res.json()}'
            yield error
            raise RuntimeError(error)

        if valid:
            res = self.master.db.post('/samples', json=valid)
            if res.status_code == 200:
                yield f'Successfully created {len(valid)} new samples.'
            else:
                error = f"Create Sample error: {res.status_code}, {res.json()}"
                yield error
                raise RuntimeError(error)

        if update:
            res = self.master.db.put('/samples', json=update)
            if res.status_code == 200:
                yield f'Successfully updated {len(update)} samples.'
            else:
                error = f"Update Sample error: {res.status_code}, {res.json()}"
                yield error
                raise RuntimeError(error)

        yield from self.goHomeDelay(3)
