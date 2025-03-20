from functools import partial
import threading
from xmlrpc.server import SimpleXMLRPCServer
import numpy as np
import pandas as pd
from typing import Optional, Callable
from holisticai_sdk.utils.logger import get_logger

logger = get_logger(__name__)

class Model:
    def __init__(self, 
                 task: str, 
                 predict_fn: Callable, 
                 predict_proba_fn: Optional[Callable]=None, 
                 classes: Optional[list]=None, 
                 n_clusters: Optional[int]=None,
                 **kwargs):
        self.name = "User Model"
        self.task = task
        self.classes = classes
        self.predict_proba = predict_proba_fn
        self.predict = predict_fn
        self.n_clusters = n_clusters
        self.kwargs = kwargs
        
    @classmethod
    def from_remote(cls, task: str, server_url: str, has_probabilities: bool, classes: Optional[list]=None, n_clusters: Optional[int]=None) -> "Model":
        import xmlrpc.client
        
        proxy = xmlrpc.client.ServerProxy(server_url, allow_none=True)

        def predict_fn(input_data):
            try:
                if isinstance(input_data, pd.DataFrame):
                    # Convertir el DataFrame a dict y forzar que las claves sean strings
                    input_data = {str(key): value for key, value in input_data.to_dict(orient="list").items()}
                
                elif isinstance(input_data, np.ndarray):
                    input_data = input_data.tolist()

                else:
                    raise ValueError("Input data must be a pandas DataFrame or a numpy array")
                
                prediction = proxy.predict(input_data)
                
                return prediction

            except Exception as e:
                raise Exception("Error communicating with the server:", str(e))


        if has_probabilities:
            def predict_proba_fn(input_data):
                try:
                    if isinstance(input_data, pd.DataFrame):
                        # Convertir el DataFrame a dict y forzar que las claves sean strings
                        input_data = {str(key): value for key, value in input_data.to_dict(orient="list").items()}
                    
                    elif isinstance(input_data, np.ndarray):
                        input_data = input_data.tolist()

                    else:
                        raise ValueError("Input data must be a pandas DataFrame or a numpy array")
                    
                    prediction = proxy.predict_proba(input_data)    
                    return prediction

                except Exception as e:
                    raise Exception("Error communicating with the server:", str(e))
            return cls(task=task, predict_fn=predict_fn, predict_proba_fn=predict_proba_fn, classes=classes, n_clusters=n_clusters)
        
        return cls(task=task, predict_fn=predict_fn, classes=classes, n_clusters=n_clusters)
    
    def get_metadata(self):
        return {
            "task": self.task,
            "classes": self.classes,
            "n_clusters": self.n_clusters,
            "has_probabilities": self.predict_proba is not None
        }
    

class ModelContext:
    def __init__(self, model: Model, port: int = 8000):
        self.model = model
        self.server = None
        self.server_thread = None
        self.port = port

    def encode(self, input_data):
        if isinstance(input_data, pd.DataFrame):
            return input_data.to_dict(orient="list")
        if isinstance(input_data, np.ndarray):
            return input_data.tolist()
        return input_data
    
    def decode(self, input_data, dtype: str):
        if dtype == "pd.DataFrame":
            if isinstance(input_data, dict):
                return pd.DataFrame(input_data)
            return pd.DataFrame(input_data)
        elif dtype == "np.ndarray":
            if isinstance(input_data, dict):
                return np.array(pd.DataFrame(input_data))
            return np.array(input_data)
        return input_data
    
    def predict(self, input_data, dtype: str):
        """
        Function exposed via XML-RPC to get predictions.
        The input is decoded according to self.dtype.
        """
        X = self.decode(input_data, dtype)
        prediction = self.model.predict(X)
        # Ensure the output is a serializable type (list)
        return np.array(prediction).tolist()
    
    def predict_proba(self, input_data, dtype: str):
        """
        Function exposed via XML-RPC to get probabilities.
        """
        X = self.decode(input_data, dtype)
        if not hasattr(self.model, "predict_proba"):
            raise ValueError("Model does not have a predict_proba method")
        probabilities = self.model.predict_proba(X)
        return np.array(probabilities).tolist()
    
    def extract_dtype(self, input_data):
        if isinstance(input_data, pd.DataFrame):
            self.dtype = "pd.DataFrame"
        elif isinstance(input_data, np.ndarray):
            self.dtype = "np.ndarray"
        else:
            raise ValueError("Input data must be a pandas DataFrame or a numpy array")

    def __enter__(self):
        logger.info(f"Entering model context for: {self.model.name}")

        self.server = SimpleXMLRPCServer(("127.0.0.1", self.port), allow_none=True, logRequests=False)
        
        self.server.register_function(partial(self.predict, dtype=self.dtype), "predict")
        self.server.register_function(partial(self.predict_proba, dtype=self.dtype), "predict_proba")
        
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logger.info(f"Exiting model context for: {self.model.name}")
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.server_thread:
            self.server_thread.join()
        return False  # Propagate any exception that occurs