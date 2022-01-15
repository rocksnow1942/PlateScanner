import base64

icon = open('./icon.ico','rb').read()

encode = base64.b64encode(icon)

with open('icon.py','wt') as f:
    f.write(f'icon = "{(encode.decode())}"')