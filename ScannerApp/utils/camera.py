from PIL import Image
from ..utils import indexToGridName,mkdir

try:
    import win32com.client as w32client
    import pythoncom
except:
    print('No win32com support')
    w32client=None
    pythoncom=None
import os
import platform
if platform.system() == 'Windows':
    from .pylibdmtx.pylibdmtx import decode
else:
    from pylibdmtx.pylibdmtx import decode



WIA_COM = "WIA.CommonDialog"
WIA_IMG_FORMAT_PNG = "{B96B3CAF-0728-11D3-9D7B-0000F81EF32E}"

WIA_COMMAND_TAKE_PICTURE="{AF933CAC-ACAD-11D2-A093-00C04F72DC3C}"

def acquire_image_wia(saveas,dpi=300):
    #return './ScannerApp/utils/devsample.png'
    if pythoncom is None:
        return './ScannerApp/utils/devsample.png'
    pythoncom.CoInitialize()
    wia = w32client.Dispatch(WIA_COM) # wia is a CommonDialog object
    dev = wia.ShowSelectDevice()
    for command in dev.Commands:
        if command.CommandID==WIA_COMMAND_TAKE_PICTURE:
            foo=dev.ExecuteCommand(WIA_COMMAND_TAKE_PICTURE)

    items = list(dev.Items)
    if len(items) == 0:
        raise RuntimeError('No scanner connected.')
    
    item = items[-1]
    for p in item.Properties:
        if not p.IsReadOnly:
            if  'Resolution' in p.Name:
                p.Value = dpi
                
    image=item.Transfer(WIA_IMG_FORMAT_PNG)
        
    if os.path.exists(saveas):
        os.remove(saveas)
    image.SaveFile(saveas)
    return saveas


class Camera():
    def __init__(self,scanConfig,dmtxConfig,master):
        super().__init__()
        self.loadSettings(scanConfig)   
        self.dmtxConfig = dmtxConfig
        self.master = master
        self.scanconfig = scanConfig
        

    def toggleZoom(self):
        "toggle camera zoom state"
        pass
        
        
        
    def start(self,):
        pass
        

    def stop(self):
        pass
        

    def adjustScanWindow(self,dx1=0,dy1=0,dx2=0,dy2=0):
        "change the scan window"
        self._scanWindow = (self._scanWindow[0]+dx1, self._scanWindow[1]+dy1,
                            self._scanWindow[2]+dx2, self._scanWindow[3]+dy2)

    def adjustBrightness(self,vol):
        self.brightness = self.valueInRange(self.brightness + vol,0,100)

    def valueInRange(self, value, minValue=0, maxValue=100):
        return min(max(value, minValue), maxValue)

    def loadSettings(self,config):
        "load settings from config.ini"           
        self._scanGrid = config['scanGrid']        
        self._scanWindow = config['scanWindow']
        self.dpi = config['dpi'] or 400
         

    def iterWells(self):
        column, row = self._scanGrid    
        for c in range(column):
            for r in range(row):
                yield (c, r)


    def yieldPanel(self, img):
        """
        yield each panel in a image
        the order is from A1,A2...to H1,H2...
        row first, then column.
        dends on self.direction, 
        the order of row is from 1-8 or 8-1,
        so that the letter order is always from A-H
        """
        oversample = 1.2
        column, row = self._scanGrid
        s1, s2, s3, s4 = self._scanWindow
        gridWidth = (s3-s1)/(row-1)
        gridHeight = (s4-s2)/(column-1)
        cropW = gridWidth * oversample // 2
        cropH = gridHeight * oversample // 2        
        for idx,(c,r) in enumerate(self.iterWells()):
            posx = r * gridWidth + s1
            posy = c * gridHeight + s2
            panel = img.crop((int(posx-cropW), int(posy-cropH), int(posx+cropW), int(posy+cropH)))
            panel.save( mkdir('panels')/ f'{self.indexToGridName(idx)}.png')
            yield panel


    def decodePanel(self, panels,attempt=0,idx = 0):
        # decode:
        # timeout is in milliseconds, max_count is how many datamatrix.
        # shape is the size of datamatrix, 10X10 is 0,   12X12 is 1. 14X14 is 2.
        # deviation is how skewed the datamatrix can be.
        # threshold, value 0-100 to threshold image. 
        # gap_size: pixels between two matrix.        
        # return self.devDecode(idx)

        for panel in panels:
            res = decode(panel,**self.dmtxConfig)
            if res:
                try:
                    code = res[0].data.decode()
                    if code and self.master.validate(code,'sample'):
                        return code    
                except:
                    continue
        return ''
        
    def snapshot(self,):
        "capture and save a image"
        pass

    def runScan(self,name=None):
        """
        bracket the exposure to find the best exposure
        """
        file = mkdir('dtmxScan') / f'./{name or "noname"}.png'
        saved = acquire_image_wia(str(file),dpi=self.dpi)
        img = Image.open(saved)
        # delete file after open 
        if not self.scanconfig.get('saveScanImage', False):
            os.remove(saved)        
        return img

    

    def scanDTMX(self,olderror=[],oldresult=[],attempt=0,needToVerify=96,plateId=''):
        """
        perform a capture and decode
        olderror is a list of (idx, color, reason) that were invalid.
        reason = 'invalid, conflict, non-exist'
        oldresult is al list of [(A1,Id)...] that contain both valid and invalid results.
        attempt is how many times have been reading the result.
        perform 2 sequential image capture
        """        
        images = [self.runScan(plateId)]        
        oldresultDict = {i[0]:i[1] for i in oldresult}
        for idx,panels in enumerate(zip( * [self.yieldPanel(i) for i in images] )):
            label = self.indexToGridName(idx)
            if not self.withinCount(label,needToVerify):              
                # have to return "" for control wells, so that the ID is empty
                # I was using the empty ID as indicator of control wells when parsing results.
                yield  ""
            else:
                code = self.decodePanel(panels,attempt=attempt,idx=idx)                
                oldCode = oldresultDict.get(label,'')
                if oldCode and code and oldCode != code:
                    # print('new read:',oldCode+'->'+code)
                    previousReads = oldCode.split('->')
                    oldCode = '->'.join(previousReads[-2:])
                    yield oldCode+'->'+code
                    # Or, we can say if there is 2 continuous reads are the same code, we think it is correct?
                    # if previousReads.count(code) > 1:
                    #     yield code
                    # else:
                    #     oldCode = '->'.join(previousReads[-2:])
                    #     yield oldCode+'->'+code
                elif oldCode:
                    yield  oldCode
                else:
                    yield  code

    def withinCount(self,label,count,grid=(12,8)):
        "check if a label is within a count from top to bottom, left to right"
        col = int(label[1:])
        row = label[0]
        c = (col-1) * grid[1] + 'ABCDEFGHIJKLMNOPQRST'.index(row)
        return c<count
    
    
                
    def indexToGridName(self, idx):
        return indexToGridName(idx, grid=self._scanGrid)

    def gridToIndex(self,r,c):
        """
        covert the (1,3) row column tuple to the index from self.iterWells.
        Because self.iterWells spit out wells in the order of A1,B1,C1,D1,E1,F1,G1,H1,A2,B2,C2,D2,E2,F2,G2,H2...
        And based on whether the direction is top or bottom for the camera, (the physical setup right now only alllows bottom.)
        The grid (row, column) order will be either (0,1),(1,1),(2,1)... or (7,1),(6,1),(5,1)... (assuming 8 row plate)
        So this function convert the (row,column) order to the index in the iterWells, depending on the direction.
        """        
        return c * self._scanGrid[1] + r





