from holisticai_sdk import Assessment, Session
from sklearn.linear_model import LogisticRegression
import pandas as pd

config = {
  "projectId": "YOUR_PROJECT_ID",
  "solutionId": "YOUR_SOLUTION_ID",
  "moduleId": "RobustnessAssessment",
  "clientId": "unilever",
  "key": "YOUR_KEY",
  "api": "api-sdk-staging-unilever-v1.holisticai.io"
}

session = Session(config=config)

df_train = pd.read_csv("data/german_credit_train.csv")
df_test = pd.read_csv("data/german_credit_test.csv")

X_train = df_train.drop(columns=["default"])
y_train = df_train["default"]

X_test = df_test.drop(columns=["default"])
y_test = df_test["default"]

model = LogisticRegression(penalty=None, solver="lbfgs", max_iter=20)
model.fit(X_train, y_train)
 
def predict_proba(x):
    return model.predict_proba(x)[:, 1]
    
def predict(x):
    return model.predict(x)

settings = {
    "name": "Robustness_model",
    "config": config,
    "task": "binary_classification",
    "data_type": "test",
    "classes": model.classes_,
    "predict_proba_fn": predict_proba,
    "predict_fn": predict,
    # for testing purposes
    "use_virtual_env": False, 
    "reset_env":False,
}

attributes = ["gender_male ", "gender_female "]

assess = Assessment(session=session, settings=settings)
res = assess.run(vertical="robustness", 
                 X_train=X_train, 
                 y_train=y_train, 
                 X_test=X_test, 
                 y_test=y_test,
                 attack_attributes=attributes,)
