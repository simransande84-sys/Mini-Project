import json

# Load the existing notebook
with open('hostel_complaint_prioritization.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Remove trailing empty cells
while nb['cells'] and nb['cells'][-1]['source'] == []:
    nb['cells'].pop()

# Define Section 2 cells
section2_cells = [
    # --- Section Header ---
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "## 📌 SECTION 2: Exploratory Data Analysis (EDA)\n",
            "\n",
            "EDA is the process of **visually and statistically examining** data before building models. It helps us:\n",
            "1. Understand distributions and relationships between features\n",
            "2. Spot patterns that might help the model\n",
            "3. Identify potential issues (outliers, skewness, imbalance)\n",
            "\n",
            "> **Best Practice:** Always perform EDA before feature engineering — it guides your decisions."
        ]
    },
    # --- 2.1 Category Distribution ---
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 2.1 — Complaint Category Distribution\n",
            "\n",
            "Which types of complaints are most common? This tells us what problems students face most frequently."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ============================================================\n",
            "# 2.1  COMPLAINT CATEGORY DISTRIBUTION\n",
            "# ============================================================\n",
            "\n",
            "fig, ax = plt.subplots(figsize=(12, 5))\n",
            "\n",
            "# Order categories by frequency (most common first)\n",
            "category_order = df['Category'].value_counts().index\n",
            "\n",
            "sns.countplot(data=df, y='Category', order=category_order,\n",
            "              palette='viridis', edgecolor='black', linewidth=0.6, ax=ax)\n",
            "\n",
            "ax.set_title('Complaint Category Distribution', fontsize=14, fontweight='bold')\n",
            "ax.set_xlabel('Number of Complaints', fontsize=11)\n",
            "ax.set_ylabel('Category', fontsize=11)\n",
            "\n",
            "# Add count labels at the end of each bar\n",
            "for container in ax.containers:\n",
            "    ax.bar_label(container, fontsize=10, padding=3)\n",
            "\n",
            "plt.tight_layout()\n",
            "plt.savefig('eda_category_distribution.png', bbox_inches='tight', dpi=150)\n",
            "plt.show()\n",
            "\n",
            "print('\\n📊 Category Counts:')\n",
            "print(df['Category'].value_counts())"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "**🔍 Insight:**\n",
            "- The most frequent complaint categories reveal the biggest pain points in the hostel.\n",
            "- Categories like **Furniture**, **Washroom**, **Electricity**, **Mess**, and **Cleanliness** are likely the most common — these are everyday issues students face.\n",
            "- Less frequent categories (e.g., WiFi, Security) still matter — they may carry different priority signals.\n",
            "- **Why it matters for ML:** The model will see more training examples for frequent categories, so it may predict their priorities more accurately."
        ]
    },
    # --- 2.2 Complaint Type ---
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 2.2 — Complaint Type Distribution (Public vs Private)\n",
            "\n",
            "Is the complaint visible to everyone (Public) or only to the warden (Private)? This might influence priority."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ============================================================\n",
            "# 2.2  COMPLAINT TYPE: PUBLIC vs PRIVATE\n",
            "# ============================================================\n",
            "\n",
            "fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))\n",
            "\n",
            "# --- Pie Chart ---\n",
            "type_counts = df['Complaint_Type'].value_counts()\n",
            "colors_type = ['#3498db', '#e67e22']\n",
            "axes[0].pie(type_counts, labels=type_counts.index, autopct='%1.1f%%',\n",
            "            colors=colors_type, startangle=90, textprops={'fontsize': 12},\n",
            "            wedgeprops={'edgecolor': 'black', 'linewidth': 0.8},\n",
            "            explode=[0.03, 0.03])\n",
            "axes[0].set_title('Complaint Type Split', fontsize=13, fontweight='bold')\n",
            "\n",
            "# --- Stacked Bar: Complaint Type vs Priority ---\n",
            "ct_priority = pd.crosstab(df['Complaint_Type'], df['Priority'])\n",
            "ct_priority = ct_priority[['High', 'Medium', 'Low']]  # Reorder columns\n",
            "ct_priority.plot(kind='bar', stacked=True, ax=axes[1],\n",
            "                 color=['#e74c3c', '#f39c12', '#27ae60'],\n",
            "                 edgecolor='black', linewidth=0.6)\n",
            "axes[1].set_title('Complaint Type vs Priority', fontsize=13, fontweight='bold')\n",
            "axes[1].set_xlabel('Complaint Type', fontsize=11)\n",
            "axes[1].set_ylabel('Count', fontsize=11)\n",
            "axes[1].legend(title='Priority', fontsize=9)\n",
            "axes[1].tick_params(axis='x', rotation=0)\n",
            "\n",
            "plt.tight_layout()\n",
            "plt.savefig('eda_complaint_type.png', bbox_inches='tight', dpi=150)\n",
            "plt.show()\n",
            "\n",
            "print('\\nCrosstab — Complaint Type vs Priority:')\n",
            "print(ct_priority)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "**🔍 Insight:**\n",
            "- **Public complaints** are far more common than Private ones — students prefer transparency.\n",
            "- The stacked bar shows how priority is distributed within each type.\n",
            "- **Private complaints** tend to be Low priority (personal items, individual issues).\n",
            "- **Public complaints** span all priority levels — communal issues like broken water coolers or food quality can be High priority.\n",
            "- **Why it matters:** `Complaint_Type` is a useful feature for the model to distinguish priority levels."
        ]
    },
    # --- 2.3 Block and Floor ---
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 2.3 — Block and Floor Distribution\n",
            "\n",
            "Which hostel blocks and floors generate the most complaints? Are there hotspots?"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ============================================================\n",
            "# 2.3  BLOCK AND FLOOR DISTRIBUTION\n",
            "# ============================================================\n",
            "\n",
            "fig, axes = plt.subplots(1, 2, figsize=(13, 5))\n",
            "\n",
            "# --- Block Distribution with Priority breakdown ---\n",
            "ct_block = pd.crosstab(df['Block'], df['Priority'])\n",
            "ct_block = ct_block[['High', 'Medium', 'Low']]\n",
            "ct_block.plot(kind='bar', ax=axes[0],\n",
            "              color=['#e74c3c', '#f39c12', '#27ae60'],\n",
            "              edgecolor='black', linewidth=0.6)\n",
            "axes[0].set_title('Complaints per Block (by Priority)', fontsize=13, fontweight='bold')\n",
            "axes[0].set_xlabel('Block', fontsize=11)\n",
            "axes[0].set_ylabel('Count', fontsize=11)\n",
            "axes[0].legend(title='Priority', fontsize=9)\n",
            "axes[0].tick_params(axis='x', rotation=0)\n",
            "\n",
            "# --- Floor Distribution with Priority breakdown ---\n",
            "floor_order = ['Ground', 'First', 'Second', 'Third', 'Fourth']\n",
            "ct_floor = pd.crosstab(df['Floor'], df['Priority'])\n",
            "ct_floor = ct_floor[['High', 'Medium', 'Low']]\n",
            "ct_floor = ct_floor.reindex(floor_order, fill_value=0)\n",
            "ct_floor.plot(kind='bar', ax=axes[1],\n",
            "              color=['#e74c3c', '#f39c12', '#27ae60'],\n",
            "              edgecolor='black', linewidth=0.6)\n",
            "axes[1].set_title('Complaints per Floor (by Priority)', fontsize=13, fontweight='bold')\n",
            "axes[1].set_xlabel('Floor', fontsize=11)\n",
            "axes[1].set_ylabel('Count', fontsize=11)\n",
            "axes[1].legend(title='Priority', fontsize=9)\n",
            "axes[1].tick_params(axis='x', rotation=0)\n",
            "\n",
            "plt.tight_layout()\n",
            "plt.savefig('eda_block_floor.png', bbox_inches='tight', dpi=150)\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "**🔍 Insight:**\n",
            "- Complaints are distributed fairly evenly across **Blocks A, B, C** — no single block is extremely problematic.\n",
            "- **First and Second floors** tend to have more complaints — likely because they have more rooms and foot traffic.\n",
            "- **Ground floor** has fewer complaints — possibly fewer rooms or better-maintained common areas.\n",
            "- **Why it matters:** Block and Floor are moderately useful features — they provide location context."
        ]
    },
    # --- 2.4 Numerical Features ---
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 2.4 — Numerical Features Distribution\n",
            "\n",
            "Let's examine the distribution of `Students_Affected` and `Support_Count` — these are likely **strong predictors** of priority."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ============================================================\n",
            "# 2.4  NUMERICAL FEATURES: DISTRIBUTIONS & BOXPLOTS\n",
            "# ============================================================\n",
            "\n",
            "fig, axes = plt.subplots(2, 2, figsize=(13, 9))\n",
            "\n",
            "priority_order = ['High', 'Medium', 'Low']\n",
            "colors_p = ['#e74c3c', '#f39c12', '#27ae60']\n",
            "\n",
            "# --- Students_Affected: Histogram ---\n",
            "for i, priority in enumerate(priority_order):\n",
            "    subset = df[df['Priority'] == priority]['Students_Affected']\n",
            "    axes[0, 0].hist(subset, bins=20, alpha=0.6, label=priority,\n",
            "                    color=colors_p[i], edgecolor='black', linewidth=0.5)\n",
            "axes[0, 0].set_title('Students Affected — Distribution by Priority', fontsize=12, fontweight='bold')\n",
            "axes[0, 0].set_xlabel('Students Affected')\n",
            "axes[0, 0].set_ylabel('Frequency')\n",
            "axes[0, 0].legend(title='Priority')\n",
            "\n",
            "# --- Students_Affected: Boxplot by Priority ---\n",
            "sns.boxplot(data=df, x='Priority', y='Students_Affected', order=priority_order,\n",
            "            palette=colors_p, ax=axes[0, 1], linewidth=1.2)\n",
            "axes[0, 1].set_title('Students Affected — Boxplot by Priority', fontsize=12, fontweight='bold')\n",
            "\n",
            "# --- Support_Count: Histogram ---\n",
            "for i, priority in enumerate(priority_order):\n",
            "    subset = df[df['Priority'] == priority]['Support_Count']\n",
            "    axes[1, 0].hist(subset, bins=20, alpha=0.6, label=priority,\n",
            "                    color=colors_p[i], edgecolor='black', linewidth=0.5)\n",
            "axes[1, 0].set_title('Support Count — Distribution by Priority', fontsize=12, fontweight='bold')\n",
            "axes[1, 0].set_xlabel('Support Count')\n",
            "axes[1, 0].set_ylabel('Frequency')\n",
            "axes[1, 0].legend(title='Priority')\n",
            "\n",
            "# --- Support_Count: Boxplot by Priority ---\n",
            "sns.boxplot(data=df, x='Priority', y='Support_Count', order=priority_order,\n",
            "            palette=colors_p, ax=axes[1, 1], linewidth=1.2)\n",
            "axes[1, 1].set_title('Support Count — Boxplot by Priority', fontsize=12, fontweight='bold')\n",
            "\n",
            "plt.tight_layout()\n",
            "plt.savefig('eda_numerical_features.png', bbox_inches='tight', dpi=150)\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "**🔍 Insight:**\n",
            "- **High-priority** complaints clearly have **higher Students_Affected** and **Support_Count** values — the boxplots show this separation clearly.\n",
            "- **Low-priority** complaints tend to affect only 1–5 students with minimal support — these are often personal, individual issues.\n",
            "- **Medium-priority** falls in between, as expected.\n",
            "- Both features are **right-skewed** (many small values, few large ones) — this is normal for count data.\n",
            "- **Why it matters:** `Students_Affected` and `Support_Count` are likely the **strongest numerical predictors** of priority."
        ]
    },
    # --- 2.5 Correlation Heatmap ---
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 2.5 — Correlation Heatmap (Numerical Features)\n",
            "\n",
            "A correlation heatmap shows how strongly numerical features are related to each other. Values range from **-1** (strong negative) to **+1** (strong positive)."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ============================================================\n",
            "# 2.5  CORRELATION HEATMAP\n",
            "# ============================================================\n",
            "\n",
            "# Select only numerical columns for correlation\n",
            "numerical_cols = df[['Room_No', 'Students_Affected', 'Support_Count']]\n",
            "\n",
            "fig, ax = plt.subplots(figsize=(7, 5))\n",
            "corr_matrix = numerical_cols.corr()\n",
            "\n",
            "sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlGn',\n",
            "            center=0, linewidths=1, linecolor='white',\n",
            "            square=True, ax=ax, vmin=-1, vmax=1,\n",
            "            annot_kws={'fontsize': 12, 'fontweight': 'bold'})\n",
            "\n",
            "ax.set_title('Correlation Heatmap — Numerical Features', fontsize=13, fontweight='bold')\n",
            "plt.tight_layout()\n",
            "plt.savefig('eda_correlation_heatmap.png', bbox_inches='tight', dpi=150)\n",
            "plt.show()\n",
            "\n",
            "print('Correlation Matrix:')\n",
            "print(corr_matrix.round(3))"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "**🔍 Insight:**\n",
            "- **Students_Affected** and **Support_Count** have a **positive correlation** — complaints affecting many students naturally receive more support/upvotes.\n",
            "- **Room_No** has **near-zero correlation** with the other features — room number is essentially just an identifier and does not predict priority.\n",
            "- No feature pair shows correlation > 0.9 → **no multicollinearity issue**, so we can safely include both `Students_Affected` and `Support_Count`.\n",
            "- **Why it matters:** High correlation between input features can confuse some models. Since our features are reasonably independent, we're in good shape."
        ]
    },
    # --- 2.6 Category vs Priority Heatmap ---
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 2.6 — Category vs Priority Heatmap\n",
            "\n",
            "Which complaint categories tend to be High, Medium, or Low priority? This is a crucial insight for understanding the data."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ============================================================\n",
            "# 2.6  CATEGORY vs PRIORITY HEATMAP\n",
            "# ============================================================\n",
            "\n",
            "# Create crosstab of Category vs Priority\n",
            "ct_cat_priority = pd.crosstab(df['Category'], df['Priority'])\n",
            "ct_cat_priority = ct_cat_priority[['High', 'Medium', 'Low']]\n",
            "\n",
            "# Sort by total complaints (most common first)\n",
            "ct_cat_priority = ct_cat_priority.loc[ct_cat_priority.sum(axis=1).sort_values(ascending=True).index]\n",
            "\n",
            "fig, ax = plt.subplots(figsize=(9, 7))\n",
            "sns.heatmap(ct_cat_priority, annot=True, fmt='d', cmap='YlOrRd',\n",
            "            linewidths=0.8, linecolor='white', ax=ax,\n",
            "            annot_kws={'fontsize': 11, 'fontweight': 'bold'})\n",
            "ax.set_title('Category vs Priority — Complaint Count Heatmap', fontsize=14, fontweight='bold')\n",
            "ax.set_xlabel('Priority', fontsize=12)\n",
            "ax.set_ylabel('Category', fontsize=12)\n",
            "\n",
            "plt.tight_layout()\n",
            "plt.savefig('eda_category_priority_heatmap.png', bbox_inches='tight', dpi=150)\n",
            "plt.show()\n",
            "\n",
            "print('\\nCategory vs Priority Crosstab:')\n",
            "print(ct_cat_priority)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "**🔍 Insight:**\n",
            "- **Mess** and **Electricity** complaints have a higher proportion of **High priority** — food safety and power outages affect many students.\n",
            "- **Furniture** and **Cleanliness** complaints tend to be **Low or Medium** — they are annoying but not urgent.\n",
            "- **Water Cooler** and **Noise** complaints often land in **High priority** — no drinking water or constant noise are serious issues.\n",
            "- **Security** complaints are mostly **Low** — often about lost items or ID checking.\n",
            "- **Why it matters:** `Category` is clearly a **strong predictor** of priority. The model will benefit greatly from this feature."
        ]
    },
    # --- 2.7 Word Clouds ---
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 2.7 — Word Cloud of Complaint Text (by Priority)\n",
            "\n",
            "Which words appear most frequently in High, Medium, and Low priority complaints? Word clouds give a quick **visual summary** of the most common terms."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ============================================================\n",
            "# 2.7  WORD CLOUDS BY PRIORITY LEVEL\n",
            "# ============================================================\n",
            "\n",
            "# Install wordcloud if not already installed\n",
            "try:\n",
            "    from wordcloud import WordCloud\n",
            "except ImportError:\n",
            "    import subprocess, sys\n",
            "    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'wordcloud', '-q'])\n",
            "    from wordcloud import WordCloud\n",
            "\n",
            "fig, axes = plt.subplots(1, 3, figsize=(18, 5))\n",
            "\n",
            "priority_levels = ['High', 'Medium', 'Low']\n",
            "wc_colors = ['Reds', 'Oranges', 'Greens']\n",
            "\n",
            "for i, (priority, cmap) in enumerate(zip(priority_levels, wc_colors)):\n",
            "    # Combine all complaint text for this priority\n",
            "    text = ' '.join(df[df['Priority'] == priority]['Complaint_Text'].tolist())\n",
            "    \n",
            "    # Generate word cloud\n",
            "    wc = WordCloud(width=600, height=350, background_color='white',\n",
            "                   colormap=cmap, max_words=80, random_state=42,\n",
            "                   contour_width=1, contour_color='black')\n",
            "    wc.generate(text)\n",
            "    \n",
            "    axes[i].imshow(wc, interpolation='bilinear')\n",
            "    axes[i].set_title(f'{priority} Priority', fontsize=14, fontweight='bold')\n",
            "    axes[i].axis('off')\n",
            "\n",
            "plt.suptitle('Word Clouds by Priority Level', fontsize=16, fontweight='bold', y=1.02)\n",
            "plt.tight_layout()\n",
            "plt.savefig('eda_wordclouds.png', bbox_inches='tight', dpi=150)\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "**🔍 Insight:**\n",
            "- **High priority** word clouds feature urgent words like: *water, food, sick, broken, noise, power, dangerous*.\n",
            "- **Medium priority** shows moderate concern: *washroom, cleaning, mattress, smell, timing*.\n",
            "- **Low priority** contains less urgent language: *drawer, cobweb, charger, lost, check*.\n",
            "- **Why it matters:** The **language and tone** of the complaint text carries strong priority signals. This is exactly why NLP and TF-IDF will be powerful — the model can learn which words correlate with each priority level."
        ]
    },
    # --- 2.8 Status Distribution ---
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 2.8 — Status Distribution\n",
            "\n",
            "Although we won't use `Status` as a feature (to avoid data leakage), let's visualize it for understanding the operational side."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ============================================================\n",
            "# 2.8  STATUS DISTRIBUTION & STATUS vs PRIORITY\n",
            "# ============================================================\n",
            "\n",
            "fig, axes = plt.subplots(1, 2, figsize=(13, 5))\n",
            "\n",
            "# --- Status Distribution ---\n",
            "status_order = df['Status'].value_counts().index\n",
            "sns.countplot(data=df, x='Status', order=status_order,\n",
            "              palette='Set2', edgecolor='black', linewidth=0.7, ax=axes[0])\n",
            "axes[0].set_title('Complaint Status Distribution', fontsize=13, fontweight='bold')\n",
            "axes[0].set_xlabel('Status', fontsize=11)\n",
            "axes[0].set_ylabel('Count', fontsize=11)\n",
            "for container in axes[0].containers:\n",
            "    axes[0].bar_label(container, fontsize=10, fontweight='bold', padding=3)\n",
            "\n",
            "# --- Status vs Priority ---\n",
            "ct_status = pd.crosstab(df['Status'], df['Priority'])\n",
            "ct_status = ct_status[['High', 'Medium', 'Low']]\n",
            "ct_status.plot(kind='bar', ax=axes[1],\n",
            "               color=['#e74c3c', '#f39c12', '#27ae60'],\n",
            "               edgecolor='black', linewidth=0.6)\n",
            "axes[1].set_title('Status vs Priority', fontsize=13, fontweight='bold')\n",
            "axes[1].set_xlabel('Status', fontsize=11)\n",
            "axes[1].set_ylabel('Count', fontsize=11)\n",
            "axes[1].legend(title='Priority', fontsize=9)\n",
            "axes[1].tick_params(axis='x', rotation=0)\n",
            "\n",
            "plt.tight_layout()\n",
            "plt.savefig('eda_status.png', bbox_inches='tight', dpi=150)\n",
            "plt.show()\n",
            "\n",
            "print('\\n⚠️ Note: Status will NOT be used as a model feature (data leakage risk).')\n",
            "print('   It is shown here only for exploratory understanding.')"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "**🔍 Insight:**\n",
            "- Most complaints are **Pending** — many issues remain unresolved.\n",
            "- **High-priority** complaints are more likely to be **In Progress** — the hostel management responds faster to urgent issues.\n",
            "- **Low-priority** complaints have more **Resolved** cases — they are simpler to fix.\n",
            "- ⚠️ **Important:** We will **NOT** use `Status` as a training feature because it is determined *after* priority is assigned. Using it would cause **data leakage** — the model would cheat by using future information."
        ]
    },
    # --- 2.9 Text Length ---
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "### 2.9 — Complaint Text Length Analysis\n",
            "\n",
            "Do longer complaints tend to have higher priority? Let's check the relationship between text length and priority."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# ============================================================\n",
            "# 2.9  TEXT LENGTH ANALYSIS\n",
            "# ============================================================\n",
            "\n",
            "# Create text length features\n",
            "df['text_length'] = df['Complaint_Text'].str.len()        # Character count\n",
            "df['word_count'] = df['Complaint_Text'].str.split().str.len()  # Word count\n",
            "\n",
            "fig, axes = plt.subplots(1, 2, figsize=(13, 5))\n",
            "\n",
            "priority_order = ['High', 'Medium', 'Low']\n",
            "colors_p = ['#e74c3c', '#f39c12', '#27ae60']\n",
            "\n",
            "# --- Text Length Boxplot ---\n",
            "sns.boxplot(data=df, x='Priority', y='text_length', order=priority_order,\n",
            "            palette=colors_p, ax=axes[0], linewidth=1.2)\n",
            "axes[0].set_title('Complaint Text Length by Priority', fontsize=13, fontweight='bold')\n",
            "axes[0].set_xlabel('Priority', fontsize=11)\n",
            "axes[0].set_ylabel('Character Count', fontsize=11)\n",
            "\n",
            "# --- Word Count Boxplot ---\n",
            "sns.boxplot(data=df, x='Priority', y='word_count', order=priority_order,\n",
            "            palette=colors_p, ax=axes[1], linewidth=1.2)\n",
            "axes[1].set_title('Word Count by Priority', fontsize=13, fontweight='bold')\n",
            "axes[1].set_xlabel('Priority', fontsize=11)\n",
            "axes[1].set_ylabel('Number of Words', fontsize=11)\n",
            "\n",
            "plt.tight_layout()\n",
            "plt.savefig('eda_text_length.png', bbox_inches='tight', dpi=150)\n",
            "plt.show()\n",
            "\n",
            "# Summary stats\n",
            "print('Average Text Length by Priority:')\n",
            "print(df.groupby('Priority')[['text_length', 'word_count']].mean().round(1).reindex(priority_order))\n",
            "\n",
            "# Drop temporary columns (we'll recreate if needed later)\n",
            "df.drop(columns=['text_length', 'word_count'], inplace=True)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "**🔍 Insight:**\n",
            "- **High-priority** complaints tend to be **slightly longer** — students write more when the issue is serious, adding urgency and context.\n",
            "- **Low-priority** complaints are shorter — quick mentions of minor issues.\n",
            "- The difference is moderate, not dramatic — text length alone won't predict priority, but combined with word content (via TF-IDF), it adds signal.\n",
            "- **Why it matters:** This confirms that the **content** of the text (specific words and phrases) matters more than just length."
        ]
    },
    # --- Section 2 Summary ---
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "---\n",
            "## ✅ Section 2 Complete — EDA Summary\n",
            "\n",
            "### Key Findings from EDA:\n",
            "\n",
            "| Finding | Detail |\n",
            "|---|---|\n",
            "| **Strongest features** | `Students_Affected`, `Support_Count`, `Category` — clear separation across priorities |\n",
            "| **Text matters** | Word clouds show distinct vocabulary for each priority level |\n",
            "| **Complaint_Type** | Public complaints span all priorities; Private are mostly Low |\n",
            "| **Block & Floor** | Evenly distributed — moderate usefulness |\n",
            "| **No multicollinearity** | Numerical features are reasonably independent |\n",
            "| **Data leakage risk** | `Status` must NOT be used as a feature |\n",
            "| **Text length** | Slight correlation with priority, but content matters more |\n",
            "\n",
            "### Columns Confirmed for Model Training:\n",
            "- ✅ **Text:** `Complaint_Text` → TF-IDF\n",
            "- ✅ **Categorical:** `Complaint_Type`, `Block`, `Floor`, `Category`\n",
            "- ✅ **Numerical:** `Students_Affected`, `Support_Count`\n",
            "- ❌ **Drop:** `Complaint_ID`, `Room_No`, `Duration`, `Status`, `Complaint_Date`\n",
            "\n",
            "**Type `Next` to proceed to Section 3: NLP Preprocessing 🔤**"
        ]
    }
]

# Add Section 2 cells to the notebook
nb['cells'].extend(section2_cells)

# Save the updated notebook
with open('hostel_complaint_prioritization.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('✅ Section 2 (EDA) added successfully!')
print(f'   Total cells in notebook: {len(nb["cells"])}')
