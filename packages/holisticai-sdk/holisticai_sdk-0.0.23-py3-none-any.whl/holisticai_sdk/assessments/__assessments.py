from holisticai_sdk.session import Session
from typing import overload, Literal, List, Optional
from holisticai_sdk.assessments.core import QuantitativeAssessment, AssessmentResult
import os
import json
from typing import Union
from logging import getLogger

logger = getLogger(__name__)

SUPERVISED_LEARNING_TASK = Literal["binary_classification", "multiclass_classification", "regression"]
UNSUPERVISED_LEARNING_TASK = Literal["clustering"]

class Assessment:
    def __init__(self, session: Session, settings: dict):
        self.session = session
        self.settings = settings
        self.qa = QuantitativeAssessment.from_config(config=settings)

    @overload
    def run(self, vertical: Literal["efficacy"], X_train, y_train, X_test, y_test, submit_results: bool=True):
        ...      
    
    @overload
    def run(self, vertical: Literal["efficacy"], X_train, X_test, submit_results: bool=True):
        ...

    @overload
    def run(self, vertical: Literal["bias"], X_train, y_train, X_test, y_test, group_a_train, group_b_train, group_a_test, group_b_test, submit_results: bool=True):
        ...

    @overload
    def run(self, vertical: Literal["bias"], X_train, X_test, group_a_train, group_b_train, group_a_test, group_b_test, submit_results: bool=True):
        ...

    @overload
    def run(self, vertical: Literal["robustness"], X_train, y_train, X_test, y_test, submit_results: bool=True, attack_attributes: Optional[List] = None):
        ...

    def __run(self, **kwargs):
        metrics = self.qa.run(params=kwargs, 
                           just_model=False if self.settings['data_type'] == "train-test" else True,
                           use_virtual_env=self.settings.get("use_virtual_env", False), 
                           reset_env=self.settings.get("reset_env", False))
        return metrics

    def run(self, submit_results: bool=True, **kwargs) -> Union[AssessmentResult, list[dict]]:
        if self.session is None:
            logger.warning("Session is not initialized. Results will not be submitted.")
            submit_results = False
        metrics = self.__run(**kwargs)
        if submit_results:    
            return self.__send_results(metrics)
        else:
            return AssessmentResult(body=None, response=None, metrics=metrics)  
    
    @staticmethod
    def _with_source():
        return (
            f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
            if "GITHUB_ACTIONS" in os.environ and os.environ["GITHUB_ACTIONS"] == "true"
            else "python-sdk"
        )
            
    def __create_body(self, metrics: list[dict]):
        data = {      
            "projectId": self.session.config["projectId"],
            "solutionId": self.session.config["solutionId"],
            "platformEndpoint": self.session.config["api"],
            "clientId": self.session.config["clientId"],
            "moduleId": self.session.config["moduleId"],
            "key": self.session.config['key'],
            "dataFile": "dataFile",
            "targetColumn": "targetColumn",
            "name": self.settings["name"],
            "version": self.settings.get("version", "NA"),  
            "problemType": self.settings["task"],
            "dataType": self.settings["data_type"],
            "comment": self.settings.get("comment", "NA"),
            "source": self._with_source(),
            "metrics": metrics
        }
        return data


    def __send_results(self, metrics: list[dict]):
        import requests, urllib3
        body = self.__create_body(metrics)
        url = f"https://{self.session.config['api']}/assessment-result"

        headers = {
            "x-api-key": self.session.config['key'],
            "Content-Type": "application/json"
        }
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.post(url, data=json.dumps(body), headers=headers, verify=False)

        response.raise_for_status()

        return AssessmentResult(body=body, response=response.json(), metrics=metrics)
