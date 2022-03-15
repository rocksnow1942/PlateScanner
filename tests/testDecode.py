
from email.mime import image
from PIL import Image
from time import perf_counter
import os
import platform
from pylibdmtx.pylibdmtx import decode
from PIL import ImageEnhance,ImageOps

with open('./result.txt') as f:
    correct = [i for i in f.read().split('\n') if i]
 
def yieldPanel(img):
    """
    yield each panel in a image
    the order is from A1,A2...to H1,H2...
    row first, then column.
    dends on self.direction, 
    the order of row is from 1-8 or 8-1,
    so that the letter order is always from A-H
    """
    oversample = 1
    column, row = (12,8)
    s1, s2, s3, s4 = (433,589,1903,2929)
    gridWidth = (s3-s1)/(row-1)
    gridHeight = (s4-s2)/(column-1)
    cropW = gridWidth * oversample // 2
    cropH = gridHeight * oversample // 2        
    for c in range(column):
        for r in range(row):            
            posx = r * gridWidth + s1
            posy = c * gridHeight + s2
            panel = img.crop((int(posx-cropW), int(posy-cropH), int(posx+cropW), int(posy+cropH)))        
            # panel = ImageEnhance.Contrast(panel).enhance(1.5)
            # panel =ImageEnhance.Contrast(ImageOps.grayscale(panel)).enhance(1.5) 
            panel.save(f'./{c}{r}.png')
            yield panel


file = r"C:\Users\hui\RnD\Users\Hui Kang\SampleToLyse_0100002242.png"

img = Image.open(file)

# decode(image, timeout=None, gap_size=None, shrink=1, shape=None,
#            deviation=None, threshold=None, min_edge=None, max_edge=None,
#            corrections=None, max_count=None)

decodeTimes = []

decodePara =  dict(
timeout=None,
gap_size=None,
shrink=1,
shape=None,
deviation=None,
threshold=10,
min_edge=20,
max_edge=None,
corrections=None, 
max_count=1    
)


for idx,i in enumerate(yieldPanel(img)):    
    start = perf_counter()
    res = decode(i,**decodePara)
    end = perf_counter()
    decodeTimes.append(end-start)        
    if (res and res[0].data.decode()  == correct[idx]):
        pass
    else:
        print('incorrect code:',res and res[0].data.decode())

paraText = ','.join([f'{k}={v}' for k,v in decodePara.items()])
print(f'{paraText} decode times: {sum(decodeTimes):.3f} seconds')


