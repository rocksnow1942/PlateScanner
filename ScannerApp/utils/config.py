defaultConfig = {
    "appConfig": {
        "databaseURL": "http://192.168.1.200:8001",
        "routines": [
            "SampleToLyse",
            "LyseToLAMP",
            "SampleToLyseRetest",
            "SaveStore",
            "FindStore",
            "ValidateSample",
            "CreateSample",
            "ReadCSV"
        ]
    },
    "codeValidation": {
        "sampleCodeFormat": "^(S[Kk])?\\d{8}$",    
        "samplePlateFirstDigit": "01",
        "lysePlateFirstDigit": "2",
        "lampN7PlateFirstDigit": "3",
        "lampRP4PlateFirstDigit": "4"
    },
    "plateColors": {
        "lyse": [
            "blue",
            "blue"
        ],
        "lampN7": [
            "red",
            "red"
        ],
        "lampRP4": [
            "transparent",
            "brown"
        ]
    },
    "dataMatrixConfig": {        
        "max_count": 1,
        "timeout":3000,
    },
    "scanConfig": {
        "scanWindow": (433,589,1903,2929),
        "scanGrid": [
            12,
            8
        ],
        "dpi": 600,
        "saveScanImage": False
    },
    "debugConfig": {
        "appMode": "prod",
        "LOGLEVEL": "debug"
    }
}