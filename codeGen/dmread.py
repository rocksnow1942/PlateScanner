from pylibdmtx.pylibdmtx import decode,encode
import cv2
import numpy as np
import matplotlib.pyplot as plt
import glob
imgs = glob.glob('96DM/*.png')





originals = [i[5:15] for i in imgs]


plate = cv2.imread('plate.jpg')

single = cv2.imread('IMG_1008.jpg')

decode(single)

concat = cv2.imread('concat.jpg')

decode(concat)



res = decode(plate)


len(res)

result = []
 



camera = cv2.imread('/Users/hui/Downloads/IMG_1007.jpg')

camera = cv2.imread('./imgs/printer_iphone.jpg')

plt.imshow(camera)

res = decode(camera,timeout=1000)

camera=single

# convert image to grayscale

gray = cv2.cvtColor(camera,cv2.COLOR_BGR2GRAY)
plt.imshow(gray,cmap='gray')


# create threshold to remove backgroud black.
th,threshold = cv2.threshold(gray,220,255,cv2.THRESH_BINARY)

plt.imshow(threshold,cmap='gray')

## (2) Morph-op to remove noise
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11,11))
morphed = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel)

## (3) Find the max-area contour
cnts = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
cnt = sorted(cnts, key=cv2.contourArea)[-1]

## (4) Crop and save it
x,y,w,h = cv2.boundingRect(cnt)
dst = gray[y:y+h, x:x+w]
plt.imshow(dst,cmap='gray')


# convert to black and white
(thresh, im_bw) = cv2.threshold(dst, 160, 255,cv2.THRESH_BINARY)# cv2.THRESH_BINARY | cv2.THRESH_OTSU)
plt.imshow(im_bw,cmap='gray')

# resize to smaller seems to be helpful with reading.
im_bw_resize = cv2.resize(im_bw,(int(im_bw.shape[1]/1),int(im_bw.shape[0]/1)))

plt.imshow(im_bw_resize,cmap='gray')

cv2.imwrite('im_bw_resize1.5.jpg',im_bw_resize)
result = decode(im_bw_resize,timeout=100000,max_count=96)


result = decode(im_bw,timeout=100000,max_count=96)
decode(im_bw)
decode(dst)

def panel_parse(im_bw):
    "read each panel of a black and white image."
    h,w = im_bw.shape
    px = w//12
    py = h//8
    panel_result = []
    for r in range(8):
        for c in range(12):
            panel = im_bw[py*r:py*r+py,px*c:px*c+px]
            p = None
            for ratio in [3,2,1.5]:
                panel_resize = cv2.resize(panel,
                        (int(panel.shape[1]/ratio),int(panel.shape[0]/ratio)))
                res = decode(panel_resize,max_count=1,timeout=3000)
                
                if res and len(res[0].data.decode())==10 and res[0].data.decode().isnumeric():
                    p = res[0].data.decode()
                    break
            panel_result.append(p)
    return panel_result

def show_panel(im_bw,panel,offset=(0,0)):
    r,c = panel
    x,y = offset
    h,w = im_bw.shape
    px = w//12
    py = h//8
    r-=1
    c-=1
    
    panel_img = im_bw[py*r+y:py*r+py+y,px*c+x:px*c+px+x]
    
    plt.imshow(panel_img,cmap='gray')
    return panel_img
    
    
resize_result = panel_parse(im_bw_resize)

im_bw_resize = cv2.resize(im_bw,(int(im_bw.shape[1]/2),int(im_bw.shape[0]/1)))


parse_result = [i and i.data.decode() for i in resize_result]

for i in parse_result:
    if i not in originals:
        print(i)

p1_1 = show_panel(im_bw_resize,panel=(2,9),offset=(0,0))

decode(p1_1,max_count=1)
        
show_panel(im_bw_resize,panel=(8,1))
for r in range(8):
    for c in range(12):
        show_panel(im_bw_resize,panel=(r+1,c+1))
        plt.show()

for i,dres in enumerate(parse_result):
    if dres not in originals:
        print(f'{i//12+1}x{i%12+1} : {dres}=>{originals[i]}')
        
        
        

for i,dres in enumerate(resize_result):
    read = dres and dres.data.decode()
    if read != originals[i]:
        print(f'{i//12+1}x{i%12+1} : {read}=>{originals[i]}')


     