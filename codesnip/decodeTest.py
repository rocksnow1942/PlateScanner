from pylibdmtx.pylibdmtx import decode
from PIL import Image 
import time


file = './2.jpeg'
img = Image.open(file)


t0 = time.perf_counter()
res = decode(
img,
timeout = 5000,
gap_size=50,
shrink = 1,
shape = None,
deviation = 90,
threshold = None,
min_edge = None,
max_edge = None,
corrections=None,
max_count = 80
)

print(f'time used: {time.perf_counter()-t0}')


len(res)

for i in res:
    print(i)