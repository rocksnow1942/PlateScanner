import cv2
import numpy as np
import glob
import matplotlib.pyplot as plt
import random
imgs = glob.glob('96DM/*.png')


def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(255,255,255))
    return result

def add_border(image,percent):
    row,col = image.shape[:2]    
    mean = cv2.mean(image[row-2:row,0:col])[0]
    return cv2.copyMakeBorder(image, top=int(row*percent),
            bottom=int(row*percent), left=int(col*percent), 
            right = int(col*percent), borderType=cv2.BORDER_CONSTANT,value=[mean,mean,mean])


img = cv2.imread('imgs/printer_iphone.jpg')

cv2.imshow('image',img)


len(imgs)
imgs

rows = []
for r in range(8):
    cols = []
    for c in range(12):
        img = cv2.imread(imgs[r*12+c])
        img = add_border(img,0.33)
        deg = random.random()*360
        imgr = rotate_image(img,deg)
        cols.append(imgr)
    rows.append(cv2.hconcat(cols))

plate = cv2.vconcat(rows)

cv2.imwrite('plate.jpg',plate)


i1 = cv2.imread(imgs[0])
i1 = add_border(i1,0.5)
r1 = rotate_image(i1,23)
plt.imshow(i1)
plt.imshow(r1)
plt.show()

cv2.imwrite('rotate.jpg',r1)

cv2.vconcat()
cv2.hconcat()

imgs
