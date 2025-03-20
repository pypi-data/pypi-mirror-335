import argparse
import pickle
from holisticai_sdk.engine.assessment.core import run_assessment
from holisticai_sdk.assessments.model_context import Model
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run assessment")
    parser.add_argument("--input_path", type=str, default="input.pkl")
    parser.add_argument("--output_path", type=str, default="output.pkl")
    parser.add_argument("--client_port", type=int, default=8000)
    args = parser.parse_args()    

    inputs = pickle.load(open(args.input_path, "rb"))
    params = inputs["params"]
    model_metadata = inputs["model_metadata"]

    model = Model.from_remote(task=model_metadata["task"], 
                              server_url=f"http://127.0.0.1:{args.client_port}/",
                              has_probabilities=model_metadata["has_probabilities"],
                              classes=model_metadata.get('classes'),
                              n_clusters=model_metadata.get('n_clusters')
                              )

    results = run_assessment(model=model, params=params)
    json.dump(results, open(args.output_path, "w"))
