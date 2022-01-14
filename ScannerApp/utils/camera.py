import time
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from ..utils import indexToGridName,mkdir
import re
import win32com.client, os
import pythoncom


def onThreadStart(threadIndex):
    pythoncom.CoInitialize()

WIA_COM = "WIA.CommonDialog"
WIA_IMG_FORMAT_PNG = "{B96B3CAF-0728-11D3-9D7B-0000F81EF32E}"

WIA_COMMAND_TAKE_PICTURE="{AF933CAC-ACAD-11D2-A093-00C04F72DC3C}"

def acquire_image_wia(saveas,dpi=300):
    pythoncom.CoInitialize()
    wia = win32com.client.Dispatch(WIA_COM) # wia is a CommonDialog object
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


try:
    from pylibdmtx.pylibdmtx import decode
except ImportError:
    decode = lambda *_,**__:0
try:
    from pyzbar.pyzbar import decode as zbarDecode
except ImportError:
    zbarDecode = lambda *_,**__:0


class Camera():
    def __init__(self,scanConfig,cameraConfig,dmtxConfig,master):
        super().__init__()
        self.loadSettings(scanConfig,cameraConfig)
        self.overlay = None
        
        self.startLiveBarcode = False
        self.dmtxConfig = dmtxConfig
        self.master = master
        self.inZoomState = 0
        self.zoomRegion = [
            (0.0, 0.0, 1.0, 1.0),
            (0.4, 0.4, 0.2, 0.2),
            (0.1, 0.1, 0.2, 0.2),
            (0.1, 0.7, 0.2, 0.2),
            (0.7, 0.1, 0.2, 0.2),
            (0.7, 0.7, 0.2, 0.2),
        ]

    def toggleZoom(self):
        "toggle camera zoom state"
        print('tooogle zoom')
        
        
        
    def start(self,):
        print('camera start')
        

    def stop(self):
        print('camera stop')
        

    def adjustScanWindow(self,dx1=0,dy1=0,dx2=0,dy2=0):
        "change the scan window"
        self._scanWindow = (self._scanWindow[0]+dx1, self._scanWindow[1]+dy1,
                            self._scanWindow[2]+dx2, self._scanWindow[3]+dy2)

    def adjustBrightness(self,vol):
        self.brightness = self.valueInRange(self.brightness + vol,0,100)

    def valueInRange(self, value, minValue=0, maxValue=100):
        return min(max(value, minValue), maxValue)

    def loadSettings(self,config,cameraConfig):
        "load settings from config.ini"
        scanWindow = config['scanWindow']
        scanGrid = config['scanGrid']
        direction = config['direction']
        resW = config['scanResolution'] # picture resultion, width. always maintain 4:3
        previewW = 300  # preview width
        self.resolution = (resW, resW*3//4)
        self.framerate = 24
        # preview window is rotated 90 deg and mirrorred.
        self._previewWindow = (20, 20, previewW, previewW*4//3)
        self._scanGrid = scanGrid
        self.direction = direction  # tube scan from top or bottom.                
        self._scanWindow = scanWindow
        
        

       
    def getColor(self,color):
        return {
            'red':(255, 0, 0, 180),
            'green':(0, 255, 0, 180),
            'blue':(0, 0, 255, 180),
            'yellow':(255, 255, 0, 180),
            'white':(255, 255, 255, 180),
            'black':(0, 0, 0, 180),
            'orange':(255, 165, 0, 180),
            'purple':(255, 0, 255, 180),
            'pink':(255, 192, 203, 180),
            'cyan':(0, 255, 255, 180),
            'brown':(165, 42, 42, 180),
        }.get(color,(10, 10, 10, 180))

    def drawOverlay(self, highlights=[],currentSelection=None):
        """
        highlights is a list of [(idx, color),...]
        """
        print('draw overylan',highlights)
        return

        

    def manualRun(self):
        ""
        while True:
            time.sleep(1)
            action = input("action:\n").strip()
            if action == 's':
                self.snapshot()
            elif action.isnumeric():
                self.drawOverlay(highlights=[int(action)])
            else:
                result = self.scan()
                highlights = []
                for idx, res in enumerate(result):
                    if len(res) != 10 or (not res.isnumeric()):
                        highlights.append(idx)
                self.drawOverlay(highlights)

    def iterWells(self):
        column, row = self._scanGrid
        if self.direction == 'top':
            row = list(range(row))
        elif self.direction == 'bottom':
            row = list(range(row)) # [::-1]
        else:
            raise ValueError("direction must be top or bottom")
        for c in range(column):
            for r in row:
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
        timeout = 300+attempt*1000                
        # return self.devDecode(idx)        
        for panel in panels:
            res = decode(panel, max_count=1)
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
        file = mkdir('snapshot') / f'./{datetime.now().strftime("%H:%M:%S")}.jpeg'
        self.capture(file, format='jpeg')

    def runScan(self,name=None):
        """
        bracket the exposure to find the best exposure
        """
        file = mkdir('dtmxScan') / f'./{name or "noname"}_{datetime.now().strftime("%Y%m%d%H%M%S")}.png'        
        acquire_image_wia(str(file),dpi=400)        
        img = Image.open(file)        
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
        ol = len(oldresult)
        needToRead = [i[0] for i in olderror if i[1] == 'red']
        for idx,panels in enumerate(zip( * [self.yieldPanel(i) for i in images] )):
            label = self.indexToGridName(idx)
            if not self.withinCount(label,needToVerify):              
                # have to return "" for control wells, so that the ID is empty
                # I was using the empty ID as indicator of control wells when parsing results.
                yield ""                            
            elif ol>idx:
                if idx in needToRead: 
                    # p1 = self.decodePanel(panel1,attempt)
                    # p2 = self.decodePanel(panel2,attempt)
                    # if p1==p2:
                    #     yield p1
                    # else:
                    #     yield ""
                    yield self.decodePanel(panels,attempt,idx)
                else: 
                    yield oldresult[idx][1] 
            else:
                yield self.decodePanel(panels,attempt,idx)

    def withinCount(self,label,count,grid=(12,8)):
        "check if a label is within a count from top to bottom, left to right"
        col = int(label[1:])
        row = label[0]
        c = (col-1) * grid[1] + 'ABCDEFGHIJKLMNOPQRST'.index(row)
        return c<count
    
    def translatePoint(self,x,y):
        "map a point xy to preview window corrdinate"
        xo, yo, pw, ph = self._previewWindow
        resolutionX, resolutionY = self.resolution
        pY = int(x * ph / resolutionX) + yo
        pX = int(y * pw / resolutionY) + xo
        return pX,pY
    
    def liveScanBarcode(self,cb=print):
        "use pyzbar to scan"
        self.lastRead = None
        while True:
            time.sleep(0.05)
            self._captureStream.seek(0)
            if not self.startLiveBarcode:
                break
            self.capture(self._captureStream,format='jpeg',) #resize=(c_w,c_h)
            self._captureStream.seek(0)
            img = Image.open(self._captureStream)
            code = zbarDecode(img)
            if code and self.startLiveBarcode:    
                res = code[0].data.decode()
                if res != self.lastRead:
                    cb(res)
                self.lastRead = res                
                pad = Image.new('RGBA',(800,480))
                padDraw = ImageDraw.Draw(pad)
                xy = [self.translatePoint(i.x, i.y) for i in code[0].polygon]
                padDraw.polygon(xy, fill=(0, 0, 0, 0),
                                outline=(0, 255, 0, 205))
                for de in code[1:]:
                    xy = [self.translatePoint(i.x, i.y) for i in de.polygon]
                    padDraw.polygon(xy, fill=(0, 0, 0, 0),
                                    outline=(255, 0, 0, 205))

                if self.overlay:
                    self.remove_overlay(self.overlay)
                    self.overlay = None
                self.overlay = self.add_overlay(pad.tobytes(),size=pad.size, layer=3)
            else:
                if self.overlay:
                    self.remove_overlay(self.overlay)
                    self.overlay = None
                
    def indexToGridName(self, idx):
        return indexToGridName(idx, grid=self._scanGrid, direction=self.direction)

    def gridToIndex(self,r,c):
        """
        covert the (1,3) row column tuple to the index from self.iterWells.
        Because self.iterWells spit out wells in the order of A1,B1,C1,D1,E1,F1,G1,H1,A2,B2,C2,D2,E2,F2,G2,H2...
        And based on whether the direction is top or bottom for the camera, (the physical setup right now only alllows bottom.)
        The grid (row, column) order will be either (0,1),(1,1),(2,1)... or (7,1),(6,1),(5,1)... (assuming 8 row plate)
        So this function convert the (row,column) order to the index in the iterWells, depending on the direction.
        """
        column, row = self._scanGrid
        if self.direction == 'top':
            idx = c * row + r
        else:
            idx = c * row + (row - r - 1)
        return idx





