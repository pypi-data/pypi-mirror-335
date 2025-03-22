.. Holisticai-SDK documentation master file, created by
   sphinx-quickstart on Thu Feb 13 10:55:06 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. raw:: html

   <div class="banner-container">
     <div class="banner-content">
       <h1>Holistic AI SDK</h1>
       <p>Assess and improve the trustworthiness of your AI systems</p>
     </div>
   </div>

   <style>
     .banner-container {
       background: linear-gradient(135deg, #4568dc, #b06ab3);
       color: white;
       padding: 3rem 2rem;
       border-radius: 8px;
       margin-bottom: 2rem;
       text-align: center;
     }
     .banner-content h1 {
       font-size: 2.5rem;
       margin-bottom: 1rem;
       color: white;
     }
     .banner-content p {
       font-size: 1.2rem;
       opacity: 0.9;
     }
   </style>

The Holistic AI SDK is an open-source tool designed to assess and improve the trustworthiness of AI systems. 
Our platform provides comprehensive tools to measure and mitigate technical risks across multiple dimensions:

- **Efficacy**: Evaluate model performance and accuracy
- **Bias**: Identify and address unfair treatment of different groups
- **Robustness (soon)**: Test resilience against adversarial attacks and data perturbations
- **Security (soon)**: Protect against data leakage and model vulnerabilities

.. grid:: 4
    :gutter: 2
    :padding: 1 1 0 0
    :class-container: sd-text-center

    .. grid-item::
        .. button-link:: https://www.holisticai.com/        
            :class: btn-outline-primary btn-lg
            :shadow: sm

            :fa:`globe` Visit Our Website

.. grid:: 1 2 2 2
    :gutter: 4
    :padding: 4 4 0 0
    :class-container: sd-text-center

    .. grid-item-card:: Getting Started
        :img-top: _static/images/getting_started.svg
        :class-card: sd-card-hover intro-card
        :link: getting_started/index.html
        :shadow: md

        Learn how to install and use the SDK with step-by-step guides

    .. grid-item-card:: Example Gallery
        :img-top: _static/images/gallery.svg
        :class-card: sd-card-hover intro-card
        :link: gallery/index.html
        :shadow: md

        Explore practical examples showing how to integrate the SDK with your projects

    .. grid-item-card:: API Reference
        :img-top: _static/images/reference.svg
        :class-card: sd-card-hover intro-card
        :link: reference/index.html
        :shadow: md

        Comprehensive documentation of all SDK components and functions

    .. grid-item-card:: Technical Risks
        :img-top: _static/images/learn.svg
        :class-card: sd-card-hover intro-card
        :link: risks/index.html
        :shadow: md
            
        Understand the technical risks associated with AI systems

Key Features
-----------

.. raw:: html

   <div class="features-container">
     <div class="feature-card">
       <div class="feature-icon">
         <i class="fas fa-chart-line"></i>
       </div>
       <div class="feature-content">
         <h3>Comprehensive Assessment</h3>
         <p>Evaluate AI systems across multiple dimensions including efficacy, bias, 
         robustness, and security to ensure holistic trustworthiness.</p>
       </div>
     </div>
     
     <div class="feature-card">
       <div class="feature-icon">
         <i class="fas fa-plug"></i>
       </div>
       <div class="feature-content">
         <h3>Easy Integration</h3>
         <p>Seamlessly integrate with your existing ML workflows and CI/CD pipelines
         to automate assessment and reporting.</p>
       </div>
     </div>
     
     <div class="feature-card">
       <div class="feature-icon">
         <i class="fas fa-analytics"></i>
       </div>
       <div class="feature-content">
         <h3>Detailed Metrics</h3>
         <p>Access comprehensive metrics and visualizations to understand your model's
         performance and identify areas for improvement.</p>
       </div>
     </div>
     
     <div class="feature-card">
       <div class="feature-icon">
         <i class="fas fa-balance-scale"></i>
       </div>
       <div class="feature-content">
         <h3>Baseline Comparisons</h3>
         <p>Compare your models against industry baselines to benchmark performance
         and identify competitive advantages.</p>
       </div>
     </div>
   </div>

   <style>
     .features-container {
       display: grid;
       grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
       gap: 1.5rem;
       margin: 2rem 0;
     }
     
     .feature-card {
       background: white;
       border-radius: 12px;
       box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
       padding: 1.5rem;
       transition: transform 0.3s ease, box-shadow 0.3s ease;
       display: flex;
       align-items: flex-start;
       overflow: hidden;
       position: relative;
     }
     
     .feature-card:hover {
       transform: translateY(-5px);
       box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
     }
     
     .feature-card::before {
       content: '';
       position: absolute;
       top: 0;
       left: 0;
       width: 5px;
       height: 100%;
       background: linear-gradient(135deg, #4568dc, #b06ab3);
     }
     
     .feature-icon {
       font-size: 1.8rem;
       color: #4568dc;
       margin-right: 1rem;
       display: flex;
       align-items: center;
       justify-content: center;
       min-width: 50px;
     }
     
     .feature-content h3 {
       margin-top: 0;
       margin-bottom: 0.5rem;
       color: #333;
       font-size: 1.2rem;
     }
     
     .feature-content p {
       margin: 0;
       color: #666;
       font-size: 0.95rem;
       line-height: 1.5;
     }
     
     @media (max-width: 768px) {
       .features-container {
         grid-template-columns: 1fr;
       }
     }
   </style>

.. toctree::
   :maxdepth: 2
   :hidden:

   getting_started/index
   reference/index
   gallery/index
   risks/index