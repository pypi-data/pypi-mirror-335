.. raw:: html

   <div class="banner-container">
     <div class="banner-content">
       <h1>Technical Risks in AI</h1>
       <p>Understanding and mitigating risks in AI systems</p>
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
       font-family: 'Ubuntu', sans-serif;
     }
     .banner-content h1 {
       font-size: 2.2rem;
       margin-bottom: 1rem;
       color: white;
       font-family: 'Ubuntu', sans-serif;
       font-weight: 500;
     }
     .banner-content p {
       font-size: 1.1rem;
       opacity: 0.9;
       font-family: 'Ubuntu', sans-serif;
       font-weight: 300;
     }
     .risk-card {
       background: white;
       border-radius: 12px;
       box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
       padding: 1.5rem;
       margin-bottom: 2rem;
       transition: transform 0.3s ease, box-shadow 0.3s ease;
       position: relative;
       overflow: hidden;
     }
     .risk-card:hover {
       transform: translateY(-5px);
       box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12);
     }
     .risk-card::before {
       content: '';
       position: absolute;
       top: 0;
       left: 0;
       width: 5px;
       height: 100%;
       background: linear-gradient(135deg, #4568dc, #b06ab3);
     }
     .risk-card h2 {
       margin-top: 0;
       color: #333;
       font-size: 1.5rem;
       font-family: 'Ubuntu', sans-serif;
       font-weight: 500;
     }
     .risk-card p {
       color: #666;
       font-size: 1rem;
       line-height: 1.6;
       font-family: 'Ubuntu', sans-serif;
     }
     .risk-metrics {
       display: flex;
       flex-wrap: wrap;
       gap: 1rem;
       margin-top: 1rem;
     }
     .metric-badge {
       background: #f5f7fa;
       border-radius: 20px;
       padding: 0.4rem 0.8rem;
       font-size: 0.9rem;
       color: #4568dc;
       font-weight: 500;
       cursor: pointer;
       transition: background-color 0.2s ease;
     }
     .metric-badge:hover {
       background: #e9ecf3;
     }
     .coming-soon {
       opacity: 0.6;
     }
     .coming-soon-label {
       display: inline-block;
       background: #ff9800;
       color: white;
       padding: 0.2rem 0.5rem;
       border-radius: 4px;
       font-size: 0.7rem;
       margin-left: 0.5rem;
       vertical-align: middle;
     }
     
     /* Modal styles */
     .metric-modal {
       display: none;
       position: fixed;
       z-index: 1000;
       left: 0;
       top: 0;
       width: 100%;
       height: 100%;
       overflow: auto;
       background-color: rgba(0,0,0,0.4);
       opacity: 0;
       transition: opacity 0.3s ease;
     }
     
     .metric-modal.show {
       opacity: 1;
       display: block;
     }
     
     .metric-modal-content {
       background-color: #fefefe;
       margin: 10% auto;
       padding: 2rem;
       border-radius: 12px;
       box-shadow: 0 5px 30px rgba(0,0,0,0.15);
       max-width: 600px;
       transform: translateY(-20px);
       transition: transform 0.3s ease;
       position: relative;
     }
     
     .metric-modal.show .metric-modal-content {
       transform: translateY(0);
     }
     
     .close-modal {
       position: absolute;
       top: 15px;
       right: 20px;
       font-size: 1.5rem;
       font-weight: bold;
       color: #aaa;
       cursor: pointer;
     }
     
     .close-modal:hover {
       color: #333;
     }
     
     .metric-title {
       color: #4568dc;
       margin-top: 0;
       margin-bottom: 1rem;
       font-size: 1.5rem;
       border-bottom: 2px solid #f0f0f0;
       padding-bottom: 0.5rem;
     }
     
     .metric-description {
       margin-bottom: 1.5rem;
       line-height: 1.6;
     }
     
     .metric-formula {
       background: #f8f9fa;
       padding: 1.5rem;
       border-radius: 8px;
       text-align: center;
       margin-bottom: 1.5rem;
     }
     
     .metric-use-cases {
       background: #f0f7ff;
       padding: 1rem 1.5rem;
       border-radius: 8px;
       border-left: 4px solid #4568dc;
     }
     
     .metric-use-cases h4 {
       margin-top: 0;
       color: #4568dc;
     }
   </style>

Technical Risks
---------------

AI systems can introduce various technical risks that need to be identified, measured, and mitigated. The Holistic AI SDK provides tools to assess these risks across multiple dimensions.

.. raw:: html

   <!-- Modal container -->
   <div id="metricModal" class="metric-modal">
     <div class="metric-modal-content">
       <span class="close-modal">&times;</span>
       <h3 class="metric-title" id="metricTitle">Metric Name</h3>
       <div class="metric-description" id="metricDescription">Description goes here</div>
       <div class="metric-formula" id="metricFormula">Formula goes here</div>
       <div class="metric-use-cases">
         <h4>When to use this metric</h4>
         <p id="metricUseCases">Use cases go here</p>
       </div>
     </div>
   </div>

   <!-- JavaScript for the modal functionality -->
   <script type="text/javascript">
     document.addEventListener('DOMContentLoaded', function() {
       // Add click event listeners to all metric badges
       const metricBadges = document.querySelectorAll('.metric-badge');
       metricBadges.forEach(badge => {
         badge.addEventListener('click', function() {
           const title = this.getAttribute('data-title');
           const description = this.getAttribute('data-description');
           const formula = this.getAttribute('data-formula');
           const useCases = this.getAttribute('data-use-cases');
           
           if (title && description && formula) {
             showMetricDetails(title, description, formula, useCases);
           }
         });
       });
       
       // Close modal when clicking the X
       const closeButton = document.querySelector('.close-modal');
       if (closeButton) {
         closeButton.addEventListener('click', function() {
           document.getElementById('metricModal').classList.remove('show');
         });
       }
       
       // Close modal when clicking outside the content
       window.addEventListener('click', function(event) {
         const modal = document.getElementById('metricModal');
         if (event.target === modal) {
           modal.classList.remove('show');
         }
       });
     });
     
     function showMetricDetails(title, description, formula, useCases) {
       // Set modal content
       document.getElementById('metricTitle').textContent = title;
       document.getElementById('metricDescription').textContent = description;
       
       // Clear and set formula with proper delimiters for MathJax
       const formulaElement = document.getElementById('metricFormula');
       formulaElement.innerHTML = '';
       
       // Create a div specifically for MathJax to render
       const mathDiv = document.createElement('div');
       mathDiv.className = 'math';
       mathDiv.innerHTML = '\\[' + formula + '\\]';
       formulaElement.appendChild(mathDiv);
       
       document.getElementById('metricUseCases').textContent = useCases;
       
       // Show modal
       const modal = document.getElementById('metricModal');
       modal.classList.add('show');
       
       // Render LaTeX with MathJax
       if (window.MathJax) {
         window.MathJax.typesetPromise([formulaElement]).catch(function(err) {
           console.log('Error typesetting math:', err);
         });
       } else {
         console.warn('MathJax not available');
       }
     }
   </script>

   <!-- Add MathJax configuration at the top of the document -->
   <script type="text/javascript">
     window.MathJax = {
       tex: {
         inlineMath: [['$', '$'], ['\\(', '\\)']],
         displayMath: [['$$', '$$'], ['\\[', '\\]']],
         processEscapes: true,
         processEnvironments: true
       },
       options: {
         skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
       }
     };
   </script>
   <script type="text/javascript" id="MathJax-script" async
     src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
   </script>

   <!-- Update metric badges to use data attributes instead of onclick -->
   <div class="risk-card">
     <h2>Efficacy</h2>
     <p>Efficacy refers to how well an AI model performs its intended task. Poor efficacy can lead to incorrect predictions, recommendations, or decisions, potentially causing harm to users or stakeholders.</p>
     <div class="risk-metrics">
       <span class="metric-badge" 
             data-title="Accuracy" 
             data-description="The proportion of correct predictions among the total number of predictions." 
             data-formula="\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}" 
             data-use-cases="Use accuracy when your classes are balanced and all types of errors are equally important. It's most suitable for classification tasks with similar costs for false positives and false negatives.">Accuracy</span>
       <span class="metric-badge" 
             data-title="Precision" 
             data-description="The proportion of true positive predictions among all positive predictions." 
             data-formula="\text{Precision} = \frac{TP}{TP + FP}" 
             data-use-cases="Use precision when the cost of false positives is high. For example, in spam detection, where marking a legitimate email as spam (false positive) is more problematic than missing some spam emails.">Precision</span>
       <span class="metric-badge" 
             data-title="Recall" 
             data-description="The proportion of true positive predictions among all actual positives." 
             data-formula="\text{Recall} = \frac{TP}{TP + FN}" 
             data-use-cases="Use recall when the cost of false negatives is high. For example, in medical diagnosis, where missing a disease (false negative) can be more harmful than a false alarm.">Recall</span>
       <span class="metric-badge" 
             data-title="F1 Score" 
             data-description="The harmonic mean of precision and recall, providing a balance between the two." 
             data-formula="F1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}" 
             data-use-cases="Use F1 score when you need a balance between precision and recall, especially with imbalanced datasets where accuracy might be misleading.">F1 Score</span>
       <span class="metric-badge" 
             data-title="AUC-ROC" 
             data-description="Area Under the Receiver Operating Characteristic curve, measuring the ability to distinguish between classes." 
             data-formula="AUC = \int_{0}^{1} TPR(FPR^{-1}(t)) dt" 
             data-use-cases="Use AUC-ROC when you need to evaluate how well your model can distinguish between classes, regardless of the classification threshold. It's particularly useful for imbalanced datasets and when you need to compare different models.">AUC-ROC</span>
       <span class="metric-badge" 
             data-title="Mean Squared Error" 
             data-description="The average of the squared differences between predicted and actual values." 
             data-formula="MSE = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2" 
             data-use-cases="Use MSE for regression tasks when larger errors should be penalized more heavily than smaller ones. It's particularly useful when outliers are significant and should influence the model evaluation.">Mean Squared Error</span>
     </div>
   </div>

   <div class="risk-card">
     <h2>Bias</h2>
     <p>Bias occurs when an AI system systematically and unfairly discriminates against certain individuals or groups. Biased AI can perpetuate or amplify existing social inequalities and lead to unfair treatment.</p>
     <div class="risk-metrics">
       <span class="metric-badge" 
             data-title="Demographic Parity" 
             data-description="The probability of a positive outcome should be the same across all demographic groups." 
             data-formula="P(\hat{Y}=1|A=a) = P(\hat{Y}=1|A=b) \text{ for all } a,b" 
             data-use-cases="Use demographic parity when you want to ensure that positive outcomes are distributed equally across different demographic groups, regardless of the true underlying distribution.">Demographic Parity</span>
       <span class="metric-badge" 
             data-title="Equal Opportunity" 
             data-description="The true positive rates should be equal across all demographic groups." 
             data-formula="P(\hat{Y}=1|Y=1,A=a) = P(\hat{Y}=1|Y=1,A=b) \text{ for all } a,b" 
             data-use-cases="Use equalized odds when you want to ensure that both the true positive rate and false positive rate are the same across different demographic groups, providing a stronger fairness guarantee than equal opportunity.">Equalized Odds</span>
       <span class="metric-badge" 
             data-title="Disparate Impact" 
             data-description="The ratio of positive outcome rates between different demographic groups." 
             data-formula="\text{Disparate Impact} = \frac{P(\hat{Y}=1|A=\text{unprivileged})}{P(\hat{Y}=1|A=\text{privileged})}" 
             data-use-cases="Use disparate impact when you need to comply with legal standards like the 80% rule, which states that the ratio of positive outcomes between protected and unprotected groups should be at least 0.8.">Disparate Impact</span>
       <span class="metric-badge" 
             data-title="Statistical Parity" 
             data-description="The difference in positive outcome rates between demographic groups." 
             data-formula="\text{Statistical Parity Difference} = P(\hat{Y}=1|A=a) - P(\hat{Y}=1|A=b)" 
             data-use-cases="Use statistical parity difference when you want to measure the absolute difference in outcome rates between groups, with a value of 0 indicating perfect parity.">Statistical Parity</span>
     </div>
   </div>

   <div class="risk-card coming-soon">
     <h2>Robustness <span class="coming-soon-label">Coming Soon</span></h2>
     <p>Robustness measures how well an AI system maintains its performance under various conditions, including adversarial attacks, data perturbations, and distribution shifts. Non-robust systems can be manipulated or fail unexpectedly.</p>
     <div class="risk-metrics">
       <span class="metric-badge">Adversarial Accuracy</span>
       <span class="metric-badge">Perturbation Sensitivity</span>
       <span class="metric-badge">Distribution Shift Resilience</span>
       <span class="metric-badge">Noise Tolerance</span>
     </div>
   </div>

   <div class="risk-card coming-soon">
     <h2>Security <span class="coming-soon-label">Coming Soon</span></h2>
     <p>Security concerns the protection of AI systems against unauthorized access, data breaches, and other malicious activities. Insecure AI systems can leak sensitive information or be compromised to produce harmful outputs.</p>
     <div class="risk-metrics">
       <span class="metric-badge">Data Leakage</span>
       <span class="metric-badge">Model Inversion</span>
       <span class="metric-badge">Membership Inference</span>
       <span class="metric-badge">Model Stealing</span>
     </div>
   </div>

The Holistic AI SDK provides comprehensive tools to help you assess and mitigate these technical risks, ensuring your AI systems are trustworthy, fair, and robust.

.. toctree::
   :maxdepth: 1
   :hidden:

   efficacy
   bias
   robustness
   security
