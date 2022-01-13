from pylibdmtx.pylibdmtx import decode
import time

from PIL import Image 

img = Image.open('./camera_croped.jpg')

img = Image.open('./imgs/test1_cropped.png')


import glob
imgs = glob.glob('96DM/*.png')
originals = [i[5:15] for i in imgs]

#because raspberry Pi doesn't have CV2, so cannot do the cropping with openCV.

def decode_panel(panel):
    px,py = panel.size
    p = None
    for size in [100,200]:
        print(size)
        panel_resize = panel.resize((size, int(size*py/px)))
        res = decode(panel_resize,max_count=1)
        
        if res and len(res[0].data.decode())==10 and res[0].data.decode().isnumeric():
            p = res[0].data.decode()
            return p
    return p
    


def panel_parse(im_bw):
    "read each panel of a black and white image."
    w,h = im_bw.size
    px = w//12
    py = h//8
    panel_result = []
    for r in range(8):
        for c in range(12):
            # this si cropping some extra to avoid edge loss.
            panel = im_bw.crop((px*(c -0.1) ,py*(r-0.1),px*(c+1.1),py*(r+1.1),))
            p = decode_panel(panel)
            panel_result.append(p)
    return panel_result

def show_panel(im_bw,panel=(1,1),offset=(0,0)):
    r,c = panel
    x,y = offset
    w,h = im_bw.size
    px = w//12
    py = h//8
    r-=1
    c-=1    
    panel_img = im_bw.crop((px*(c-0.1)+x,py*(r-0.1)+y,px*(c+1.1)+x,py*(r+1.1)+y,))
    return panel_img


show_panel(img,(1,1))

resize_result = panel_parse(img)




if __name__ == '__main__':
    t0 = time.perf_counter()
    resize_result = panel_parse(img)
    t1 = time.perf_counter()

    print(f'Time elasped: {t1-t0:.6f}s')

    for i,dres in enumerate(resize_result):
        if dres not in originals:
            print(f'{i//12+1}x{i%12+1} : {dres}=>{originals[i]}')
         
            
            
            