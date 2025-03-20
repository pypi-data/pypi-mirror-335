====================================
Setting Up a Quantitative Assessment
====================================

This document provides guidance on how to use the Holistic AI Governance Platform’s SDK functionality to perform a quantitative assessment within a user’s development environment using Python. 

Navigating the Governance Platform
----------------------------------

Before using the library, you must be onboarded and given access to the platform. To get started:

1. Sign in to your instance of the Governance Platform.

2. Locate the Solution for which you would like to perform the Quantitative Assessment.

3. Find the Quantitative Assessment node in the Solution's Panel view.

In this guide, we will use the Efficacy Quantitative Assessment as an example. 

.. image:: ../../_static/images/sdk/qassess.png
   :align: center
   :width: 400px

In the Quantitative Assessment, click the 'SDK Access' button available at the top of the Quantitative Efficacy assessment page and copy the SDK Access Config information to the clipboard. 


.. image:: ../../_static/images/sdk/sdkbutton.png
   :align: center
   :width: 400px

.. image:: ../../_static/images/sdk/sdkconfig.png
   :align: center
   :width: 600px

Initialising a Quantitative Assessment
----------------------------------

In your Python code, import the Holistic AI SDK library together with Pandas as a necessary prerequisite: 

.. code-block::

  from holisticai_sdk import Assessment, Config
  import pandas as pd


The data from the SDK Access Config, as copied to your clipboard above, should then be assigned to a variable named ‘config’ and then an instance of the Config class should be created and assigned to a variable named ‘session’ – for example:

.. code-block::

  config = {
    "projectId": "cc5a543d-418b-4da4-b21f-24b201456b16",
    "solutionId": "9a9c0092-7e70-4d7b-9d67-e3064a745041",
    "moduleId": "EfficacyAssessment",
    "clientId": "none",
    "key": "oooWEAuZYV5NPEHYhje2YVrZYFQznmgC",
    "api": "api-sdk-demo.holisticai.io"
  }

  session = Config(config=config)


The settings for the assessment then need to be defined, and assigned to the ‘settings’ variable – for example:


.. code-block::

  def predict_proba(x):
      """
      Predicts the probability of the positive class. Must return a numpy array with shape (n_samples,).
      """
      return model.predict_proba(x)[:, 1]
      
  def predict(x):
      """
      Predicts the class. Must return a numpy array with shape (n_samples,).
      """
      return model.predict(x)

  settings = {
    "name": "Binary Classifier 1",
    "task": "binary_classification",
    "data_type": "train-test",
    "predict_proba_fn": predict_proba,
    "predict_fn": predict,
  }


- task– this the task being fulfilled by the model. The SDK accepts the tasks: binary_classification, multi_classification, and simple_regression
- data_type – only ‘train-test’ or ‘test’ is available
- predict_proba_fn - the function that returns the probability of the positive class
- predict_fn – the function that returns the predicted class

An instance of the Assess class can then be created thus and assigned to a variable called ‘assess’:

.. code-block::
  
  assess = Assess(session=session, settings=settings)


Running a Quantitative Assessment
---------------------------------

The assessment is run via the run method over the Assess instance, passing to the method the X and y training data (as a Pandas DataFrame), the X and y test data (also as a Pandas DataFrame), :

.. code-block::

  res = assess.run(vertical="efficacy", 
              X_train=X_train, 
              y_train=y_train, 
              X_test=X_test, 
              y_test=y_test)

By assigning the result of the run method to a variable, the results of the assessment can be printed to the console.

The results can be viewed in the console:

.. code-block::

  print(res.metrics)

  [
    {'method': 'User Model',
    'metrics': [{'name': 'Accuracy Score',
      'aggregates': [{'name': 'mean', 'value': 0.5175000000000001},
      {'name': 'median', 'value': 0.5175000000000001},
      {'name': 'q05', 'value': 0.51075},
      {'name': 'q95', 'value': 0.52425},
      {'name': 'mad', 'value': 0.007500000000000007},
      {'name': 'std_error', 'value': 0.007500000000000006}],
      'target': {'range': None, 'value': 1.0}},
    {'name': 'F1 Score',
      'aggregates': [{'name': 'mean', 'value': 0.06722689075630252},
      {'name': 'median', 'value': 0.06722689075630252},
      {'name': 'q05', 'value': 0.04201680672268907},
      {'name': 'q95', 'value': 0.09243697478991596},
      {'name': 'mad', 'value': 0.028011204481792715},
      {'name': 'std_error', 'value': 0.028011204481792715}],
      'target': {'range': None, 'value': 1.0}},
    {'name': 'Brier Score Loss',
      'aggregates': [{'name': 'mean', 'value': 0.26364025718750506},
      {'name': 'median', 'value': 0.26364025718750506},
      {'name': 'q05', 'value': 0.26253417810205504},
      {'name': 'q95', 'value': 0.264746336272955},
      {'name': 'mad', 'value': 0.0012289767616111003},
      {'name': 'std_error', 'value': 0.0012289767616111}],
      'target': {'range': None, 'value': 0.0}},
      ...
      {'name': 'q05', 'value': 0.393975},
      {'name': 'q95', 'value': 0.407925},
      {'name': 'mad', 'value': 0.007750000000000007},
      {'name': 'std_error', 'value': 0.007750000000000006}],
      'target': {'range': None, 'value': 1.0}}]}
  ]

The results can also be viewed on the Solution’s Quantitative Efficacy Assessment page in the Governance Platform:

.. image:: ../../_static/images/sdk/panel.png
   :align: center
   :width: 600px