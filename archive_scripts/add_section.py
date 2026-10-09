import json

with open('hostel_complaint_prioritization.ipynb', 'rb') as f:
    nb = json.loads(f.read().decode('utf-8', errors='replace'))

section14_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "## SECTION 14: Project Conclusions\n",
            "\n",
            "This is the final section of the **AI-Based Hostel Complaint Prioritization System** notebook.\n",
            "We summarize all findings, limitations, and future directions in a format suitable for a B.Tech mini project report and viva."
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 14.1 - Final Model Performance Summary"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ============================================================\n",
            "# 14.1  FINAL PERFORMANCE SUMMARY TABLE\n",
            "# ============================================================\n",
            "\n",
            "print('FINAL PROJECT RESULTS')\n",
            "print('=' * 75)\n",
            "print(f'{\"Model\":<22} {\"Accuracy\":>10} {\"Precision\":>10} {\"Recall\":>10} {\"F1-Score\":>10}')\n",
            "print('-' * 75)\n",
            "for model_name, res in results.items():\n",
            "    print(f'{model_name:<22} {res[\"Accuracy\"]:>10.4f} {res[\"Precision\"]:>10.4f} '\n",
            "          f'{res[\"Recall\"]:>10.4f} {res[\"F1-Score\"]:>10.4f}')\n",
            "print('-' * 75)\n",
            "\n",
            "print(f'\\nSelected Final Model  : {best_tuned_name}')\n",
            "print(f'Test F1-Score (tuned) : {best_tuned_f1:.4f}')\n",
            "print(f'Test Accuracy (tuned) : {accuracy_score(y_test, final_model.predict(X_test_raw)):.4f}')\n",
            "print(f'\\nNote: Naive Bayes used TF-IDF features only. Other models used all features.')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 14.2 - Complete Project Pipeline Visualization"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ============================================================\n",
            "# 14.2  PROJECT PIPELINE VISUALIZATION\n",
            "# ============================================================\n",
            "\n",
            "fig, ax = plt.subplots(figsize=(16, 5))\n",
            "ax.axis('off')\n",
            "\n",
            "# Pipeline stages\n",
            "stages = [\n",
            "    ('Raw Dataset\\n(800 complaints)', '#3498db'),\n",
            "    ('EDA\\n(Sections 2)', '#9b59b6'),\n",
            "    ('NLP Preprocessing\\n(Section 3)', '#e67e22'),\n",
            "    ('TF-IDF\\nVectorization\\n(Section 4)', '#e74c3c'),\n",
            "    ('Feature\\nEngineering\\n(Section 5)', '#1abc9c'),\n",
            "    ('Model Training\\n(Sections 6-9)', '#2980b9'),\n",
            "    ('Evaluation &\\nComparison\\n(Section 10)', '#8e44ad'),\n",
            "    ('CV + Tuning\\n(Section 11)', '#d35400'),\n",
            "    ('Save & Deploy\\n(Sections 12-13)', '#27ae60'),\n",
            "]\n",
            "\n",
            "n = len(stages)\n",
            "box_w, box_h = 0.10, 0.55\n",
            "gap = 0.005\n",
            "start_x = 0.01\n",
            "\n",
            "for i, (label, color) in enumerate(stages):\n",
            "    x = start_x + i * (box_w + gap)\n",
            "    rect = plt.Rectangle((x, 0.2), box_w, box_h,\n",
            "                          facecolor=color, edgecolor='white',\n",
            "                          linewidth=2, alpha=0.88,\n",
            "                          transform=ax.transAxes, clip_on=False)\n",
            "    ax.add_patch(rect)\n",
            "    ax.text(x + box_w / 2, 0.475, label,\n",
            "            transform=ax.transAxes,\n",
            "            ha='center', va='center',\n",
            "            fontsize=8.5, fontweight='bold', color='white',\n",
            "            wrap=True)\n",
            "    if i < n - 1:\n",
            "        ax.annotate('', xy=(x + box_w + gap, 0.475),\n",
            "                    xytext=(x + box_w, 0.475),\n",
            "                    xycoords='axes fraction', textcoords='axes fraction',\n",
            "                    arrowprops=dict(arrowstyle='->', color='#2c3e50', lw=2))\n",
            "\n",
            "ax.set_title('AI-Based Hostel Complaint Prioritization - Full Pipeline',\n",
            "             fontsize=14, fontweight='bold', pad=20)\n",
            "plt.tight_layout()\n",
            "plt.savefig('project_pipeline.png', bbox_inches='tight', dpi=150)\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 14.3 - Key Findings"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ============================================================\n",
            "# 14.3  KEY FINDINGS SUMMARY\n",
            "# ============================================================\n",
            "\n",
            "findings = [\n",
            "    ('Dataset',\n",
            "     '800 hostel complaints with 13 features across categories like Mess, Electricity, Plumbing.'),\n",
            "    ('EDA',\n",
            "     'Category and numerical features (Students_Affected, Support_Count) show distinct distributions '\n",
            "     'across priority levels, suggesting predictive value.'),\n",
            "    ('NLP Preprocessing',\n",
            "     'Lowercasing, punctuation/number removal, stopword removal (standard + domain-specific), '\n",
            "     'and lemmatization reduced vocabulary size significantly.'),\n",
            "    ('TF-IDF',\n",
            "     'Bigrams captured multi-word concepts (e.g., \"water cooler\"). '\n",
            "     'Top features differ across priority classes.'),\n",
            "    ('Feature Engineering',\n",
            "     'Combined TF-IDF (text) + OneHotEncoded categorical + StandardScaled numerical '\n",
            "     'features into a single ColumnTransformer pipeline.'),\n",
            "    ('Model Training',\n",
            "     'Trained 4 classifiers: Logistic Regression, Random Forest, Linear SVM, Multinomial Naive Bayes.'),\n",
            "    ('Best Model',\n",
            "     f'{best_tuned_name} achieved the highest weighted F1-Score of {best_tuned_f1:.4f} after tuning.'),\n",
            "    ('Cross-Validation',\n",
            "     '5-fold stratified CV confirmed consistent performance. GridSearchCV tuned the C parameter.'),\n",
            "    ('Deployment Ready',\n",
            "     'Final pipeline saved with joblib. predict_priority() function demonstrates real-time inference.')\n",
            "]\n",
            "\n",
            "print('KEY FINDINGS')\n",
            "print('=' * 75)\n",
            "for i, (topic, finding) in enumerate(findings, 1):\n",
            "    print(f'\\n{i}. {topic}:')\n",
            "    print(f'   {finding}')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 14.4 - Limitations"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "The following limitations apply to this project:\n",
            "\n",
            "| # | Limitation | Impact |\n",
            "|---|---|---|\n",
            "| 1 | **Dataset size** — 800 complaints is a relatively small dataset | Larger datasets would produce more reliable and generalizable models |\n",
            "| 2 | **Single data source** — the dataset is from one hostel context | The model may not generalize well to complaints from very different hostels or phrasing styles |\n",
            "| 3 | **Subjective labels** — priority labels were assigned by annotators | Different annotators might assign different priorities to the same complaint |\n",
            "| 4 | **TF-IDF limitations** — does not capture word order or semantic meaning | Words like 'broken' and 'damaged' are treated as separate features despite similar meaning |\n",
            "| 5 | **No temporal analysis** — complaint date is not used | Seasonal patterns or time-of-year effects on complaint types are not captured |\n",
            "| 6 | **Naive Bayes feature constraint** — Multinomial NB required non-negative features | NB was trained on TF-IDF only, making its comparison with other models approximate |\n",
            "| 7 | **Single train-test split** — initial evaluation was on one 80/20 split | Cross-validation partially addresses this, but a larger dataset would be more reliable |\n",
            "| 8 | **No real-time retraining** — the saved model does not update with new complaints | In production, the model would need periodic retraining as new complaint data accumulates |"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 14.5 - Future Scope"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "The following improvements and extensions can enhance this system in future work:\n",
            "\n",
            "| # | Future Direction | Benefit |\n",
            "|---|---|---|\n",
            "| 1 | **Word Embeddings (Word2Vec, GloVe)** | Capture semantic similarity between words — 'broken' and 'damaged' would have similar vectors |\n",
            "| 2 | **Transformer Models (BERT)** | Context-aware text representations for significantly better NLP accuracy |\n",
            "| 3 | **Larger and more diverse dataset** | Improve generalization across different hostels, regions, and complaint styles |\n",
            "| 4 | **Multi-label classification** | Some complaints span multiple categories and priorities simultaneously |\n",
            "| 5 | **Flask/FastAPI web API** | Wrap the saved model in a REST API for integration with hostel management software |\n",
            "| 6 | **Active Learning** | Allow hostel staff to correct predictions, which are fed back to retrain the model |\n",
            "| 7 | **IoT Integration** | Combine the NLP module with the IoT water level monitoring module for a unified dashboard |\n",
            "| 8 | **Explainability (SHAP/LIME)** | Explain individual predictions to hostel management — which words drove a High priority classification |\n",
            "| 9 | **Multilingual Support** | Handle complaints in regional languages using multilingual BERT or translation preprocessing |"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 14.6 - Viva Question Bank\n",
            "\n",
            "Below are common questions that may be asked during a B.Tech project viva, along with concise answers."
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "**Q1. What is TF-IDF and why did you use it?**\n",
            "> TF-IDF (Term Frequency-Inverse Document Frequency) converts text into numbers. TF measures how often a word appears in one document; IDF measures how rare it is across all documents. The product gives a score that is high for words distinctive to a specific document. We used it because it is fast, interpretable, and works well for text classification with moderate-sized datasets.\n",
            "\n",
            "---\n",
            "\n",
            "**Q2. What is the difference between Logistic Regression and SVM?**\n",
            "> Logistic Regression models the probability of each class using a sigmoid/softmax function and finds the decision boundary that maximizes likelihood. SVM finds the decision boundary that maximizes the margin (distance) between classes. For high-dimensional text data, both work well. SVM is generally more robust to high-dimensional sparse features.\n",
            "\n",
            "---\n",
            "\n",
            "**Q3. Why did you choose F1-Score as the primary metric?**\n",
            "> In a multi-class classification problem, accuracy can be misleading if classes are imbalanced. F1-Score is the harmonic mean of Precision and Recall, so it penalizes models that sacrifice one for the other. For complaint prioritization, both missing a High-priority complaint (low Recall) and falsely flagging Low-priority complaints as High (low Precision) have real consequences.\n",
            "\n",
            "---\n",
            "\n",
            "**Q4. What is data leakage and how did you prevent it?**\n",
            "> Data leakage occurs when information from the test set influences the training process, leading to overly optimistic evaluation. We prevented it by: (1) splitting data BEFORE applying any transformation, (2) using `fit_transform` only on training data and `transform` on test data, (3) excluding the `Status` column which is determined after priority is assigned, and (4) using Pipeline inside cross-validation so preprocessing is re-fitted at each fold.\n",
            "\n",
            "---\n",
            "\n",
            "**Q5. What is the Naive assumption in Naive Bayes?**\n",
            "> Naive Bayes assumes all features are conditionally independent given the class label. In text, this means it assumes each word in a complaint is independent of all other words given the priority class. This is not true in reality (words co-occur in meaningful patterns), but despite this simplification, Naive Bayes performs well in practice for text classification.\n",
            "\n",
            "---\n",
            "\n",
            "**Q6. What is cross-validation and why is it better than a single train-test split?**\n",
            "> Cross-validation divides the data into K folds and trains/evaluates the model K times, each time using a different fold as the test set. It then averages the K scores. This gives a more reliable performance estimate because it reduces the dependence on which specific data points ended up in the test set. A single split might be lucky or unlucky in its composition.\n",
            "\n",
            "---\n",
            "\n",
            "**Q7. Why did you use ColumnTransformer?**\n",
            "> Different feature types require different preprocessing. TF-IDF is needed for text, OneHotEncoding for categorical features, and StandardScaler for numerical features. ColumnTransformer applies the right transformation to each column type in a single, clean pipeline. This prevents manual concatenation errors and ensures consistent preprocessing during both training and prediction.\n",
            "\n",
            "---\n",
            "\n",
            "**Q8. What would you improve if you had more time?**\n",
            "> I would explore BERT or other transformer-based text representations for better semantic understanding, collect more diverse training data, implement an active learning loop where staff corrections improve the model over time, and build a Flask API to integrate the model with the hostel's complaint management system."
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 14.7 - Project Summary Statistics"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ============================================================\n",
            "# 14.7  PROJECT SUMMARY STATISTICS\n",
            "# ============================================================\n",
            "\n",
            "import os\n",
            "\n",
            "# Count saved PNG files\n",
            "png_files = [f for f in os.listdir('.') if f.endswith('.png')]\n",
            "\n",
            "print('PROJECT SUMMARY')\n",
            "print('=' * 60)\n",
            "print(f'  Dataset size          : 800 complaints')\n",
            "print(f'  Features              : 13 original columns')\n",
            "print(f'  Target classes        : 3 (High, Medium, Low)')\n",
            "print(f'  Training samples      : {len(X_train_raw)}')\n",
            "print(f'  Test samples          : {len(X_test_raw)}')\n",
            "print(f'  TF-IDF features       : 1000 (max)')\n",
            "print(f'  NLP preprocessing     : 6 steps + custom domain stopwords')\n",
            "print(f'  Models trained        : 4 (LR, RF, SVM, Naive Bayes)')\n",
            "print(f'  Best model            : {best_tuned_name}')\n",
            "print(f'  Best F1-Score         : {best_tuned_f1:.4f}')\n",
            "print(f'  CV folds              : 5 (StratifiedKFold)')\n",
            "print(f'  Saved artifacts       : 4 (model + encoder + stopwords + metadata)')\n",
            "print(f'  Visualizations saved  : {len(png_files)} PNG files')\n",
            "print('=' * 60)\n",
            "print('\\nProject complete!')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "## PROJECT COMPLETE\n",
            "\n",
            "### AI-Based Hostel Complaint Prioritization System\n",
            "**B.Tech Mini Project | Machine Learning Module**\n",
            "\n",
            "---\n",
            "\n",
            "### Sections Completed:\n",
            "\n",
            "| Section | Title | Status |\n",
            "|---|---|---|\n",
            "| 1 | Setup & Data Loading | Done |\n",
            "| 2 | Exploratory Data Analysis (EDA) | Done |\n",
            "| 3 | NLP Preprocessing | Done |\n",
            "| 4 | TF-IDF Vectorization | Done |\n",
            "| 5 | Feature Engineering & Combining | Done |\n",
            "| 6 | Train-Test Split & Logistic Regression | Done |\n",
            "| 7 | Random Forest Classifier | Done |\n",
            "| 8 | Linear SVM (LinearSVC) | Done |\n",
            "| 9 | Multinomial Naive Bayes | Done |\n",
            "| 10 | Model Comparison | Done |\n",
            "| 11 | Cross-Validation & Hyperparameter Tuning | Done |\n",
            "| 12 | Save the Model | Done |\n",
            "| 13 | Predict New Complaints | Done |\n",
            "| 14 | Project Conclusions | Done |\n",
            "\n",
            "---\n",
            "\n",
            "### Core Technologies Used:\n",
            "- **Python** — scikit-learn, pandas, numpy, matplotlib, seaborn\n",
            "- **NLP** — NLTK (stopwords, lemmatization), TF-IDF (scikit-learn)\n",
            "- **ML Algorithms** — Logistic Regression, Random Forest, LinearSVC, MultinomialNB\n",
            "- **Pipeline** — ColumnTransformer, sklearn Pipeline, GridSearchCV\n",
            "- **Persistence** — joblib\n",
            "\n",
            "---\n",
            "\n",
            "> **Note on Interpretations:** All observations in this notebook are strictly evidence-based. Conclusions are drawn only from data and model outputs. Where causation cannot be determined, it has been clearly stated as a limitation."
        ]
    }
]

nb['cells'].extend(section14_cells)

with open('hostel_complaint_prioritization.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f'Section 14 added! Total cells: {len(nb["cells"])}')
print('PROJECT NOTEBOOK COMPLETE!')
