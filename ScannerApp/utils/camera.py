from io import BytesIO
import time
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from ..utils import indexToGridName,mkdir
import re


class Mock:
    _scanGrid = [12,8]
    direction = 'bottom'
    def __init__(self,*args,**kwargs) -> None:
        pass
    def __getattr__(self, name: str):
        return lambda *_,**__:0
    
    def scanDTMX(self,*args,**kwargs):
        for i in range(12):
            yield f'SK0000{i}'
    def indexToGridName(self, idx):
        return indexToGridName(idx, grid=self._scanGrid, direction=self.direction)
    

try:
    from picamera import PiCamera
except ImportError:
    PiCamera = Mock

try:
    from pylibdmtx.pylibdmtx import decode
except ImportError:
    decode = lambda *_,**__:0
try:
    from pyzbar.pyzbar import decode as zbarDecode
except ImportError:
    zbarDecode = lambda *_,**__:0


class Camera(PiCamera):
    def __init__(self,scanConfig,cameraConfig,dmtxConfig,master):
        super().__init__()
        self.loadSettings(scanConfig,cameraConfig)
        self.overlay = None
        self._captureStream = BytesIO()
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
        self.inZoomState = (self.inZoomState + 1) % len(self.zoomRegion)
        if self.inZoomState:
            if  self.overlay:
                self.remove_overlay(self.overlay)
                self.overlay = None
        else:
            self.drawOverlay()
        self.zoom = self.zoomRegion[self.inZoomState]
        
        
    def start(self,):
        self.startLiveBarcode = True
        self.start_preview(
            fullscreen=False, window=self._previewWindow, hflip=True, rotation=90)

    def stop(self):
        self.startLiveBarcode = False
        if self.overlay:
            self.remove_overlay(self.overlay)
            self.overlay = None
        self.stop_preview()

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
        self.bracketExposureDelta = config['bracketExposure']

        if scanWindow:
            self._scanWindow = scanWindow
        else:
            scanRatio = 0.8
            scanX = (resW * (1-scanRatio) )// 2
            gridSize =( resW * scanRatio) // (self._scanGrid[0]-1)
            scanY = (resW*3/4 - gridSize*(self._scanGrid[1]-1))//2

            self._scanWindow = (scanX, scanY,
                                scanX + gridSize*(self._scanGrid[0]-1),
                                scanY + gridSize*(self._scanGrid[1]-1))
        self.font = ImageFont.truetype("./ScannerApp/utils/arial.ttf", 26)

        for key,value in cameraConfig.items():
            if key == 'brightness':
                value = self.valueInRange(value,0,100)
            setattr(self,key,value)
        # self.brightness = config['brightness']
        # self.contrast = config['contrast']
        # self.sharpness = config['sharpness']
        # self.iso = config['iso']
        # self.shutter_speed = config['shutter_speed']
    
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
        pad = Image.new('RGBA', (800, 480))
        padDraw = ImageDraw.Draw(pad)
        column, row = self._scanGrid
        xo, yo, pw, ph = self._previewWindow
        s1, s2, s3, s4 = self._scanWindow        
        resolutionX, resolutionY = self.resolution
        # because preview is flipped and rotated,
        # the x overlay offset caused by scan window is actually y offset of scan window
        # in preview window, overlay offset caused by scan window in y direction.
        scan_offset_y = (s1 * ph / resolutionX)
        # in preview window, overlay offset caused by scan window in x direction.
        scan_offset_x = (s2 * pw / resolutionY)

        # overlay grid height in preview window, this is actually scan window width.
        gridHeight = ((s3-s1) * ph / resolutionX / (column - 1))
        # overlay grid height in preview window, this is actually scan window height.
        gridWidth = ((s4-s2) * pw / resolutionY / (row - 1))
        gridW_ = gridWidth*0.9//2  # half width of actually drawing box in preview window
        gridH_ = gridHeight*0.9//2  # half width of actually drawing box in preview window
        highlightsDict = dict((idx, color) for idx, color,*_ in highlights)
        
        
        for (c,r) in self.iterWells():            
            idx = self.gridToIndex(r,c)
            fill=(0, 0, 0, 0)
            if idx in highlightsDict:
                outline =  self.getColor(highlightsDict[idx]) #(255, 0, 0, 180)
                width = 3
            else:
                outline = (0, 255, 0, 180)
                width = 1
            posy = c * gridHeight + yo + scan_offset_y
            posx = r * gridWidth + xo + scan_offset_x
            if idx == currentSelection:
                fill = (*outline[0:3],180)
                width = 5                
            padDraw.rectangle([posx-gridW_, posy-gridH_, posx+gridW_, posy+gridH_],
                                fill=fill, outline=outline, width=width)
                        

        # label A1 - H12
        labelY = yo + scan_offset_y - gridH_
        rowIndex = "ABCDEFGHIJKLMNOPQRST"[0:row]
        rowIndex = rowIndex if self.direction == 'top' else rowIndex[::-1]
        for r in range(row):
            posx = r * gridWidth + xo + scan_offset_x
            label = rowIndex[r]
            padDraw.text((posx, labelY), label, anchor='md',
                         font=self.font, fill=(255, 0, 0, 255))
        labelX = xo + scan_offset_x - gridW_ - 5
        for c in range(column):
            posy = c * gridHeight + yo + scan_offset_y
            padDraw.text(
                (labelX, posy), f'{c+1}', anchor='rm', font=self.font, fill=(255, 0, 0, 255))

        if self.overlay:
            self.remove_overlay(self.overlay)
            self.overlay = None
        self.overlay = self.add_overlay(pad.tobytes(), size=pad.size, layer=3)

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
            row = list(range(row))[::-1]
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
        gridWidth = (s3-s1)/(column-1)
        gridHeight = (s4-s2)/(row-1)
        cropW = gridWidth * oversample // 2
        cropH = gridHeight * oversample // 2        
        for (c,r) in self.iterWells():
            posx = c * gridWidth + s1
            posy = r * gridHeight + s2
            yield img.crop((int(posx-cropW), int(posy-cropH), int(posx+cropW), int(posy+cropH)))

    def devDecode(self,idx):
        """
        return some development barcode.
        """
        samples = [
        # the following samples are in AMS DB but havn't received
        'SK00017114', 'SK00017109',
        'SK12345678', 'SK12345679',
        'SK20291092', 'SK82345678',

        # the following samples have conflicts in our database
        'SK00064737', 'SK00105747',
        'SK00105808', 'SK00105819',
        'SK00105827', 'SK00105839',

        # the following samples don't exist
        'SK99912344', 'SK99912345',
        'SK99812344', 'SK99812345',        
        ]
        if idx < len(samples):
            return samples[idx]
        else:
            return ''
        

    def decodePanel(self, panels,attempt=0,idx = 0):
        # decode:
        # timeout is in milliseconds, max_count is how many datamatrix.
        # shape is the size of datamatrix, 10X10 is 0,   12X12 is 1. 14X14 is 2.
        # deviation is how skewed the datamatrix can be.
        # threshold, value 0-100 to threshold image. 
        # gap_size: pixels between two matrix.
        timeout = 300+attempt*1000                
        # return self.devDecode(idx)
        codes = []
        for panel in panels:
            res = decode(panel,timeout=timeout, **self.dmtxConfig)
            if res:
                try:
                    code = res[0].data.decode()
                    if code and self.master.validate(code,'sample'):
                        codes.append(code)
                        if codes.count(code) > 1:
                            return code
                except:
                    continue
        return ''
        
    def snapshot(self,):
        "capture and save a image"
        file = mkdir('snapshot') / f'./{datetime.now().strftime("%H:%M:%S")}.jpeg'
        self.capture(file, format='jpeg')

    def bracketExposure(self,brightness,name=None):
        """
        bracket the exposure to find the best exposure
        """
        time.sleep(0.2)
        old = self.brightness
        self.brightness = self.valueInRange(old+brightness,0,100)
        self._captureStream.seek(0)
        self.capture(self._captureStream, format='jpeg')
        self._captureStream.seek(0)
        img = Image.open(self._captureStream)
        if name:
            file = mkdir('dtmxScan') / f'./{name}_{datetime.now().strftime("%Y%m%d%H%M%S")}.jpeg'
            img.save(file)
        self.brightness = old
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
        images = [
        self.bracketExposure(0),
        self.bracketExposure(self.bracketExposureDelta),        
        self.bracketExposure(-self.bracketExposureDelta),
        ]
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





