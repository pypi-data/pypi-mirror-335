import sys

sys.path.insert(0, r"C:\Users\cris_\hai-sdk\src")

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sdk import Session, Assessment

config = {
  "projectId": "c938e116-8163-4103-b6b8-14807f41f5ae",
  "solutionId": "6826b507-7dcc-4236-90b1-cb0bad8b92bf",
  "moduleId": "EfficacyAssessment",
  "clientId": "unilever",
  "key": "PWhFuKJb2SQ5Wn9dDzrlBwaf4CiPQx09",
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
    "name": "My Model",
    "config": config,
    "task": "binary_classification",
    "data_type": "test",
    "classes": model.classes_,
    "predict_proba_fn": predict_proba,
    "predict_fn": predict,
    # for testing purposes
    "use_virtual_env": False, 
    "reset_env":False
}

assess = Assessment(session=session, settings=settings)
res = assess.run(vertical="efficacy", 
                 X_train=X_train, 
                 y_train=y_train, 
                 X_test=X_test, 
                 y_test=y_test)