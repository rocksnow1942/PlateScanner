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

## User config file

User can change custom config with the settings file in the `./exports/userConfig/config.ini` folder.

```
# Config file for plate scanner app.
# Configurations are single line. Use python equivilent syntax for parameter values.
# Save this file in ./exports/userConfig/config.ini to apply settings.
# Each key - value pair need to be single line.


# App overall settings
[appConfig]
# url of internal database server.
databaseURL = 'http://192.168.1.200:8001'

# routines to be shown on the home page as buttons.
routines = ['SampleToLyse','LyseToLAMP','SampleToLyseRetest','SaveStore','FindStore','ValidateSample','CreateSample','ReadCSV']
# 'DeleteSample',

# rules for validate sample tube barcodes and plate barcodes.
[codeValidation]
# Regex format for validate barcode on saliva sample tube.
# for common 10 digits: '^\d{10}$'
# for SK00000000: '^SK\d{8}$'
# for SK00000000 or 12345678: '^(SK)?\d{8}$'
# for SK(k)00000000 or 12345678 or AC12345678: '^(S[Kk]|AC)?\d{8}$'
sampleCodeFormat = '^(S[Kk]|AC)?\d{8}$'

# Rules for the ID for plate barcodes.
# '01' means the barcode can start with 0 o 1.
samplePlateFirstDigit = '01'
lysePlateFirstDigit = '2'
lampN7PlateFirstDigit = '3'
lampRP4PlateFirstDigit = '4'


# configuration for datamatrix decoding algorithm
[dataMatrixConfig]

# shape is dmtx size: 10X10:0, 12X12:1, 14X14:2, 16X16:3; None to ignore size.
# Don't set shape and let app decode for proper shape.
# shape = None means will try to check for all shapes. 
# shape = 1

# max_count is max count of barcods in 1 grid.
# always set it to 1 in our application.
max_count=1

# deviation for dmtx, set to 15 works well.
# ignore this setting is also fine.
# deviation = 15

# time out for decoding each grid in milliseconds
timeout = 3000


# Configure the overall scanning area size and resolution.
[scanConfig]
# the grid size of plate, (column, row)
scanGrid = (12,8)

# the resolution and area of plate in the sanned image. 
# default value should work fine for current settings.
# dpi = 600
# scanWindow = (433,589,1903,2929)

# whether save each scanned image to disk.
# change to True while debugging. Otherwise set to False to save disk space.
saveScanImage = False


# for debug
[debugConfig]
#appMode = 'prod'
#LOGLEVEL = 'debug'
```

## Trouble shoot:
According to [pylibdmtx PyPI](https://pypi.org/project/pylibdmtx/)

You might see `WindowsError: [Error 126] The specified module could not be found`

Here is what you need to do:

        If you see an ugly ImportError when importing pylibdmtx on Windows 
        you will most likely need the Visual C++ Redistributable Packages
        for Visual Studio 2013. Install vcredist_x64.exe if using 64-bit Python, 
        vcredist_x86.exe if using 32-bit Python.

Install the correspoinding file. The exe files are under `install` folder. 
