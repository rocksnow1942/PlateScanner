from PIL import Image,ImageOps,ImageDraw,ImagePath,ImageFont

img = Image.open('out.png')

img.show()

xy = [(10,20),(50,20),(50,50),(10,50)]

img1 = ImageDraw.Draw(img)

img1.polygon(xy,fill=(0,0,0,0),outline='red')

img.show()





# image overlay
img = Image.open('out.png')
pad = Image.new('RGBA',(
        ((img.size[0] + 31) // 32) * 32,
        ((img.size[1] + 15) // 16) * 16,
        ))
        
pad.paste(img, (0, 0),img)
o = camera.add_overlay(pad.tobytes(),size=img.size, layer=3)




base = Image.new('RGBA',(800,480))

draw = ImageDraw.Draw(base)
font = ImageFont.truetype("arial.ttf", 30)


draw.text((10,10),'Hello',font=font,fill=(255,0,0,255))

_scanGrid = (12,8)
_previewWindow = (30,30,300,400)
_scanWindow = (100,135,1100,765)
resolution = (1200,900)
pad = Image.new('RGBA',(800,480))
padDraw = ImageDraw.Draw(pad)
column,row = _scanGrid
xo,yo,pw,ph = _previewWindow
s1,s2,s3,s4 = _scanWindow
resolutionX, resolutionY = resolution
# because preview is flipped and rotated,
# the x overlay offset caused by scan window is actually y offset of scan window
scan_offset_y = s1 * ph // resolutionX #in preview window, overlay offset caused by scan window in y direction.
scan_offset_x = s2 * pw // resolutionY #in preview window, overlay offset caused by scan window in x direction.

gridHeight = (s3-s1) * ph / resolutionX // (column -1) # overlay grid height in preview window, this is actually scan window width.
gridWidth = (s4-s2) * pw / resolutionY // (row -1)   # overlay grid height in preview window, this is actually scan window height. 
gridW_ = gridWidth*0.9//2 # half width of actually drawing box in preview window
gridH_ = gridHeight*0.9//2 # half width of actually drawing box in preview window
for r in range(row):
    for c in range(column):
        idx = r * column + c
        outline = (0,255,0,180)
        width = 1
        posy = c * gridHeight + yo + scan_offset_y
        posx = r * gridWidth + xo + scan_offset_x
        padDraw.rectangle([posx-gridW_,posy-gridH_,posx+gridW_,posy+gridH_],
                           fill=(0,0,0,0),outline=outline,width=width)
labelY = yo + scan_offset_y - gridH_
for r in range(row):
    posx = r * gridWidth + xo + scan_offset_x
    label = 'ABCDEFGH'[r]
    padDraw.text((posx,labelY),label,anchor='md',font=font,fill=(255,0,0,255))                           
labelX = xo + scan_offset_x - gridW_ - 5
for c in range(column):
    posy = c * gridHeight + yo + scan_offset_y
    padDraw.text((labelX,posy),f'{c+1}',anchor='rm',font=font,fill=(255,0,0,255)) 
                           
pad