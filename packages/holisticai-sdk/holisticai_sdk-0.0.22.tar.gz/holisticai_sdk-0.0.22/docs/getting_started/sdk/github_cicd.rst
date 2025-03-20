==================================
Setting Up a GitHub CI/CD Pipeline
==================================

This document provides guidance on using the Holistic AI Governance Platform’s SDK functionality to set up a Continuous Integration / Continuous Delivery (CI/CD) pipeline for model development using GitHub.

.. note::
  This guidance assumes model development is conducted within a repository managed using GitHub.

Creating the GitHub Workflow
----------------------------

To configure the CI/CD pipeline in GitHub, a workflow must be created for your repository:

1. Navigate to your repository in GitHub.
2. Open the 'Actions' tab in the repository's top navigation bar. |action|
3. Click the 'New workflow' button in the top left corner of the Actions tab |newworkflow|.
4. Click the hyperlink 'set up a workflow yourself' on the 'Choose a workflow' page.
5. Enter your test script using YAML:

.. |action| image:: ../../_static/images/sdk/action.avif
   :width: 80px

.. |newworkflow| image:: ../../_static/images/sdk/newworkflow.avif
   :width: 80px

.. image:: ../../_static/images/sdk/console.png
   :align: center
   :width: 400px

The following YAML workflow script tests Python development (Python 3.9):

.. code-block:: yaml

  name: Test pipeline
  on: pull_request

  jobs:
    integration-test-pipeline:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
          with:
            fetch-depth: 0
        - uses: actions/setup-python@v4
          with:
            python-version: 3.9

        - name: Install dependencies
          run: |
            python -m pip install --upgrade pip
            pip install -r requirements.txt
            pip install holisticai_sdk

        - name: Run tests
          run: |
            pytest -s

Commit this YAML script to deploy the workflow.

Navigating the Governance Platform
----------------------------------

Before using the SDK, you must have access to the platform:

1. Sign in to your instance of the Governance Platform.
2. Select the Solution for your CI/CD pipeline.
3. Access the Quantitative Assessment node from the Solution's Panel view.

Using the Efficacy Quantitative Assessment as an example:

.. image:: ../../_static/images/sdk/qassess.png
   :align: center
   :width: 400px

In the Quantitative Assessment, click the 'SDK Access' button at the top of the page and copy the SDK Access Config information.

.. image:: ../../_static/images/sdk/sdkbutton.png
   :align: center
   :width: 300px

.. raw:: html
   <br><br>

.. image:: ../../_static/images/sdk/sdkconfig.png
   :align: center
   :width: 600px

Initializing a Quantitative Assessment
--------------------------------------

In Python, import the Holistic AI SDK library along with Pandas:

.. code-block::

  from holisticai_sdk import Assess, Config
  import pandas as pd

Assign the copied SDK Access Config data to a variable named `config` and create an instance of the Config class:

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

Define assessment settings and assign them to the `settings` variable:

.. code-block::

  def predict_proba(x):
      return model.predict_proba(x)[:, 1]
      
  def predict(x):
      return model.predict(x)

  settings = {
    "name": "Binary Classifier 1",
    "task": "binary_classification",
    "data_type": "train-test",
    "predict_proba_fn": predict_proba,
    "predict_fn": predict,
  }

- `task`: supports `binary_classification`, `multi_classification`, and `simple_regression`
- `data_type`: supports `train-test` or `test`
- `predict_proba_fn`: function returning positive class probabilities
- `predict_fn`: function returning predicted classes

Create an instance of the Assess class:

.. code-block::

  assess = Assess(session=session, settings=settings)

Running the Quantitative Assessment
-----------------------------------

Execute the assessment using the `run` method, passing training and test data as Pandas DataFrames:

.. code-block::

  res = assess.run(vertical="efficacy",
                   X_train=X_train,
                   y_train=y_train,
                   X_test=X_test,
                   y_test=y_test)

Access the results using:

.. code-block::

  metrics = res.metrics

Implement tests within the CI/CD workflow using Python assertions. For example, verifying the Precision metric:

.. code-block::

  for metric in metrics:
      if metric['name'] == 'Precision':
          assert metric['aggregates'][0]['value'] >= 0.8  # Adjust threshold as necessary

Running the Pipeline
--------------------

Whenever your model code is updated and pushed to GitHub, the configured workflow will automatically run. It performs the tests specified in your pipeline and generates GitHub alerts indicating if the current model iteration passes the configured tests.

