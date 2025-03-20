from __future__ import annotations

from typing import Annotated, Literal, Union, Optional

from pydantic import BaseModel, ConfigDict, Field

import pandas as pd
from holisticai.utils import ConditionalImportances, Importances, PartialDependence
from numpy.typing import ArrayLike, NDArray

# Eficacy


class BinaryClassificationEfficacyMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["binary_classification"] = "binary_classification"
    vertical: Literal["efficacy"] = "efficacy"
    y_true: Optional[ArrayLike] = None
    y_pred: Optional[ArrayLike] = None 
    y_prob: Optional[ArrayLike | NDArray] = None


class MultiClassificationEfficacyMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["multi_classification"] = "multi_classification"
    vertical: Literal["efficacy"] = "efficacy"
    y_true: Optional[ArrayLike] = None
    y_pred: Optional[ArrayLike] = None 
    y_prob: Optional[ArrayLike | NDArray] = None



class RegressionEfficacyMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["regression"] = "regression"
    vertical: Literal["efficacy"] = "efficacy"
    y_true: Optional[ArrayLike] = None
    y_pred: Optional[ArrayLike] = None 


class ClusteringEfficacyMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["clustering"] = "clustering"
    vertical: Literal["efficacy"] = "efficacy"
    x: Optional[pd.DataFrame] = None
    y_pred: Optional[ArrayLike] = None


EfficacyMetricEntry = Annotated[
    Union[
        BinaryClassificationEfficacyMetricEntry,
        MultiClassificationEfficacyMetricEntry,
        RegressionEfficacyMetricEntry,
        ClusteringEfficacyMetricEntry,
    ],
    Field(discriminator="learning_task"),
]

# Bias


class BinaryClassificationBiasMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    vertical: Literal["bias"] = "bias"
    learning_task: Literal["binary_classification"] = "binary_classification"
    y_true: Optional[ArrayLike] = None
    y_pred: Optional[ArrayLike] = None
    x: Optional[ArrayLike] = None
    group_a: Optional[ArrayLike] = None
    group_b: Optional[ArrayLike] = None


class MultiClassificationBiasMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    vertical: Literal["bias"] = "bias"
    learning_task: Literal["multi_classification"] = "multi_classification"
    y_true: Optional[ArrayLike] = None
    y_pred: Optional[ArrayLike] = None
    x: Optional[ArrayLike] = None
    group_a: Optional[ArrayLike] = None
    group_b: Optional[ArrayLike] = None


class RegressionBiasMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    vertical: Literal["bias"] = "bias"
    learning_task: Literal["regression"] = "regression"
    y_true: Optional[ArrayLike] = None
    y_pred: Optional[ArrayLike] = None
    x: Optional[ArrayLike] = None
    group_a: Optional[ArrayLike] = None
    group_b: Optional[ArrayLike] = None


class ClusteringBiasMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    vertical: Literal["bias"] = "bias"
    learning_task: Literal["clustering"] = "clustering"
    y_pred: Optional[ArrayLike] = None
    x: Optional[ArrayLike] = None
    group_a: Optional[ArrayLike] = None
    group_b: Optional[ArrayLike] = None


BiasMetricEntry = Annotated[
    Union[
        BinaryClassificationBiasMetricEntry,
        MultiClassificationBiasMetricEntry,
        RegressionBiasMetricEntry,
        ClusteringBiasMetricEntry
    ],
    Field(discriminator="learning_task"),
]

# Explainability

class BinaryClassificationExplainabilityMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["binary_classification"] = "binary_classification"
    vertical: Literal["explainability"] = "explainability"
    y_pred: Optional[ArrayLike] = None
    surrogate_importances: Optional[Importances]=None
    #surrogate_conditional_importances: ConditionalImportances
    y_surrogate: Optional[ArrayLike] = None
    y_prob_surrogate: Optional[ArrayLike] = None
    permutation_importances: Optional[Importances]=None
    permutation_conditional_importances: Optional[ConditionalImportances]=None
    permutation_partial_dependencies: Optional[PartialDependence | list[PartialDependence]]=None


class MultiClassificationExplainabilityMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["multi_classification"] = "multi_classification"
    vertical: Literal["explainability"] = "explainability"
    y_pred: Optional[ArrayLike] = None
    surrogate_importances: Optional[Importances]=None
    #surrogate_conditional_importances: ConditionalImportances
    y_surrogate: Optional[ArrayLike] = None
    y_prob_surrogate: Optional[ArrayLike] = None
    permutation_importances: Optional[Importances]=None
    permutation_conditional_importances: Optional[ConditionalImportances]=None
    permutation_partial_dependencies: Optional[PartialDependence | list[PartialDependence]]=None


class RegressionExplainabilityMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["regression"] = "regression"
    vertical: Literal["explainability"] = "explainability"
    y_pred: Optional[ArrayLike] = None
    surrogate_importances: Optional[Importances]=None
    #surrogate_conditional_importances: ConditionalImportances
    y_surrogate: Optional[ArrayLike] = None
    permutation_importances: Optional[Importances]=None
    permutation_conditional_importances: Optional[ConditionalImportances]=None
    permutation_partial_dependencies: Optional[PartialDependence | list[PartialDependence]]=None

class ClusteringExplainabilityMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["clustering"] = "clustering"
    vertical: Literal["explainability"] = "explainability"
    y_pred: Optional[ArrayLike] = None

ExplainabilityMetricEntry = Annotated[
    Union[
        BinaryClassificationExplainabilityMetricEntry,
        MultiClassificationExplainabilityMetricEntry,
        RegressionExplainabilityMetricEntry,
        ClusteringExplainabilityMetricEntry
    ],
    Field(discriminator="learning_task"),
]


# Security


class BinaryClassificationSecurityMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["binary_classification"] = "binary_classification"
    vertical: Literal["security"] = "security"
    x_train: Optional[pd.DataFrame] = None
    x_test: Optional[pd.DataFrame] = None
    y_train: Optional[ArrayLike] = None
    y_test: Optional[ArrayLike] = None
    y_pred_train: Optional[ArrayLike] = None
    y_pred_test: Optional[ArrayLike] = None
    y_pred_test_dm: Optional[list[dict]] = None
    attack_attribute: Optional[str] = None


class MultiClassificationSecurityMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["multi_classification"] = "multi_classification"
    vertical: Literal["security"] = "security"
    x_train: Optional[pd.DataFrame] = None
    x_test: Optional[pd.DataFrame] = None
    y_train: Optional[ArrayLike] = None
    y_test: Optional[ArrayLike] = None
    y_pred_train: Optional[ArrayLike] = None
    y_pred_test: Optional[ArrayLike] = None
    y_pred_test_dm: Optional[list[dict]] = None
    attack_attribute: Optional[str] = None


class RegressionSecurityMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["regression"] = "regression"
    vertical: Literal["security"] = "security"
    x_train: Optional[pd.DataFrame] = None
    x_test: Optional[pd.DataFrame] = None
    y_train: Optional[ArrayLike] = None
    y_test: Optional[ArrayLike] = None
    y_pred_train: Optional[ArrayLike] = None
    y_pred_test: Optional[ArrayLike] = None
    y_pred_test_dm: Optional[list[dict]] = None
    attack_attribute: Optional[str] = None


class ClusteringSecurityMetricEntry(BaseModel):
    pass

SecurityMetricEntry = Annotated[
    Union[
        BinaryClassificationSecurityMetricEntry,
        MultiClassificationSecurityMetricEntry,
        RegressionSecurityMetricEntry,
        ClusteringSecurityMetricEntry
    ],
    Field(discriminator="learning_task"),
]


# Robustness

class AdversarialAttackerOutput(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    attacker_name: Literal["HSJ", "Zoo"]
    y_adv_pred: Optional[ArrayLike] = None
    adv_x: Optional[pd.DataFrame] = None


class BinaryClassificationRobustnessMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["binary_classification"] = "binary_classification"
    vertical: Literal["robustness"] = "robustness"
    x_test: Optional[pd.DataFrame] = None
    y_test: Optional[ArrayLike] = None
    y_pred_test: Optional[ArrayLike] = None
    zoo_attacks_data: Optional[AdversarialAttackerOutput] = None
    hsj_attacks_data: Optional[AdversarialAttackerOutput] = None


class MultiClassificationRobustnessMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["multi_classification"] = "multi_classification"
    vertical: Literal["robustness"] = "robustness"
    x_test: Optional[pd.DataFrame] = None
    y_test: Optional[ArrayLike] = None
    y_pred_test: Optional[ArrayLike]= None
    zoo_attacks_data: Optional[AdversarialAttackerOutput]=None
    hsj_attacks_data: Optional[AdversarialAttackerOutput]=None


class RegressionRobustnessMetricEntry(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_task: Literal["regression"] = "regression"
    vertical: Literal["robustness"] = "robustness"
    x_test: Optional[pd.DataFrame] = None
    y_test: Optional[ArrayLike] = None
    y_pred_test: Optional[ArrayLike] = None
    zoo_attacks_data: Optional[AdversarialAttackerOutput] = None
    hsj_attacks_data: Optional[AdversarialAttackerOutput] = None


class ClusteringRobustnessMetricEntry(BaseModel):
    pass

RobustnessMetricEntry = Annotated[
    Union[
        BinaryClassificationRobustnessMetricEntry,
        MultiClassificationRobustnessMetricEntry,
        RegressionRobustnessMetricEntry,
        ClusteringRobustnessMetricEntry
    ],
    Field(discriminator="learning_task"),
]
