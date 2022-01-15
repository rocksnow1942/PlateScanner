# 96 Well Plate Scanner App

<img src=./ScannerApp/Images/icon.ico width=100>


## Description

The app works with a WIA compatible 96 well plate scanner on windows.

The specific brand of scanner tested here is [Biobank](http://www.inno-spring.com/pro_easyCapture.html).

<img src=./images/biobank.png width=350>

The scanner app drive the scanner and decodes the datamatrix code on the bottom of the sample tube.

The scanning result is pushed to the server to save the sample plate information.

## How to use
The app only works on Windows PC.

- First install the WIA driver for the scanner. (WIA scanner driver from the manufacturer)

- Install requried python packages `pip install -r requirements.txt`

- Make the app with `python make.py`

- The `Scanner_{version}.exe` file will be in the `/dist` folder.

