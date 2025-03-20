from holisticai_sdk.engine.definitions import (
    HAIModel,
    SecurityMetricEntry,
    MetricEntry,
    LearningMetric,
    DatasetTypes,
    SecuritySettings
)

from holisticai_sdk.engine.metrics.utils import convert_to_holisticai_proxy
from holisticai.security.commons import DataMinimizer


def get_metric_entry(model: HAIModel, train: DatasetTypes, test: DatasetTypes, learning_metrics: list[LearningMetric], settings:SecuritySettings, data_minimizer:DataMinimizer)->SecurityMetricEntry:
    entry_names =[param for metric in learning_metrics for param in metric.entry_params]
    obj = get_entry_params(entry_names, model, train, test, settings, data_minimizer)
    return MetricEntry(vertical="security", learning_task=model.learning_task, obj=obj)


def get_entry_params(entry_params: list[str], model: HAIModel, train: DatasetTypes, test: DatasetTypes, settings: SecuritySettings, data_minimizer: DataMinimizer):
    hai_proxy = convert_to_holisticai_proxy(model)
    entry_kargs = {}
            
    for param in entry_params:

        if test.learning_task != "clustering":
            result = process_test_param(param, test, hai_proxy, data_minimizer, train)
            if result is not None:
                entry_kargs[param] = result

        if train.learning_task != "clustering":
            result = process_train_param(param, train, hai_proxy)
            if result is not None:
                entry_kargs[param] = result
 
        if param == "attack_attribute":
            entry_kargs[param] = settings.attack_attribute

        if param not in entry_kargs and param != "attack_attribute":
            raise NotImplementedError(f"El parámetro {param} no está implementado.")

    return entry_kargs


def process_test_param(param, test, hai_proxy, data_minimizer, train):
    match param:
        case "x_test":
            return test.X
        case "y_test":
            return test.y_true
        case "y_pred_test":
            output = hai_proxy.predict(test.X)
            return output
        case "y_pred_test_dm":         
            data_minimizer.proxy = hai_proxy
            output = data_minimizer.predict(test.X)
            return output
            
        case _:
            return None

def process_train_param(param, train, hai_proxy):
    match param:
        case "x_train":
            return train.X
        case "y_train":
            return train.y_true
        case "y_pred_train":
            return hai_proxy.predict(train.X)
        case _:
            return None