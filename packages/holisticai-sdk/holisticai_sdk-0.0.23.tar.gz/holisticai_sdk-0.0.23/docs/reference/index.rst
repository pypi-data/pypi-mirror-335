.. raw:: html

   <div class="banner-container">
     <div class="banner-content">
       <h1>API Reference</h1>
       <p>Here you can find the API reference for the Holistic AI SDK</p>
     </div>
   </div>

   <style>
     .banner-container {
       background: linear-gradient(135deg, #4568dc, #b06ab3);
       color: white;
       padding: 2.5rem 2rem;
       border-radius: 8px;
       margin-bottom: 2rem;
       text-align: center;
     }
     .banner-content h1 {
       font-size: 2.2rem;
       margin-bottom: 1rem;
       color: white;
     }
     .banner-content p {
       font-size: 1.1rem;
       opacity: 0.9;
     }
   </style>

API Reference
-------------

This section provides detailed documentation for the Holistic AI SDK API.

.. currentmodule:: holisticai_sdk


Core Classes
~~~~~~~~~~~~~

.. autosummary::
   :toctree: generated/
   
   Session
   Assessment
   QuantitativeAssessment

Model Definitions
~~~~~~~~~~~~~~~~~

.. currentmodule:: holisticai_sdk.engine.definitions

.. autosummary::
   :toctree: generated/
   
   HAIModel
   HAIBinaryClassification
   HAIProbBinaryClassification
   HAIRigidBinaryClassification
   HAIMultiClassification
   HAIProbMultiClassification
   HAIRigidMultiClassification
   HAIRegression
   HAIClustering
   HAIClassification

Model Utilities
~~~~~~~~~~~~~~~~~

.. currentmodule:: holisticai_sdk.engine.models

.. autosummary::
   :toctree: generated/
   
   get_proxy_from_sdk_model
   get_baselines
   predict
   predict_proba

Datasets
~~~~~~~~~~~~~~~~~

.. currentmodule:: holisticai_sdk.engine.definitions

.. autosummary::
   :toctree: generated/
   
   Dataset
   SupervisedDataset
   UnsupervisedDataset
   BiasSupervisedDataset
   BiasUnsupervisedDataset

Metrics
~~~~~~~~~~~~~~~~~

.. currentmodule:: holisticai_sdk.engine.metrics

.. autosummary::
   :toctree: generated/
   
   compute_bias_metrics
   compute_efficacy_metrics
   compute_explainability_metrics
   compute_robustness_metrics
   compute_security_metrics
   bias_metrics
   efficacy_metrics
   explainability_metrics
   robustness_metrics
   security_metrics

Vertical Settings
~~~~~~~~~~~~~~~~~

.. currentmodule:: holisticai_sdk.engine.definitions

.. autosummary::
   :toctree: generated/
   
   VerticalSettings
   SecuritySettings
   RobustnessSettings

Bootstrapping
~~~~~~~~~~~~~~~~~

.. currentmodule:: holisticai_sdk.engine.definitions

.. autosummary::
   :toctree: generated/
   
   Bootstrapping
   BootstrapMetric
   BootstrapModelMetrics
   MetricAggregate
   MetricAggregates
   BootstrapModelMetricAggregates
