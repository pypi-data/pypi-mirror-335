from holisticai_sdk.assessments.model_context import ModelContext, Model
from holisticai_sdk.assessments.environment import submit_assessment_in_env
import warnings
import pandas as pd
warnings.filterwarnings("ignore", category=FutureWarning)

class QuantitativeAssessment(ModelContext):
    """
    Base class for all assessments.
    """

    @classmethod
    def from_config(
        cls,
        config: dict,
    ) -> "QuantitativeAssessment":
        return cls(model=Model(**config))
    
    def run(self, params: dict, use_virtual_env: bool = False, reset_env: bool = False, just_model: bool = False):
        self.extract_dtype(params["X_test"])
        if use_virtual_env:
            with self:
                return submit_assessment_in_env("hai_qa", self.model, params, client_port=self.port, reset_env=reset_env)
        else:
            from holisticai_sdk.engine.assessment.core import run_assessment                
            return run_assessment(self.model, params, just_model=just_model)


class AssessmentResult:
    def __init__(self, body: list[dict], response: dict, metrics: list[dict]):
        self.body = body
        self.response = response
        self.metrics = metrics

    def result_table(self):
        data_list = []
        for method_entry in self.metrics:
            method = method_entry["method"]
            for metric in method_entry["metrics"]:
                metric_name = metric["name"]
                mean_value = metric["aggregates"][0]["value"]
                target_value = metric.get("target", {}).get("value", None)
                data_list.append({
                    "Method": method,
                    "Metric": metric_name,
                    "Mean Value": mean_value,
                    "Target Value": target_value
                })
        return pd.DataFrame(data_list)

