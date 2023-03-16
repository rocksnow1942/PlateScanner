# pip install --upgrade firebase-admin

# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import firestore

# cred = credentials.ApplicationDefault()
# cred = credentials.Certificate('path/to/serviceAccount.json')

# firebase_admin.initialize_app(cred)
# db = firestore.client()

defaultConfig = {
    "appConfig": {
        # "databaseURL": "http://192.168.1.200:8001",
        # "databaseURL": "http://localhost:27017",
        "databaseURL": "https://sa-east-1.aws.data.mongodb-api.com/app/data-wqmut/endpoint/data/v1",
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