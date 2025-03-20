#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
from pathlib import Path
from typing import NewType
from abc import abstractmethod
RunID = NewType("RunID", int)

MetricType = NewType("MetricType", str)

class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


class Runner:
    def __init__(self, pred: dict):

        if isinstance(pred, dict):
            # Create from dict when posted from API; this
            # is used to create a new PredictorModel
            self.name: str   = pred["name"]
            self.description = pred.get("description", "")
            self.conf        = pred["config"]
            self.metrics     = pred["metrics"]
            self.entry_point = pred["entry_point"]
            self.active = pred.get("active", True)
        else:
            # Create from PredictorModel when loaded from database.
            # This is done when running analysis
            self.id = pred.id
            self.asset = pred.asset
            self.name: str = pred.name
            self.description = "" # conf.description
            self.conf = pred.config
            self.entry_point = pred.entry_point
            self.metrics = pred.metrics
            self.active = pred.active
            if pred.config_file:
                self.model_file = Path(pred.config_file.path).resolve()
                self.out_dir = Path(__file__).parents[0]/"Predictions"
                self.runs = {}

    @abstractmethod
    def newPrediction(self, event)->RunID: ...

    @abstractmethod
    def runPrediction(self, run_id)->bool: ...

    def getMetricList(self)->list:
        return self.metrics

    def activateMetric(self, type, rid=None)->bool:
        return False

    @abstractmethod
    def getMetricData(self, run: RunID, metric: MetricType)->dict: ...
