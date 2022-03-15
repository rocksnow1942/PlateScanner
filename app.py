from ScannerApp import ScannerApp
import platform
import base64
import os
from ScannerApp.Images.icon import icon

isRunningOnPi = platform.platform().startswith('Linux')

# raspberry pi running with script and cannot load icon
if not isRunningOnPi:
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

if not isRunningOnPi:
    app.iconbitmap(tempFile)
    os.remove(tempFile)

app.protocol('WM_DELETE_WINDOW',app.on_closing)
app.mainloop()
