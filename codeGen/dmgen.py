from pylibdmtx.pylibdmtx import encode,decode
import random
import cv2
import numpy as np
from PIL import ImageOps,Image
import matplotlib.pyplot as plt
 

def randomCode(N = 96, digits = 10,seed = 42):
    np.random.seed(seed)
    no = (np.random.random(N)*(10**digits)).astype(int)    
    return [(f"{{:0{digits}}}").format(i) for i in no]

def textToDMTX(text,pixel = 600):
    dm = encode(text.encode(),size='12x12')
    o= np.frombuffer(dm.pixels, np.uint8).reshape(dm.width,dm.height,-1)
    return cv2.resize(o,(pixel,pixel),interpolation=cv2.INTER_NEAREST)

def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT,borderValue=(255,255,255))
    return result

def add_border(image,percent):
    row,col = image.shape[:2]    
    mean = cv2.mean(image[row-2:row,0:col])[0]
    return cv2.copyMakeBorder(image, top=int(row*percent),
            bottom=int(row*percent), left=int(col*percent), 
            right = int(col*percent), borderType=cv2.BORDER_CONSTANT,value=[mean,mean,mean])

def imgToGrid(imgs,border=0.33,grid=(12,8)):
    idx = -1
    rows = []
    for r in range(grid[1]):
        cols = []
        for c in range(grid[0]):
            idx += 1
            img = imgs[idx]
            img = add_border(img,border)
            img = rotate_image(img,random.random()*360)
            cols.append(img)
        rows.append(cv2.hconcat(cols))
    return cv2.vconcat(rows)

def codeToGrid(codes,grid=(12,8)):
    rowIndex = "ABCDEFGHIJKLMNOPQRST"[0:grid[1]]
    result = []
    idx = -1
    for r in range(grid[1]):
        for c in range(grid[0]):
            idx += 1
            rowM = rowIndex[r]
            result.append((f"{rowM}{c+1}",codes[idx]))
    return result

def saveCodeGrid(file='./codes.csv',codes = None):
    if codes:
        with open(file,'wt') as f:
            for n,c in codes:
                f.write(f"{n},{c}\n")
        
            



codes = randomCode(96,10,42)

imgs = [textToDMTX(i,320) for i in codes]

plate = imgToGrid(imgs,border=1,grid=(6,4))

cv2.imwrite('out.png',plate)

plt.imshow(plate)

saveCodeGrid(codes=codeToGrid(codes,grid=(6,4)))




