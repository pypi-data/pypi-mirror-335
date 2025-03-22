.. raw:: html

   <div class="banner-container">
     <div class="banner-content">
       <h1>Gallery</h1>
       <p>Here you can find examples of how to use the Holistic AI SDK</p>
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
     
     /* Modern card styling */
     .card-container {
       display: grid;
       grid-template-columns: repeat(2, 1fr);
       gap: 1.5rem;
       margin: 2rem 0;
     }
     
     .modern-card {
       background: white;
       border-radius: 8px;
       overflow: hidden;
       box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
       transition: transform 0.2s ease, box-shadow 0.2s ease;
       display: block;
       text-decoration: none;
       color: inherit;
       border: 1px solid #f0f0f0;
       padding: 1.25rem;
     }
     
     .modern-card:hover {
       transform: translateY(-3px);
       box-shadow: 0 6px 15px rgba(69, 104, 220, 0.08);
     }
     
     .disabled-card {
       opacity: 0.7;
       pointer-events: none;
       position: relative;
       background: #fafafa;
     }
     
     .coming-soon-badge {
       position: absolute;
       top: 12px;
       right: 12px;
       background: linear-gradient(135deg, #ff9800, #ff5722);
       color: white;
       padding: 0.25rem 0.5rem;
       border-radius: 4px;
       font-size: 0.7rem;
       font-weight: 500;
       z-index: 10;
     }
     
     .card-header {
       display: flex;
       align-items: center;
       margin-bottom: 0.8rem;
     }
     
     .card-icon {
       font-size: 1.5rem;
       background: linear-gradient(135deg, #4568dc, #b06ab3);
       -webkit-background-clip: text;
       -webkit-text-fill-color: transparent;
       margin-right: 0.8rem;
       flex-shrink: 0;
     }
     
     .card-title {
       font-size: 1.1rem;
       font-weight: 600;
       color: #333;
       margin: 0;
     }
     
     .card-text {
       color: #666;
       font-size: 0.9rem;
       line-height: 1.5;
       margin: 0;
     }
     
     /* Category section styling */
     .category-section {
       margin-top: 3rem;
       margin-bottom: 2rem;
     }
     
     .category-title {
       font-size: 1.5rem;
       color: #333;
       margin-bottom: 1rem;
       padding-bottom: 0.5rem;
       border-bottom: 2px solid #f0f0f0;
       position: relative;
     }
     
     .category-title::after {
       content: '';
       position: absolute;
       bottom: -2px;
       left: 0;
       width: 60px;
       height: 2px;
       background: linear-gradient(135deg, #4568dc, #b06ab3);
     }
     
     .example-list {
       list-style: none;
       padding-left: 0;
       margin-top: 1.2rem;
     }
     
     .example-list li {
       margin-bottom: 0.8rem;
       position: relative;
       padding-left: 1.5rem;
     }
     
     .example-list li::before {
       content: '';
       position: absolute;
       left: 0;
       top: 50%;
       transform: translateY(-50%);
       width: 8px;
       height: 8px;
       border-radius: 50%;
       background: linear-gradient(135deg, #4568dc, #b06ab3);
     }
     
     .example-list a {
       color: #4568dc;
       text-decoration: none;
       transition: color 0.2s ease;
     }
     
     .example-list a:hover {
       color: #b06ab3;
       text-decoration: underline;
     }
     
     @media (max-width: 768px) {
       .card-container {
         grid-template-columns: 1fr;
       }
     }
   </style>

Examples Gallery
----------------

This gallery provides examples of how to use the Holistic AI SDK to assess various aspects of AI systems.

.. raw:: html

   <!-- Font Awesome -->
   <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

   <div class="card-container">
     <a href="tutorials/efficacy_sdk.html" class="modern-card">
       <div class="card-header">
         <i class="fas fa-chart-line card-icon"></i>
         <h3 class="card-title">Efficacy Assessment</h3>
       </div>
       <p class="card-text">Learn how to assess the performance and accuracy of your models</p>
     </a>
     
     <a href="tutorials/bias_sdk.html" class="modern-card">
       <div class="card-header">
         <i class="fas fa-balance-scale card-icon"></i>
         <h3 class="card-title">Bias Assessment</h3>
       </div>
       <p class="card-text">Discover how to identify and measure bias in your AI systems</p>
     </a>

     <a href="tutorials/robustness_sdk.html" class="modern-card">
       <div class="card-header">
         <i class="fas fa-balance-scale card-icon"></i>
         <h3 class="card-title">Robustness Assessment</h3>
       </div>
       <p class="card-text">Test how your models perform under various adversarial conditions</p>
     </a>
     
     
     <div class="modern-card disabled-card">
       <span class="coming-soon-badge">Coming Soon</span>
       <div class="card-header">
         <i class="fas fa-lock card-icon"></i>
         <h3 class="card-title">Security Assessment</h3>
       </div>
       <p class="card-text">Evaluate the security vulnerabilities of your AI systems</p>
     </div>
   </div>

   <div class="category-section">
     <h2 class="category-title">Efficacy</h2>
     <p>Examples demonstrating how to assess model performance:</p>
     <ul class="example-list">
       <li><a href="tutorials/efficacy_binary_classification.ipynb">Binary Classification Efficacy Assessment</a></li>
       <li><a href="tutorials/efficacy_multiclass.ipynb">Multi-class Classification Efficacy Assessment</a></li>
       <li><a href="tutorials/efficacy_regression.ipynb">Regression Efficacy Assessment</a></li>
       <li><a href="tutorials/efficacy_clustering.ipynb">Clustering Efficacy Assessment</a></li>
     </ul>
   </div>

   <div class="category-section">
     <h2 class="category-title">Bias</h2>
     <p>Examples showing how to measure and mitigate bias:</p>
     <ul class="example-list">
       <li><a href="tutorials/bias_binary_classification.ipynb">Binary Classification Bias Assessment</a></li>
       <li><a href="tutorials/bias_multiclass.ipynb">Multi-class Classification Bias Assessment</a></li>
       <li><a href="tutorials/bias_regression.ipynb">Regression Bias Assessment</a></li>
       <li><a href="tutorials/bias_clustering.ipynb">Clustering Bias Assessment</a></li>
     </ul>
   </div>

   <div class="category-section">
     <h2 class="category-title">Robustness</h2>
     <p>Examples for testing model resilience:</p>
     <ul class="example-list">
       <li><a href="tutorials/robustness_adversarial.ipynb">Adversarial Attacks Assessment</a></li>
       <li><a href="tutorials/robustness_perturbation.ipynb">Data Perturbation Assessment</a></li>
     </ul>
   </div>

   <div class="category-section">
     <h2 class="category-title">Security</h2>
     <p>Examples for evaluating model security:</p>
     <ul class="example-list">
       <li><a href="tutorials/security_model_inversion.ipynb">Model Inversion Attacks</a></li>
       <li><a href="tutorials/security_membership_inference.ipynb">Membership Inference Attacks</a></li>
     </ul>
   </div>

.. toctree::
   :maxdepth: 1
   :hidden:

   tutorials/efficacy_sdk
   tutorials/bias_sdk
   tutorials/robustness_sdk
   tutorials/security_sdk
