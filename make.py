import PyInstaller.__main__
from ScannerApp.__version__ import version

PyInstaller.__main__.run([
    "app.py",
    "--onefile",
    "--noconsole",
    "--clean",
    r'--add-data=.\ScannerApp\utils\pylibdmtx\libdmtx-64.dll;.',    
    r"--icon=.\ScannerApp\Images\icon.ico" ,
    f"--name=Scanner_v{version}.exe",
])