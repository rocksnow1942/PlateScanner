class GetColorMixin:
    def getColorText(self,plate):
        return f'({self.master.plateColor(plate)[0].capitalize()})'*bool(self.master.plateColor(plate)[0])
    def getColor(self,plate):
        return self.master.plateColor(plate)[1].lower()

from .Routine import Routine
from .SampleToLyse import  SampleToLyse,SampleToLyseRetest
from .LyseToLAMP import     LyseToLAMP
from .FindStore import     FindStore
from .SaveStore import     SaveStore
from .CreateSample import     CreateSample
from .DeleteSample import     DeleteSample
from .ValidateSample import    ValidateSample
from .PatientAccession import    PatientAccession
from .ReadCSV import            ReadCSV
from .CalibrateCamera import CalibrateCamera



Routines = {r.__name__:r for r in [
    SampleToLyse,
    LyseToLAMP,
    FindStore,
    SaveStore,
    CreateSample,
    DeleteSample,
    ValidateSample,
    PatientAccession,
    SampleToLyseRetest,
    ReadCSV,
    CalibrateCamera
]}
 