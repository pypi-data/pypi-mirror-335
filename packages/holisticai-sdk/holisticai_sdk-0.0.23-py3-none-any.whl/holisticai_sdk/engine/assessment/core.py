from holisticai_sdk.engine.definitions import Dataset, Bootstrapping, BootstrapModelMetrics, LearningTask, Vertical, RobustnessSettings
from holisticai_sdk.engine.models import get_baselines, get_proxy_from_sdk_model
from holisticai_sdk.engine.metrics.efficacy._compute_metrics import efficacy_metrics
from holisticai_sdk.engine.metrics.bias._compute_metrics import bias_metrics
from holisticai_sdk.engine.metrics.robustness._compute_metrics import robustness_metrics
from holisticai_sdk.engine.bootstrap import compute_aggregates_from_bootstrap_metrics
from typing import Literal
from numpy.random import RandomState
from holisticai_sdk.utils.logger import get_logger
from typing import Any
logger = get_logger(__name__)
MAX_SAMPLES = 10000


def get_dataset(task: LearningTask, params: dict, dataset_type: Literal["train", "test"]):
    vertical = params["vertical"]
    match task:
        case "clustering" if vertical == "bias":
            ds = Dataset(learning_task=task, vertical=vertical, X=params[f"X_{dataset_type}"], group_a=params[f"group_a_{dataset_type}"], group_b=params[f"group_b_{dataset_type}"])
        
        case "clustering" if vertical != "bias":
            ds = Dataset(learning_task=task, vertical=vertical, X=params[f"X_{dataset_type}"])

        case _ as task_ if task_!= "clustering" and vertical == "bias":
            ds = Dataset(learning_task=task_, vertical=vertical, X=params[f"X_{dataset_type}"], y_true=params[f"y_{dataset_type}"], group_a=params[f"group_a_{dataset_type}"], group_b=params[f"group_b_{dataset_type}"])

        case _ as task_ if task_!= "clustering" and vertical != "bias":
            ds = Dataset(learning_task=task_, vertical=vertical, X=params[f"X_{dataset_type}"], y_true=params[f"y_{dataset_type}"])

        case _:
            raise NotImplementedError
        
    return ds


def get_baseline_models(task: LearningTask, params: dict):
    logger.info(f"Getting baseline models for task: {task}")
    X_train = params["X_train"]

    if task == "clustering":
        return get_baselines(
            learning_task=task, x=X_train, n_clusters=params["n_clusters"]
        )
    
    y_train = params["y_train"]

    return get_baselines(learning_task=task, x=X_train, y=y_train)
    

def get_proxy(model: Any):
    return get_proxy_from_sdk_model(task=model.task, 
                                    predict_fn=model.predict, 
                                    predict_proba_fn=model.predict_proba,
                                    classes=model.classes,
                                    name=model.name)

def postprocessing(boostrap_metrics):
    updated_metrics = []
    for metric in boostrap_metrics[0]['metrics']:
        if metric['target']['range'] is None:
            lower = None
            upper = None
            continue
        else:
            lower = metric['target']['range'][0]
            upper = metric['target']['range'][1]
        
        value = metric['values'][0]
        if value == float('inf'):
            value = None
            continue
        elif value == float('-inf'):
            value = None
            continue

        updated_metrics.append({
            'name': metric['name'],
            'value': value,
            'targetRange': {
                'lower': lower,
                'upper': upper
            }
        })
    return updated_metrics

def postprocessing_robustness(metrics):
    for i in range(len(metrics[0]['metrics'])):
        metrics[0]['metrics'][i].aggregates[-1]['value'] = -1
    return metrics

def run_assessment(model:Any, params: dict, just_model: bool = False):  
    random_state = params.get("seed", RandomState(42))

    if isinstance(random_state, int):
        random_state = RandomState(random_state)

    test = get_dataset(model.task, params, dataset_type="test")

    hai_model = get_proxy(model)

    baselines = [hai_model]
    
    if not just_model:
        if test.vertical != "bias":
            baselines += get_baseline_models(hai_model.learning_task, params)

    num_bootstraps = 1
    if test.vertical == "bias":
        import functools 
        compute_metrics = functools.partial(bias_metrics, test=test)
    
    elif test.vertical == "efficacy":
        import functools 
        compute_metrics = functools.partial(efficacy_metrics, test=test)
        num_bootstraps = 100

    elif test.vertical == "robustness":
        attack_attributes = params.get("attack_attributes")
        if attack_attributes is not None:
            for attr in attack_attributes:
                if attr not in test.X.columns:
                    raise ValueError(f"Attribute {attr} not found in test data")
        settings = RobustnessSettings(attack_attributes=attack_attributes)
        import functools
        compute_metrics = functools.partial(robustness_metrics, test=test, settings=settings)

    else:
        raise ValueError(f"Vertical {params['vertical']} not supported")

    num_bootstraps = params.get("num_bootstraps", num_bootstraps)
    bootstrapping = Bootstrapping(
        num_bootstraps=num_bootstraps,
        max_samples=MAX_SAMPLES,
        random_state=random_state,
        )

    boostrap_metrics = []
    for model in baselines:
        logger.info(f"Assessing {model.name}...")
        boostrap_metric = BootstrapModelMetrics(model_name=model.name, metrics=compute_metrics(model=model, bootstrapping=bootstrapping))
        boostrap_metrics.append(boostrap_metric)
        
    logger.info("Assessing complete.")
    if test.vertical != "bias":
        metrics = compute_aggregates_from_bootstrap_metrics(boostrap_metrics)
        if test.vertical == "robustness":
            metrics = postprocessing_robustness(metrics)
        return dump_metrics(metrics)
    else:
        return postprocessing(boostrap_metrics)

def dump_metrics(metrics: list[BootstrapModelMetrics]):
    dumped_results = []
    for model in metrics:
        dumped_result = {
            'method':model['model_name'],   
            'metrics':[metric.model_dump() for metric in model['metrics']]
        }
        dumped_results.append(dumped_result)
    return dumped_results
