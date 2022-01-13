import time
from pylibdmtx.pylibdmtx import decode
from PIL import Image 

 

imgs = []
for row in 'ABCDEFGH':
    for col in range(1,13):
        file = f"./out/{row}{col}.jpeg"
        img = Image.open(file)
        imgs.append((f"{row}{col}",img))

times = []
for name,img in imgs:
    t0 = time.perf_counter()
    res = decode(
    img,
    timeout = None,
    shrink = 1,
    shape = None,
    deviation = 5,
    threshold = 50,
    min_edge = None,
    max_edge = None,
    corrections=None,
    max_count = 1
    )
    times.append(time.perf_counter()-t0)
    res = res and res[0].data.decode()
    print(f"{name}:{res}")
    
print(f"Average time: {sum(times)/len(times)}")
print(f"Max time: {max(times)}")
print(f"Min time: {min(times)}")