from ScannerApp import ScannerApp

import base64
import os
from ScannerApp.Images.icon import icon

# get the temp file as icon
icondata= base64.b64decode(icon)
## The temp file is icon.ico
tempFile= ".~icon.ico"
iconfile= open(tempFile,"wb")
## Extract the icon
iconfile.write(icondata)
iconfile.close()


# run app with -dev to avoid authentication page to scan user badge.
# in the config.ini, set appMode to dev or prod to switch between devMode and prodMode
app = ScannerApp()
app.iconbitmap(tempFile)

os.remove(tempFile)

app.protocol('WM_DELETE_WINDOW',app.on_closing)
app.mainloop()
