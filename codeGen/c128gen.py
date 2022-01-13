import matplotlib.pyplot as plt
from barcode import Code128
import cv2
from barcode.writer import ImageWriter
import numpy as np
from io import BytesIO


def randomCode(N = 96, digits = 10,seed = 42):
    np.random.seed(seed)
    no = (np.random.random(N)*(10**digits)).astype(np.int64)    
    return [(f"{{:0{digits}}}").format(i) for i in no]


def textToC128(text,):
    buf = BytesIO()
    c128 = Code128(text,writer=ImageWriter())
    c128.write(buf)
    buf.seek(0)
    filebyte = np.asarray(bytearray(buf.read()),dtype=np.uint8)
    res = cv2.imdecode(filebyte,cv2.IMREAD_GRAYSCALE)
    return np.r_[res[200:220,:],res[0:100,:],res[245:,:],res[200:210,:]]
    
def imgToGrid(imgs,grid=(4,6)):
    idx = -1
    rows = []
    for r in range(grid[1]):
        cols = []
        for c in range(grid[0]):
            idx += 1
            img = imgs[idx]             
            cols.append(img)
        rows.append(cv2.hconcat(cols))
    return cv2.vconcat(rows)

codes = randomCode()

imgs = [textToC128(i) for i in codes]

grid = imgToGrid(imgs,)

cv2.imwrite('C128.png',grid)


plt.imshow(grid,cmap='gray')
 