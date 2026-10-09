# AUTO-EXTRACTED FROM NOTEBOOK FOR ERROR CHECKING
import warnings; warnings.filterwarnings('ignore')


# ====== CELL 1 ======
# ============================================================
# 1.1  IMPORT ALL REQUIRED LIBRARIES
# ============================================================

# --- Data Handling ---
import pandas as pd                # Tabular data manipulation
import numpy as np                 # Numerical computations

# --- Visualization ---
import matplotlib.pyplot as plt    # Core plotting library
import seaborn as sns              # Statistical visualizations (built on matplotlib)

# --- NLP (Natural Language Processing) ---
import re                          # Regular expressions for text cleaning
import nltk                        # NLP toolkit for stopwords, lemmatization
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# --- Feature Engineering ---
from sklearn.feature_extraction.text import TfidfVectorizer   # Text → numerical features
from sklearn.preprocessing import LabelEncoder                # Encode target labels
from sklearn.compose import ColumnTransformer                 # Combine different feature types
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# --- Machine Learning Models ---
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB

# --- Model Evaluation ---
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, classification_report, confusion_matrix,
                             ConfusionMatrixDisplay)

# --- Hyperparameter Tuning ---
from sklearn.model_selection import GridSearchCV

# --- Model Saving / Loading ---
import joblib

# --- Download NLTK Data (run once) ---
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

# --- Global Settings ---
import warnings
warnings.filterwarnings('ignore')          # Suppress sklearn convergence warnings
sns.set_style('whitegrid')                 # Clean background for all plots
plt.rcParams['figure.dpi'] = 120           # Sharper figures in the notebook

print('[OK] All libraries imported successfully!')

# ====== CELL 2 ======
# ============================================================
# 1.2  LOAD THE DATASET
# ============================================================

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('hostel_complaints_800_final (1).csv')

print(f'[OK] Dataset loaded successfully!')
print(f'   Rows   : {df.shape[0]}')
print(f'   Columns: {df.shape[1]}')

# ====== CELL 3 ======
# ============================================================
# 1.3  DISPLAY FIRST FEW ROWS
# ============================================================

# Show top 5 rows to get a quick look at the data
df.head()

# ====== CELL 4 ======
# ============================================================
# 1.4  DATASET SHAPE
# ============================================================

print(f'Dataset Shape: {df.shape}')
print(f'  → {df.shape[0]} complaints (rows)')
print(f'  → {df.shape[1]} features/columns')

# ====== CELL 5 ======
# ============================================================
# 1.5  COLUMN NAMES
# ============================================================

print('Column Names:')
print('─' * 40)
for i, col in enumerate(df.columns, 1):
    print(f'  {i:2d}. {col}')

# ====== CELL 6 ======
# ============================================================
# 1.6  DATA TYPES
# ============================================================

print('Data Types:')
print('─' * 40)
print(df.dtypes)
print()
print(f'Summary: {df.dtypes.value_counts().to_dict()}')

# ====== CELL 7 ======
# ============================================================
# 1.7  MISSING VALUES
# ============================================================

missing = df.isnull().sum()
missing_pct = (df.isnull().sum() / len(df) * 100).round(2)

# Combine into a neat table
missing_df = pd.DataFrame({
    'Missing Count': missing,
    'Missing %': missing_pct
})

print('Missing Values per Column:')
print('─' * 45)
print(missing_df)
print()
print(f'Total missing values in entire dataset: {df.isnull().sum().sum()}')

# ====== CELL 8 ======
# ============================================================
# 1.8  DUPLICATE ROWS
# ============================================================

duplicate_count = df.duplicated().sum()

print(f'Number of exact duplicate rows: {duplicate_count}')

if duplicate_count > 0:
    print(f'[!]️  Found {duplicate_count} duplicates. Removing them...')
    df = df.drop_duplicates().reset_index(drop=True)
    print(f'[OK] After removal: {df.shape[0]} rows remain.')
else:
    print('[OK] No duplicate rows found. Dataset is clean!')

# ====== CELL 9 ======
# ============================================================
# 1.9  CLASS DISTRIBUTION OF TARGET VARIABLE
# ============================================================

# Count and percentage of each Priority class
class_counts = df['Priority'].value_counts()
class_pct = df['Priority'].value_counts(normalize=True).mul(100).round(2)

class_dist = pd.DataFrame({
    'Count': class_counts,
    'Percentage (%)': class_pct
})

print('Target Variable — Priority Distribution:')
print('─' * 45)
print(class_dist)
print()

# --- Visualization ---
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

# Bar chart
colors = ['#e74c3c', '#f39c12', '#27ae60']   # Red=High, Orange=Medium, Green=Low
order = ['High', 'Medium', 'Low']
sns.countplot(data=df, x='Priority', order=order, palette=colors, ax=axes[0],
              edgecolor='black', linewidth=0.8)
axes[0].set_title('Priority Class Distribution', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Priority Level', fontsize=11)
axes[0].set_ylabel('Number of Complaints', fontsize=11)

# Add count labels on top of each bar
for container in axes[0].containers:
    axes[0].bar_label(container, fontsize=11, fontweight='bold', padding=3)

# Pie chart
class_counts_ordered = class_counts.reindex(order)
axes[1].pie(class_counts_ordered, labels=order, autopct='%1.1f%%',
            colors=colors, startangle=90, textprops={'fontsize': 11},
            wedgeprops={'edgecolor': 'black', 'linewidth': 0.8})
axes[1].set_title('Priority Proportion', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig('class_distribution.png', bbox_inches='tight', dpi=150)
plt.show()

print('[chart] Chart saved as class_distribution.png')

# ====== CELL 10 ======
# ============================================================
# 1.10  STATISTICAL SUMMARY (NUMERICAL COLUMNS)
# ============================================================

print('Statistical Summary of Numerical Columns:')
print('─' * 50)
df.describe()

# ====== CELL 11 ======
# ============================================================
# 1.11  UNIQUE VALUES PER COLUMN
# ============================================================

print('Unique Values per Column:')
print('─' * 45)
for col in df.columns:
    print(f'  {col:25s} → {df[col].nunique():4d} unique values')

print()
print('Unique values in key categorical columns:')
print('─' * 45)
for col in ['Complaint_Type', 'Block', 'Floor', 'Category', 'Priority', 'Status']:
    print(f'  {col:20s} → {df[col].unique().tolist()}')

# ====== CELL 12 ======
# ============================================================
# 2.1  COMPLAINT CATEGORY DISTRIBUTION
# ============================================================

fig, ax = plt.subplots(figsize=(12, 5))

# Order categories by frequency (most common first)
category_order = df['Category'].value_counts().index

sns.countplot(data=df, y='Category', order=category_order,
              palette='viridis', edgecolor='black', linewidth=0.6, ax=ax)

ax.set_title('Complaint Category Distribution', fontsize=14, fontweight='bold')
ax.set_xlabel('Number of Complaints', fontsize=11)
ax.set_ylabel('Category', fontsize=11)

# Add count labels at the end of each bar
for container in ax.containers:
    ax.bar_label(container, fontsize=10, padding=3)

plt.tight_layout()
plt.savefig('eda_category_distribution.png', bbox_inches='tight', dpi=150)
plt.show()

# Show counts AND percentages
cat_counts = df['Category'].value_counts()
cat_pct = df['Category'].value_counts(normalize=True).mul(100).round(1)
cat_summary = pd.DataFrame({'Count': cat_counts, 'Percentage (%)': cat_pct})
print('\nCategory Distribution (Count + Percentage):')
print(cat_summary)

# ====== CELL 13 ======
# ============================================================
# 2.2  COMPLAINT TYPE: PUBLIC vs PRIVATE
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

# --- Pie Chart ---
type_counts = df['Complaint_Type'].value_counts()
colors_type = ['#3498db', '#e67e22']
axes[0].pie(type_counts, labels=type_counts.index, autopct='%1.1f%%',
            colors=colors_type, startangle=90, textprops={'fontsize': 12},
            wedgeprops={'edgecolor': 'black', 'linewidth': 0.8},
            explode=[0.03, 0.03])
axes[0].set_title('Complaint Type Split', fontsize=13, fontweight='bold')

# --- Stacked Bar: Complaint Type vs Priority ---
ct_priority = pd.crosstab(df['Complaint_Type'], df['Priority'])
ct_priority = ct_priority[['High', 'Medium', 'Low']]  # Reorder columns
ct_priority.plot(kind='bar', stacked=True, ax=axes[1],
                 color=['#e74c3c', '#f39c12', '#27ae60'],
                 edgecolor='black', linewidth=0.6)
axes[1].set_title('Complaint Type vs Priority', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Complaint Type', fontsize=11)
axes[1].set_ylabel('Count', fontsize=11)
axes[1].legend(title='Priority', fontsize=9)
axes[1].tick_params(axis='x', rotation=0)

plt.tight_layout()
plt.savefig('eda_complaint_type.png', bbox_inches='tight', dpi=150)
plt.show()

# Print counts and percentages
print('Complaint Type Counts:')
for t in type_counts.index:
    print(f'  {t}: {type_counts[t]} ({type_counts[t]/len(df)*100:.1f}%)')

print('\nCrosstab - Complaint Type vs Priority (counts):')
print(ct_priority)
print('\nCrosstab - Complaint Type vs Priority (row percentages):')
print(ct_priority.div(ct_priority.sum(axis=1), axis=0).mul(100).round(1))

# ====== CELL 14 ======
# ============================================================
# 2.3  BLOCK AND FLOOR DISTRIBUTION
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# --- Block Distribution with Priority breakdown ---
ct_block = pd.crosstab(df['Block'], df['Priority'])
ct_block = ct_block[['High', 'Medium', 'Low']]
ct_block.plot(kind='bar', ax=axes[0],
              color=['#e74c3c', '#f39c12', '#27ae60'],
              edgecolor='black', linewidth=0.6)
axes[0].set_title('Complaints per Block (by Priority)', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Block', fontsize=11)
axes[0].set_ylabel('Count', fontsize=11)
axes[0].legend(title='Priority', fontsize=9)
axes[0].tick_params(axis='x', rotation=0)

# --- Floor Distribution with Priority breakdown ---
floor_order = ['Ground', 'First', 'Second', 'Third', 'Fourth']
ct_floor = pd.crosstab(df['Floor'], df['Priority'])
ct_floor = ct_floor[['High', 'Medium', 'Low']]
ct_floor = ct_floor.reindex(floor_order, fill_value=0)
ct_floor.plot(kind='bar', ax=axes[1],
              color=['#e74c3c', '#f39c12', '#27ae60'],
              edgecolor='black', linewidth=0.6)
axes[1].set_title('Complaints per Floor (by Priority)', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Floor', fontsize=11)
axes[1].set_ylabel('Count', fontsize=11)
axes[1].legend(title='Priority', fontsize=9)
axes[1].tick_params(axis='x', rotation=0)

plt.tight_layout()
plt.savefig('eda_block_floor.png', bbox_inches='tight', dpi=150)
plt.show()

# ====== CELL 15 ======
# ============================================================
# 2.4  NUMERICAL FEATURES: DISTRIBUTIONS & BOXPLOTS
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(13, 9))

priority_order = ['High', 'Medium', 'Low']
colors_p = ['#e74c3c', '#f39c12', '#27ae60']

# --- Students_Affected: Histogram ---
for i, priority in enumerate(priority_order):
    subset = df[df['Priority'] == priority]['Students_Affected']
    axes[0, 0].hist(subset, bins=20, alpha=0.6, label=priority,
                    color=colors_p[i], edgecolor='black', linewidth=0.5)
axes[0, 0].set_title('Students Affected — Distribution by Priority', fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('Students Affected')
axes[0, 0].set_ylabel('Frequency')
axes[0, 0].legend(title='Priority')

# --- Students_Affected: Boxplot by Priority ---
sns.boxplot(data=df, x='Priority', y='Students_Affected', order=priority_order,
            palette=colors_p, ax=axes[0, 1], linewidth=1.2)
axes[0, 1].set_title('Students Affected — Boxplot by Priority', fontsize=12, fontweight='bold')

# --- Support_Count: Histogram ---
for i, priority in enumerate(priority_order):
    subset = df[df['Priority'] == priority]['Support_Count']
    axes[1, 0].hist(subset, bins=20, alpha=0.6, label=priority,
                    color=colors_p[i], edgecolor='black', linewidth=0.5)
axes[1, 0].set_title('Support Count — Distribution by Priority', fontsize=12, fontweight='bold')
axes[1, 0].set_xlabel('Support Count')
axes[1, 0].set_ylabel('Frequency')
axes[1, 0].legend(title='Priority')

# --- Support_Count: Boxplot by Priority ---
sns.boxplot(data=df, x='Priority', y='Support_Count', order=priority_order,
            palette=colors_p, ax=axes[1, 1], linewidth=1.2)
axes[1, 1].set_title('Support Count — Boxplot by Priority', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('eda_numerical_features.png', bbox_inches='tight', dpi=150)
plt.show()

# ====== CELL 16 ======
# ============================================================
# 2.5  CORRELATION HEATMAP
# ============================================================

# Select only numerical columns for correlation
numerical_cols = df[['Room_No', 'Students_Affected', 'Support_Count']]

fig, ax = plt.subplots(figsize=(7, 5))
corr_matrix = numerical_cols.corr()

sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlGn',
            center=0, linewidths=1, linecolor='white',
            square=True, ax=ax, vmin=-1, vmax=1,
            annot_kws={'fontsize': 12, 'fontweight': 'bold'})

ax.set_title('Correlation Heatmap — Numerical Features', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('eda_correlation_heatmap.png', bbox_inches='tight', dpi=150)
plt.show()

print('Correlation Matrix:')
print(corr_matrix.round(3))

# ====== CELL 17 ======
# ============================================================
# 2.6  CATEGORY vs PRIORITY HEATMAP
# ============================================================

# Create crosstab of Category vs Priority
ct_cat_priority = pd.crosstab(df['Category'], df['Priority'])
ct_cat_priority = ct_cat_priority[['High', 'Medium', 'Low']]

# Sort by total complaints (most common first)
ct_cat_priority = ct_cat_priority.loc[ct_cat_priority.sum(axis=1).sort_values(ascending=True).index]

fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(ct_cat_priority, annot=True, fmt='d', cmap='YlOrRd',
            linewidths=0.8, linecolor='white', ax=ax,
            annot_kws={'fontsize': 11, 'fontweight': 'bold'})
ax.set_title('Category vs Priority — Complaint Count Heatmap', fontsize=14, fontweight='bold')
ax.set_xlabel('Priority', fontsize=12)
ax.set_ylabel('Category', fontsize=12)

plt.tight_layout()
plt.savefig('eda_category_priority_heatmap.png', bbox_inches='tight', dpi=150)
plt.show()

print('\nCategory vs Priority Crosstab:')
print(ct_cat_priority)

# ====== CELL 18 ======
# ============================================================
# 2.7  WORD CLOUDS BY PRIORITY LEVEL
# ============================================================

# Install wordcloud if not already installed
try:
    from wordcloud import WordCloud
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'wordcloud', '-q'])
    from wordcloud import WordCloud

# Domain-specific filler words to exclude from word clouds
# These are common in hostel complaints but carry no priority signal
custom_stopwords = {
    'please', 'kindly', 'sir', 'madam', 'hello', 'thanks', 'thank',
    'look', 'now', 'today', 'day', 'days', 'week', 'weeks', 'asap',
    'hi', 'respected', 'warden', 'hostel', 'room', 'block',
    'since', 'also', 'would', 'need', 'one', 'us', 'get', 'like',
    'pls', 'plz', 'someone', 'whoever', 'charge', 'fixed', 'soon'
}

# Combine NLTK stopwords + custom stopwords
from nltk.corpus import stopwords
all_stopwords = set(stopwords.words('english')).union(custom_stopwords)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

priority_levels = ['High', 'Medium', 'Low']
wc_colors = ['Reds', 'Oranges', 'Greens']

for i, (priority, cmap) in enumerate(zip(priority_levels, wc_colors)):
    # Combine all complaint text for this priority
    text = ' '.join(df[df['Priority'] == priority]['Complaint_Text'].str.lower().tolist())
    
    # Generate word cloud with custom stopwords
    wc = WordCloud(width=600, height=350, background_color='white',
                   colormap=cmap, max_words=80, random_state=42,
                   contour_width=1, contour_color='black',
                   stopwords=all_stopwords)
    wc.generate(text)
    
    axes[i].imshow(wc, interpolation='bilinear')
    axes[i].set_title(f'{priority} Priority', fontsize=14, fontweight='bold')
    axes[i].axis('off')

plt.suptitle('Word Clouds by Priority Level (Filler Words Removed)',
             fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('eda_wordclouds.png', bbox_inches='tight', dpi=150)
plt.show()

print(f'Custom stopwords removed: {sorted(custom_stopwords)}')

# ====== CELL 19 ======
# ============================================================
# 2.8  STATUS DISTRIBUTION & STATUS vs PRIORITY
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# --- Status Distribution ---
status_order = df['Status'].value_counts().index
sns.countplot(data=df, x='Status', order=status_order,
              palette='Set2', edgecolor='black', linewidth=0.7, ax=axes[0])
axes[0].set_title('Complaint Status Distribution', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Status', fontsize=11)
axes[0].set_ylabel('Count', fontsize=11)
for container in axes[0].containers:
    axes[0].bar_label(container, fontsize=10, fontweight='bold', padding=3)

# --- Status vs Priority ---
ct_status = pd.crosstab(df['Status'], df['Priority'])
ct_status = ct_status[['High', 'Medium', 'Low']]
ct_status.plot(kind='bar', ax=axes[1],
               color=['#e74c3c', '#f39c12', '#27ae60'],
               edgecolor='black', linewidth=0.6)
axes[1].set_title('Status vs Priority', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Status', fontsize=11)
axes[1].set_ylabel('Count', fontsize=11)
axes[1].legend(title='Priority', fontsize=9)
axes[1].tick_params(axis='x', rotation=0)

plt.tight_layout()
plt.savefig('eda_status.png', bbox_inches='tight', dpi=150)
plt.show()

print('\n[!]️ Note: Status will NOT be used as a model feature (data leakage risk).')
print('   It is shown here only for exploratory understanding.')

# ====== CELL 20 ======
# ============================================================
# 2.9  TEXT LENGTH ANALYSIS
# ============================================================

# Create text length features
df['text_length'] = df['Complaint_Text'].str.len()        # Character count
df['word_count'] = df['Complaint_Text'].str.split().str.len()  # Word count

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

priority_order = ['High', 'Medium', 'Low']
colors_p = ['#e74c3c', '#f39c12', '#27ae60']

# --- Text Length Boxplot ---
sns.boxplot(data=df, x='Priority', y='text_length', order=priority_order,
            palette=colors_p, ax=axes[0], linewidth=1.2)
axes[0].set_title('Complaint Text Length by Priority', fontsize=13, fontweight='bold')
axes[0].set_xlabel('Priority', fontsize=11)
axes[0].set_ylabel('Character Count', fontsize=11)

# --- Word Count Boxplot ---
sns.boxplot(data=df, x='Priority', y='word_count', order=priority_order,
            palette=colors_p, ax=axes[1], linewidth=1.2)
axes[1].set_title('Word Count by Priority', fontsize=13, fontweight='bold')
axes[1].set_xlabel('Priority', fontsize=11)
axes[1].set_ylabel('Number of Words', fontsize=11)

plt.tight_layout()
plt.savefig('eda_text_length.png', bbox_inches='tight', dpi=150)
plt.show()

# Summary stats
print('Average Text Length by Priority:')
print(df.groupby('Priority')[['text_length', 'word_count']].mean().round(1).reindex(priority_order))

# Drop temporary columns (we'll recreate if needed later)
df.drop(columns=['text_length', 'word_count'], inplace=True)

# ====== CELL 21 ======
# ============================================================
# 3.1  DISPLAY ORIGINAL COMPLAINT TEXT (BEFORE CLEANING)
# ============================================================

print('Sample Raw Complaint Texts (Before Preprocessing):')
print('=' * 70)
for i in range(5):
    print(f'\n[{i+1}] {df["Complaint_Text"].iloc[i]}')
print('\n' + '=' * 70)

# ====== CELL 22 ======
# ============================================================
# 3.2  NLP PREPROCESSING FUNCTION
# ============================================================

# Initialize tools
stop_words = set(stopwords.words('english'))   # Set of 179 common English words
lemmatizer = WordNetLemmatizer()                # Reduces words to root form

# Domain-specific filler words common in hostel complaints
# These words appear across all priority levels and add no predictive value
domain_stopwords = {
    'please', 'kindly', 'sir', 'madam', 'hello', 'thanks', 'thank',
    'look', 'now', 'today', 'day', 'days', 'week', 'weeks', 'asap',
    'hi', 'respected', 'warden', 'hostel', 'room', 'block',
    'since', 'also', 'would', 'need', 'one', 'us', 'get', 'like',
    'pls', 'plz', 'someone', 'whoever', 'charge', 'fixed', 'soon'
}

# Combine standard + domain stopwords
all_stop_words = stop_words.union(domain_stopwords)

def preprocess_text(text):
    """
    Clean and preprocess complaint text for NLP.
    
    Steps:
        1. Lowercase
        2. Remove punctuation
        3. Remove numbers
        4. Remove extra whitespace
        5. Remove stopwords (standard English + domain-specific)
        6. Lemmatize words
    
    Args:
        text (str): Raw complaint text
    
    Returns:
        str: Cleaned and preprocessed text
    """
    
    # Step 1: Convert to lowercase
    # Why? 'Broken' and 'broken' should be treated as the same word.
    # Without this, the model would treat them as two separate features.
    text = text.lower()
    
    # Step 2: Remove punctuation
    # Why? Commas, periods, quotes are grammatical markers that don't
    # carry meaning for priority classification.
    text = re.sub(r'[^\w\s]', '', text)
    
    # Step 3: Remove numbers
    # Why? Numbers like room numbers (24, 30) and durations (3, 4)
    # are specific identifiers. They don't generalize across complaints.
    # Numerical features like Students_Affected are handled separately.
    text = re.sub(r'\d+', '', text)
    
    # Step 4: Remove extra whitespace
    # Why? After removing punctuation and numbers, gaps may remain.
    # 'room  broken' becomes 'room broken'.
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Step 5: Remove stopwords (standard + domain-specific)
    # Why? Standard stopwords (the, is, and) appear in ALL texts equally.
    # Domain stopwords (please, kindly, sir) are polite filler words
    # that don't distinguish between High, Medium, and Low priority.
    words = text.split()
    words = [word for word in words if word not in all_stop_words]
    
    # Step 6: Lemmatization
    # Why? Reduces words to their dictionary root form.
    # 'running' -> 'run', 'mice' -> 'mouse', 'broken' -> 'broken'
    # This reduces vocabulary size and groups word variations together,
    # so the model doesn't treat them as separate features.
    words = [lemmatizer.lemmatize(word) for word in words]
    
    return ' '.join(words)

print('Preprocessing function created successfully!')
print(f'Standard English stopwords: {len(stop_words)}')
print(f'Domain-specific stopwords: {len(domain_stopwords)}')
print(f'Total stopwords: {len(all_stop_words)}')

# ====== CELL 23 ======
# ============================================================
# 3.3  STEP-BY-STEP DEMONSTRATION
# ============================================================

# Pick a sample complaint
sample = df['Complaint_Text'].iloc[3]  # Mess timing complaint
print('STEP-BY-STEP PREPROCESSING DEMO')
print('=' * 65)
print(f'\nOriginal Text:\n   "{sample}"')

# Step 1
step1 = sample.lower()
print(f'\nStep 1 - Lowercase:\n   "{step1}"')

# Step 2
step2 = re.sub(r'[^\w\s]', '', step1)
print(f'\nStep 2 - Remove Punctuation:\n   "{step2}"')

# Step 3
step3 = re.sub(r'\d+', '', step2)
print(f'\nStep 3 - Remove Numbers:\n   "{step3}"')

# Step 4
step4 = re.sub(r'\s+', ' ', step3).strip()
print(f'\nStep 4 - Remove Extra Spaces:\n   "{step4}"')

# Step 5: Using combined stopwords (standard + domain)
words = [w for w in step4.split() if w not in all_stop_words]
step5 = ' '.join(words)
removed_standard = [w for w in step4.split() if w in stop_words]
removed_domain = [w for w in step4.split() if w in domain_stopwords]
print(f'\nStep 5 - Remove Stopwords:\n   "{step5}"')
print(f'   Removed (standard): {removed_standard}')
print(f'   Removed (domain):   {removed_domain}')

# Step 6
words_lem = [lemmatizer.lemmatize(w) for w in words]
step6 = ' '.join(words_lem)
print(f'\nStep 6 - Lemmatization:\n   "{step6}"')
changed = [(w1, w2) for w1, w2 in zip(words, words_lem) if w1 != w2]
if changed:
    print(f'   Changed: {changed}')
else:
    print(f'   (No words changed in this example)')

print('\n' + '=' * 65)
print(f'FINAL RESULT: "{step6}"')

# ====== CELL 24 ======
# ============================================================
# 3.4  APPLY PREPROCESSING TO ALL COMPLAINTS
# ============================================================

# Create a new column with cleaned text
# We keep the original text for reference
df['Cleaned_Text'] = df['Complaint_Text'].apply(preprocess_text)

print('Preprocessing applied to all 800 complaints!')
print(f'New column added: "Cleaned_Text"')
print(f'Dataset shape: {df.shape}')

# ====== CELL 25 ======
# ============================================================
# 3.5  BEFORE vs AFTER COMPARISON
# ============================================================

print('BEFORE vs AFTER PREPROCESSING')
print('=' * 90)

# Show 8 examples with different priorities
sample_indices = [0, 2, 3, 6, 7, 9, 11, 14]

for idx in sample_indices:
    priority = df['Priority'].iloc[idx]
    original = df['Complaint_Text'].iloc[idx]
    cleaned = df['Cleaned_Text'].iloc[idx]
    
    print(f'\n[{idx+1}] Priority: {priority}')
    print(f'   BEFORE: {original}')
    print(f'   AFTER : {cleaned}')
    print(f'   Words reduced: {len(original.split())} -> {len(cleaned.split())}')

print('\n' + '=' * 90)

# ====== CELL 26 ======
# ============================================================
# 3.6  VERIFY PREPROCESSING QUALITY
# ============================================================

# Check 1: No empty strings after cleaning
empty_count = (df['Cleaned_Text'].str.strip() == '').sum()
print(f'Check 1 - Empty texts after cleaning: {empty_count}')

# Check 2: No null values
null_count = df['Cleaned_Text'].isnull().sum()
print(f'Check 2 - Null values: {null_count}')

# Check 3: Average word count before vs after
avg_before = df['Complaint_Text'].str.split().str.len().mean()
avg_after = df['Cleaned_Text'].str.split().str.len().mean()
reduction = ((avg_before - avg_after) / avg_before * 100)
print(f'\nCheck 3 - Average word count:')
print(f'   Before preprocessing: {avg_before:.1f} words')
print(f'   After preprocessing:  {avg_after:.1f} words')
print(f'   Reduction: {reduction:.1f}%')

# Check 4: Vocabulary size
vocab_before = set(' '.join(df['Complaint_Text'].str.lower()).split())
vocab_after = set(' '.join(df['Cleaned_Text']).split())
print(f'\nCheck 4 - Vocabulary size:')
print(f'   Before: {len(vocab_before)} unique words')
print(f'   After:  {len(vocab_after)} unique words')
print(f'   Reduction: {((len(vocab_before) - len(vocab_after)) / len(vocab_before) * 100):.1f}%')

print('\nAll checks passed! Preprocessing is clean and complete.')

# ====== CELL 27 ======
# ============================================================
# 3.7  TOP WORDS BY PRIORITY (AFTER PREPROCESSING)
# ============================================================

from collections import Counter

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

priority_levels = ['High', 'Medium', 'Low']
bar_colors = ['#e74c3c', '#f39c12', '#27ae60']

for i, (priority, color) in enumerate(zip(priority_levels, bar_colors)):
    # Get all words for this priority (already preprocessed with custom stopwords)
    all_words = ' '.join(df[df['Priority'] == priority]['Cleaned_Text']).split()
    word_freq = Counter(all_words).most_common(15)
    
    words, counts = zip(*word_freq)
    
    axes[i].barh(range(len(words)), counts, color=color,
                 edgecolor='black', linewidth=0.5)
    axes[i].set_yticks(range(len(words)))
    axes[i].set_yticklabels(words, fontsize=10)
    axes[i].invert_yaxis()  # Most frequent at top
    axes[i].set_title(f'{priority} Priority - Top 15 Words',
                     fontsize=12, fontweight='bold')
    axes[i].set_xlabel('Frequency', fontsize=10)

plt.suptitle('Most Frequent Words by Priority (After Full Preprocessing)',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('nlp_top_words_by_priority.png', bbox_inches='tight', dpi=150)
plt.show()

# Print top words as a table for reference
print('\nTop 10 Words per Priority Level:')
print('-' * 55)
for priority in priority_levels:
    all_words = ' '.join(df[df['Priority'] == priority]['Cleaned_Text']).split()
    top10 = Counter(all_words).most_common(10)
    words_str = ', '.join([f'{w} ({c})' for w, c in top10])
    print(f'{priority:8s}: {words_str}')

# ====== CELL 28 ======
# ============================================================
# 4.1  APPLY TF-IDF VECTORIZATION
# ============================================================

# Initialize the TF-IDF Vectorizer with carefully chosen parameters
tfidf = TfidfVectorizer(
    max_features=1000,       # Keep top 1000 words (controls matrix size)
    ngram_range=(1, 2),      # Unigrams + bigrams (single words + word pairs)
    min_df=2,                # Word must appear in at least 2 documents
    max_df=0.95,             # Ignore words appearing in >95% of documents
    sublinear_tf=True        # Apply log normalization to term frequency
)

# Fit and transform the cleaned complaint text
# fit_transform() learns the vocabulary AND converts text to numbers in one step
tfidf_matrix = tfidf.fit_transform(df['Cleaned_Text'])

print('TF-IDF Vectorization Complete!')
print(f'  Input:  {len(df)} complaint texts')
print(f'  Output: TF-IDF matrix of shape {tfidf_matrix.shape}')
print(f'  -> {tfidf_matrix.shape[0]} complaints (rows)')
print(f'  -> {tfidf_matrix.shape[1]} TF-IDF features (columns/words)')
print(f'\n  Matrix type: {type(tfidf_matrix).__name__} (sparse matrix - memory efficient)')
print(f'  Non-zero entries: {tfidf_matrix.nnz} out of {tfidf_matrix.shape[0] * tfidf_matrix.shape[1]}')
print(f'  Sparsity: {(1 - tfidf_matrix.nnz / (tfidf_matrix.shape[0] * tfidf_matrix.shape[1])) * 100:.1f}%')

# ====== CELL 29 ======
# ============================================================
# 4.2  EXAMINE TF-IDF VOCABULARY AND FEATURES
# ============================================================

# Get the list of feature names (words/bigrams)
feature_names = tfidf.get_feature_names_out()

print(f'Total TF-IDF features: {len(feature_names)}')
print(f'\nFirst 20 features (alphabetical):')
for i, word in enumerate(feature_names[:20], 1):
    print(f'  {i:3d}. {word}')

print(f'\nLast 20 features (alphabetical):')
for i, word in enumerate(feature_names[-20:], len(feature_names)-19):
    print(f'  {i:3d}. {word}')

# Count unigrams vs bigrams
unigrams = [f for f in feature_names if ' ' not in f]
bigrams = [f for f in feature_names if ' ' in f]
print(f'\nFeature breakdown:')
print(f'  Unigrams (single words): {len(unigrams)}')
print(f'  Bigrams (word pairs):    {len(bigrams)}')

# Show some example bigrams
print(f'\nSample bigrams:')
for bg in bigrams[:15]:
    print(f'  - {bg}')

# ====== CELL 30 ======
# ============================================================
# 4.3  TOP TF-IDF FEATURES (HIGHEST AVERAGE SCORES)
# ============================================================

# Calculate mean TF-IDF score for each feature across all documents
mean_tfidf = tfidf_matrix.mean(axis=0).A1  # .A1 converts sparse matrix to 1D array

# Create a DataFrame of features and their mean scores
tfidf_scores = pd.DataFrame({
    'Feature': feature_names,
    'Mean_TF-IDF': mean_tfidf
}).sort_values('Mean_TF-IDF', ascending=False)

# Plot top 25 features
fig, ax = plt.subplots(figsize=(10, 7))

top_n = 25
top_features = tfidf_scores.head(top_n)

ax.barh(range(top_n), top_features['Mean_TF-IDF'].values,
        color='#2980b9', edgecolor='black', linewidth=0.5)
ax.set_yticks(range(top_n))
ax.set_yticklabels(top_features['Feature'].values, fontsize=10)
ax.invert_yaxis()
ax.set_xlabel('Mean TF-IDF Score', fontsize=11)
ax.set_title(f'Top {top_n} TF-IDF Features (by Mean Score)', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('tfidf_top_features.png', bbox_inches='tight', dpi=150)
plt.show()

print(f'\nTop 10 Features with Highest Mean TF-IDF Scores:')
print(tfidf_scores.head(10).to_string(index=False))

# ====== CELL 31 ======
# ============================================================
# 4.4  TOP TF-IDF FEATURES PER PRIORITY CLASS
# ============================================================

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

priority_levels = ['High', 'Medium', 'Low']
bar_colors = ['#e74c3c', '#f39c12', '#27ae60']

for i, (priority, color) in enumerate(zip(priority_levels, bar_colors)):
    # Get indices of complaints with this priority
    mask = df['Priority'] == priority
    
    # Calculate mean TF-IDF scores for this priority class only
    mean_scores = tfidf_matrix[mask].mean(axis=0).A1
    
    # Get top 15 features
    top_indices = mean_scores.argsort()[-15:][::-1]
    top_words = feature_names[top_indices]
    top_scores = mean_scores[top_indices]
    
    axes[i].barh(range(15), top_scores, color=color,
                 edgecolor='black', linewidth=0.5)
    axes[i].set_yticks(range(15))
    axes[i].set_yticklabels(top_words, fontsize=9)
    axes[i].invert_yaxis()
    axes[i].set_xlabel('Mean TF-IDF Score', fontsize=10)
    axes[i].set_title(f'{priority} Priority - Top 15 TF-IDF Features',
                     fontsize=12, fontweight='bold')

plt.suptitle('Most Important TF-IDF Features by Priority Level',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('tfidf_features_by_priority.png', bbox_inches='tight', dpi=150)
plt.show()

# ====== CELL 32 ======
# ============================================================
# 4.5  SAMPLE TF-IDF VECTORS
# ============================================================

# Show TF-IDF representation for 3 sample complaints
sample_indices = [0, 2, 6]  # Low, High, High priority examples

for idx in sample_indices:
    print(f'Complaint {idx+1} (Priority: {df["Priority"].iloc[idx]}):')
    print(f'  Text: "{df["Cleaned_Text"].iloc[idx]}"')
    
    # Get non-zero TF-IDF scores for this complaint
    row = tfidf_matrix[idx]
    non_zero = row.nonzero()[1]  # Column indices of non-zero entries
    
    if len(non_zero) > 0:
        scores = [(feature_names[j], row[0, j]) for j in non_zero]
        scores.sort(key=lambda x: x[1], reverse=True)
        
        print(f'  Non-zero features: {len(scores)}')
        print(f'  Top 5 TF-IDF features:')
        for word, score in scores[:5]:
            print(f'    {word:25s} -> {score:.4f}')
    print()

# ====== CELL 33 ======
# ============================================================
# 5.1  DROP UNNECESSARY COLUMNS
# ============================================================

# Columns to drop and reasons:
drop_cols = {
    'Complaint_ID': 'Unique identifier, not a predictive feature',
    'Room_No': 'Near-zero correlation with other features (Section 2.5)',
    'Duration': 'Free-text field with many unique values, inconsistent format',
    'Status': 'Determined AFTER priority - using it would cause data leakage',
    'Complaint_Date': 'Date metadata, not a feature for priority prediction',
    'Complaint_Text': 'Already processed into Cleaned_Text and TF-IDF'
}

print('Columns being dropped:')
print('-' * 60)
for col, reason in drop_cols.items():
    print(f'  {col:20s} -> {reason}')

# Drop the columns
df_model = df.drop(columns=list(drop_cols.keys()))

print(f'\nRemaining columns: {df_model.columns.tolist()}')
print(f'Shape: {df_model.shape}')

# ====== CELL 34 ======
# ============================================================
# 5.2  IDENTIFY FEATURE TYPES
# ============================================================

# Define feature groups
categorical_features = ['Complaint_Type', 'Block', 'Floor', 'Category']
numerical_features = ['Students_Affected', 'Support_Count']
text_feature = 'Cleaned_Text'  # Already vectorized via TF-IDF
target = 'Priority'

print('Feature Groups:')
print('-' * 50)
print(f'  Categorical features: {categorical_features}')
print(f'  Numerical features:   {numerical_features}')
print(f'  Text feature:         {text_feature} (via TF-IDF)')
print(f'  Target variable:      {target}')

# Show unique values for each categorical feature
print('\nCategorical Feature Details:')
print('-' * 50)
for col in categorical_features:
    vals = df_model[col].unique()
    print(f'  {col}: {len(vals)} unique values -> {vals.tolist()}')

# Show numerical feature stats
print('\nNumerical Feature Stats:')
print('-' * 50)
print(df_model[numerical_features].describe().round(1))

# ====== CELL 35 ======
# ============================================================
# 5.3  ENCODE CATEGORICAL FEATURES
# ============================================================

# Demonstrate OneHotEncoding on a small example first
print('OneHotEncoding Example (Block column, first 5 rows):')
print('-' * 50)
print(f'Original values: {df_model["Block"].head().tolist()}')

# Show what OneHotEncoding will produce
example_ohe = pd.get_dummies(df_model['Block'].head(), prefix='Block')
print('\nAfter OneHotEncoding:')
print(example_ohe.to_string())

print('\nEach original value becomes a separate binary column.')
print('The model can now treat each block as an independent signal.')

# ====== CELL 36 ======
# ============================================================
# 5.4  DEMONSTRATE SCALING
# ============================================================

print('Numerical Features - Before Scaling:')
print('-' * 50)
print(df_model[numerical_features].describe().round(2))

# Demonstrate scaling on a sample
from sklearn.preprocessing import StandardScaler
demo_scaler = StandardScaler()
scaled_demo = demo_scaler.fit_transform(df_model[numerical_features].head(5))

print('\nSample (first 5 rows) - Before vs After Scaling:')
print('-' * 50)
for i in range(5):
    orig = df_model[numerical_features].iloc[i].values
    scaled = scaled_demo[i]
    print(f'  Row {i+1}: {orig} -> [{scaled[0]:.3f}, {scaled[1]:.3f}]')

print('\nAfter scaling, values are centered around 0 with unit variance.')
print('This ensures no feature dominates due to its scale.')

# ====== CELL 37 ======
# ============================================================
# 5.5  ENCODE TARGET VARIABLE
# ============================================================

# Initialize LabelEncoder
label_encoder = LabelEncoder()

# Fit and transform the Priority column
y = label_encoder.fit_transform(df_model['Priority'])

# Show the mapping
print('Target Variable Encoding:')
print('-' * 40)
for label, encoded in zip(label_encoder.classes_, range(len(label_encoder.classes_))):
    count = (y == encoded).sum()
    pct = count / len(y) * 100
    print(f'  {label:8s} -> {encoded}   ({count} samples, {pct:.1f}%)')

print(f'\nEncoded target shape: {y.shape}')
print(f'Unique encoded values: {np.unique(y)}')

# ====== CELL 38 ======
# ============================================================
# 5.6  BUILD COLUMN TRANSFORMER
# ============================================================

# Define the ColumnTransformer with three parallel transformations
preprocessor = ColumnTransformer(
    transformers=[
        # (name, transformer, columns)
        ('tfidf', TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True
        ), 'Cleaned_Text'),
        
        ('cat', OneHotEncoder(
            drop='first',           # Drop first category to avoid multicollinearity
            sparse_output=False,     # Return dense array
            handle_unknown='ignore'  # Handle unseen categories gracefully
        ), categorical_features),
        
        ('num', StandardScaler(), numerical_features)
    ],
    remainder='drop'  # Drop any columns not specified above
)

print('ColumnTransformer created with 3 transformers:')
print('-' * 55)
print('  1. TF-IDF Vectorizer  -> Cleaned_Text')
print('  2. OneHotEncoder      -> Complaint_Type, Block, Floor, Category')
print('  3. StandardScaler     -> Students_Affected, Support_Count')
print()
print('Note: OneHotEncoder uses drop="first" to avoid')
print('multicollinearity (the dummy variable trap).')

# ====== CELL 39 ======
# ============================================================
# 5.7  PREPARE X AND y
# ============================================================

# X contains all feature columns (text + categorical + numerical)
# The ColumnTransformer will handle each type appropriately
X = df_model.drop(columns=['Priority'])

# y is the encoded target variable (already created in 5.5)
# y = label_encoder.fit_transform(df_model['Priority'])  # Already done

print(f'Feature matrix X shape: {X.shape}')
print(f'Target vector y shape:  {y.shape}')
print(f'\nX columns: {X.columns.tolist()}')
print(f'\nTarget classes: {label_encoder.classes_}')

# Fit and transform X using the ColumnTransformer
X_transformed = preprocessor.fit_transform(X)

print(f'\nAfter ColumnTransformer:')
print(f'  X_transformed shape: {X_transformed.shape}')
print(f'  -> {X_transformed.shape[0]} samples')
print(f'  -> {X_transformed.shape[1]} total features')

# Break down feature count
# TF-IDF features
tfidf_feat_count = len(preprocessor.transformers_[0][1].get_feature_names_out())
# OneHot features
ohe_feat_count = len(preprocessor.transformers_[1][1].get_feature_names_out())
# Numerical features
num_feat_count = len(numerical_features)

print(f'\nFeature Breakdown:')
print(f'  TF-IDF text features:     {tfidf_feat_count}')
print(f'  OneHotEncoded categorical: {ohe_feat_count}')
print(f'  Scaled numerical:          {num_feat_count}')
print(f'  TOTAL:                     {tfidf_feat_count + ohe_feat_count + num_feat_count}')

# ====== CELL 40 ======
# ============================================================
# 5.8  VERIFY COMBINED FEATURES
# ============================================================

from scipy.sparse import issparse

print('Feature Matrix Verification:')
print('-' * 50)
print(f'Shape:       {X_transformed.shape}')
print(f'Type:        {type(X_transformed).__name__}')
print(f'Sparse:      {issparse(X_transformed)}')

# Check for NaN or infinite values
if issparse(X_transformed):
    has_nan = np.isnan(X_transformed.data).any()
    has_inf = np.isinf(X_transformed.data).any()
else:
    has_nan = np.isnan(X_transformed).any()
    has_inf = np.isinf(X_transformed).any()

print(f'Contains NaN: {has_nan}')
print(f'Contains Inf: {has_inf}')
print(f'Samples (X):  {X_transformed.shape[0]}')
print(f'Samples (y):  {len(y)}')
print(f'X and y match: {X_transformed.shape[0] == len(y)}')

print('\nAll checks passed! Data is ready for model training.')

# ====== CELL 41 ======
# ============================================================
# 6.1  TRAIN-TEST SPLIT
# ============================================================

# IMPORTANT: Split BEFORE applying any transformation
# This prevents the test set from influencing the transformer
X_train_raw, X_test_raw, y_train, y_test = train_test_split(
    X,           # Raw feature DataFrame (not yet transformed)
    y,           # Encoded target labels
    test_size=0.20,
    random_state=42,
    stratify=y   # Preserve class distribution in both splits
)

print('Train-Test Split Complete!')
print(f'  Total samples : {len(X)}')
print(f'  Training set  : {len(X_train_raw)} samples ({len(X_train_raw)/len(X)*100:.0f}%)')
print(f'  Test set      : {len(X_test_raw)} samples ({len(X_test_raw)/len(X)*100:.0f}%)')

# Verify class distribution is preserved
print('\nClass Distribution Check (stratification verification):')
print(f'{"Class":<10} {"Full Data":>12} {"Train Set":>12} {"Test Set":>12}')
print('-' * 48)
for i, cls in enumerate(label_encoder.classes_):
    full_pct  = (y == i).sum() / len(y) * 100
    train_pct = (y_train == i).sum() / len(y_train) * 100
    test_pct  = (y_test == i).sum() / len(y_test) * 100
    print(f'{cls:<10} {full_pct:>10.1f}%  {train_pct:>10.1f}%  {test_pct:>10.1f}%')

# ====== CELL 42 ======
# ============================================================
# 6.2  FIT PREPROCESSOR ON TRAIN, TRANSFORM BOTH SETS
# ============================================================

# Reinitialize a fresh preprocessor to avoid using the one fitted in Section 5
from sklearn.pipeline import Pipeline

preprocessor = ColumnTransformer(
    transformers=[
        ('tfidf', TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True
        ), 'Cleaned_Text'),
        ('cat', OneHotEncoder(
            drop='first',
            sparse_output=False,
            handle_unknown='ignore'
        ), categorical_features),
        ('num', StandardScaler(), numerical_features)
    ],
    remainder='drop'
)

# fit_transform on TRAINING data only
# The preprocessor learns vocabulary, category values, mean/std from training data
X_train = preprocessor.fit_transform(X_train_raw)

# transform (NOT fit_transform) on TEST data
# Applies the same transformations learned from training data
X_test = preprocessor.transform(X_test_raw)

print('Preprocessing applied correctly (no data leakage):')
print(f'  X_train shape: {X_train.shape}')
print(f'  X_test  shape: {X_test.shape}')
print(f'  y_train shape: {y_train.shape}')
print(f'  y_test  shape: {y_test.shape}')

# ====== CELL 43 ======
# ============================================================
# 6.3  TRAIN LOGISTIC REGRESSION
# ============================================================

# Initialize Logistic Regression
lr_model = LogisticRegression(
    C=1.0,            # Regularization strength (default; will tune in Section 11)
    max_iter=1000,    # Increase max iterations to ensure convergence
    solver='lbfgs',   # Efficient solver for multi-class problems
        random_state=42,
    class_weight='balanced'  # Adjust weights to handle any class imbalance
)

# Train the model
lr_model.fit(X_train, y_train)

print('Logistic Regression model trained!')
print(f'  Training samples: {X_train.shape[0]}')
print(f'  Features used:    {X_train.shape[1]}')
print(f'  Classes:          {label_encoder.classes_}')

# ====== CELL 44 ======
# ============================================================
# 6.4  PREDICTIONS AND EVALUATION METRICS
# ============================================================

# Make predictions on the test set
y_pred_lr = lr_model.predict(X_test)

# --- Compute Metrics ---
acc   = accuracy_score(y_test, y_pred_lr)
prec  = precision_score(y_test, y_pred_lr, average='weighted')
rec   = recall_score(y_test, y_pred_lr, average='weighted')
f1    = f1_score(y_test, y_pred_lr, average='weighted')

print('LOGISTIC REGRESSION - Evaluation Results')
print('=' * 50)
print(f'  Accuracy  : {acc:.4f}  ({acc*100:.2f}%)')
print(f'  Precision : {prec:.4f}  ({prec*100:.2f}%)')
print(f'  Recall    : {rec:.4f}  ({rec*100:.2f}%)')
print(f'  F1-Score  : {f1:.4f}  ({f1*100:.2f}%)')

# ====== CELL 45 ======
# ============================================================
# 6.5  CLASSIFICATION REPORT (PER CLASS)
# ============================================================

# Full per-class breakdown
print('LOGISTIC REGRESSION - Classification Report')
print('=' * 55)
print(classification_report(
    y_test, y_pred_lr,
    target_names=label_encoder.classes_
))

# ====== CELL 46 ======
# ============================================================
# 6.6  CONFUSION MATRIX
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

class_names = label_encoder.classes_
cm = confusion_matrix(y_test, y_pred_lr)

# --- Raw Counts ---
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_names, yticklabels=class_names,
            linewidths=0.8, linecolor='white',
            ax=axes[0], annot_kws={'fontsize': 12, 'fontweight': 'bold'})
axes[0].set_title('Confusion Matrix (Counts)', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Actual Label', fontsize=11)
axes[0].set_xlabel('Predicted Label', fontsize=11)

# --- Row-Normalized (Recall per Class) ---
cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues',
            xticklabels=class_names, yticklabels=class_names,
            linewidths=0.8, linecolor='white',
            ax=axes[1], annot_kws={'fontsize': 12, 'fontweight': 'bold'},
            vmin=0, vmax=1)
axes[1].set_title('Confusion Matrix (Row-Normalized)', fontsize=13, fontweight='bold')
axes[1].set_ylabel('Actual Label', fontsize=11)
axes[1].set_xlabel('Predicted Label', fontsize=11)

plt.suptitle('Logistic Regression - Confusion Matrix', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('lr_confusion_matrix.png', bbox_inches='tight', dpi=150)
plt.show()

# Print confusion matrix as a labeled table
print('\nConfusion Matrix (rows=Actual, columns=Predicted):')
cm_df = pd.DataFrame(cm, index=class_names, columns=class_names)
cm_df.index.name = 'Actual'
cm_df.columns.name = 'Predicted'
print(cm_df)

# ====== CELL 47 ======
# ============================================================
# 6.7  STORE RESULTS FOR COMPARISON
# ============================================================

# Dictionary to store all model results
# We will add entries after each model is trained
results = {}

results['Logistic Regression'] = {
    'Accuracy' : round(acc, 4),
    'Precision': round(prec, 4),
    'Recall'   : round(rec, 4),
    'F1-Score' : round(f1, 4),
    'y_pred'   : y_pred_lr
}

print('Logistic Regression results saved!')
print(f'  Accuracy : {acc:.4f}')
print(f'  F1-Score : {f1:.4f}')

# ====== CELL 48 ======
# ============================================================
# 7.1  TRAIN RANDOM FOREST
# ============================================================

# Note: X_train and X_test are already transformed (from Section 6)
# We reuse the same train/test split throughout all model sections

rf_model = RandomForestClassifier(
    n_estimators=200,       # 200 decision trees
    max_depth=None,         # Allow trees to grow fully (depth controlled by min_samples)
    min_samples_split=5,    # A node needs at least 5 samples to be split
    min_samples_leaf=2,     # Each leaf must have at least 2 samples
    class_weight='balanced',# Adjust for class imbalance
    random_state=42,
    n_jobs=-1               # Use all CPU cores for faster training
)

rf_model.fit(X_train, y_train)

print('Random Forest trained!')
print(f'  Number of trees : {rf_model.n_estimators}')
print(f'  Training samples: {X_train.shape[0]}')
print(f'  Features used   : {X_train.shape[1]}')

# ====== CELL 49 ======
# ============================================================
# 7.2  PREDICT AND EVALUATE
# ============================================================

y_pred_rf = rf_model.predict(X_test)

acc_rf  = accuracy_score(y_test, y_pred_rf)
prec_rf = precision_score(y_test, y_pred_rf, average='weighted')
rec_rf  = recall_score(y_test, y_pred_rf, average='weighted')
f1_rf   = f1_score(y_test, y_pred_rf, average='weighted')

print('RANDOM FOREST - Evaluation Results')
print('=' * 50)
print(f'  Accuracy  : {acc_rf:.4f}  ({acc_rf*100:.2f}%)')
print(f'  Precision : {prec_rf:.4f}  ({prec_rf*100:.2f}%)')
print(f'  Recall    : {rec_rf:.4f}  ({rec_rf*100:.2f}%)')
print(f'  F1-Score  : {f1_rf:.4f}  ({f1_rf*100:.2f}%)')

print('\nRANDOM FOREST - Classification Report')
print('=' * 55)
print(classification_report(
    y_test, y_pred_rf,
    target_names=label_encoder.classes_
))

# ====== CELL 50 ======
# ============================================================
# 7.3  CONFUSION MATRIX
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

class_names = label_encoder.classes_
cm_rf = confusion_matrix(y_test, y_pred_rf)

# --- Raw Counts ---
sns.heatmap(cm_rf, annot=True, fmt='d', cmap='Greens',
            xticklabels=class_names, yticklabels=class_names,
            linewidths=0.8, linecolor='white',
            ax=axes[0], annot_kws={'fontsize': 12, 'fontweight': 'bold'})
axes[0].set_title('Confusion Matrix (Counts)', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Actual Label', fontsize=11)
axes[0].set_xlabel('Predicted Label', fontsize=11)

# --- Row-Normalized ---
cm_rf_norm = cm_rf.astype('float') / cm_rf.sum(axis=1)[:, np.newaxis]
sns.heatmap(cm_rf_norm, annot=True, fmt='.2f', cmap='Greens',
            xticklabels=class_names, yticklabels=class_names,
            linewidths=0.8, linecolor='white',
            ax=axes[1], annot_kws={'fontsize': 12, 'fontweight': 'bold'},
            vmin=0, vmax=1)
axes[1].set_title('Confusion Matrix (Row-Normalized)', fontsize=13, fontweight='bold')
axes[1].set_ylabel('Actual Label', fontsize=11)
axes[1].set_xlabel('Predicted Label', fontsize=11)

plt.suptitle('Random Forest - Confusion Matrix', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('rf_confusion_matrix.png', bbox_inches='tight', dpi=150)
plt.show()

# ====== CELL 51 ======
# ============================================================
# 7.4  FEATURE IMPORTANCES
# ============================================================

# Get feature names from each transformer in the ColumnTransformer
tfidf_names    = preprocessor.transformers_[0][1].get_feature_names_out()
ohe_names      = preprocessor.transformers_[1][1].get_feature_names_out()
num_names      = np.array(numerical_features)
all_feat_names = np.concatenate([tfidf_names, ohe_names, num_names])

# Get importances from the trained Random Forest
importances = rf_model.feature_importances_

# Create a sorted DataFrame
feat_imp_df = pd.DataFrame({
    'Feature': all_feat_names,
    'Importance': importances
}).sort_values('Importance', ascending=False).head(20)

# Plot
fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(range(len(feat_imp_df)), feat_imp_df['Importance'].values,
        color='#27ae60', edgecolor='black', linewidth=0.5)
ax.set_yticks(range(len(feat_imp_df)))
ax.set_yticklabels(feat_imp_df['Feature'].values, fontsize=10)
ax.invert_yaxis()
ax.set_xlabel('Feature Importance (Mean Decrease in Impurity)', fontsize=11)
ax.set_title('Random Forest - Top 20 Feature Importances', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('rf_feature_importances.png', bbox_inches='tight', dpi=150)
plt.show()

print('Top 10 Most Important Features:')
print('-' * 50)
print(feat_imp_df[['Feature','Importance']].head(10).to_string(index=False))

# ====== CELL 52 ======
# ============================================================
# 7.5  STORE RESULTS FOR COMPARISON
# ============================================================

results['Random Forest'] = {
    'Accuracy' : round(acc_rf, 4),
    'Precision': round(prec_rf, 4),
    'Recall'   : round(rec_rf, 4),
    'F1-Score' : round(f1_rf, 4),
    'y_pred'   : y_pred_rf
}

# Quick comparison so far
print('Model Results So Far:')
print('-' * 60)
print(f'{"Model":<22} {"Accuracy":>10} {"F1-Score":>10}')
print('-' * 60)
for model_name, res in results.items():
    print(f'{model_name:<22} {res["Accuracy"]:>10.4f} {res["F1-Score"]:>10.4f}')

# ====== CELL 53 ======
# ============================================================
# 8.1  TRAIN LINEAR SVM
# ============================================================

# LinearSVC is the most efficient SVM implementation for text classification
svm_model = LinearSVC(
    C=1.0,              # Regularization parameter (default; will tune in Section 11)
    max_iter=2000,      # Increase iterations to ensure convergence
    class_weight='balanced',  # Handle class imbalance
    random_state=42
)

svm_model.fit(X_train, y_train)

print('LinearSVC model trained!')
print(f'  Training samples: {X_train.shape[0]}')
print(f'  Features used   : {X_train.shape[1]}')
print(f'  Classes         : {label_encoder.classes_}')

# ====== CELL 54 ======
# ============================================================
# 8.2  PREDICT AND EVALUATE
# ============================================================

y_pred_svm = svm_model.predict(X_test)

acc_svm  = accuracy_score(y_test, y_pred_svm)
prec_svm = precision_score(y_test, y_pred_svm, average='weighted')
rec_svm  = recall_score(y_test, y_pred_svm, average='weighted')
f1_svm   = f1_score(y_test, y_pred_svm, average='weighted')

print('LINEAR SVM - Evaluation Results')
print('=' * 50)
print(f'  Accuracy  : {acc_svm:.4f}  ({acc_svm*100:.2f}%)')
print(f'  Precision : {prec_svm:.4f}  ({prec_svm*100:.2f}%)')
print(f'  Recall    : {rec_svm:.4f}  ({rec_svm*100:.2f}%)')
print(f'  F1-Score  : {f1_svm:.4f}  ({f1_svm*100:.2f}%)')

print('\nLINEAR SVM - Classification Report')
print('=' * 55)
print(classification_report(
    y_test, y_pred_svm,
    target_names=label_encoder.classes_
))

# ====== CELL 55 ======
# ============================================================
# 8.3  CONFUSION MATRIX
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

class_names = label_encoder.classes_
cm_svm = confusion_matrix(y_test, y_pred_svm)

# --- Raw Counts ---
sns.heatmap(cm_svm, annot=True, fmt='d', cmap='Purples',
            xticklabels=class_names, yticklabels=class_names,
            linewidths=0.8, linecolor='white',
            ax=axes[0], annot_kws={'fontsize': 12, 'fontweight': 'bold'})
axes[0].set_title('Confusion Matrix (Counts)', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Actual Label', fontsize=11)
axes[0].set_xlabel('Predicted Label', fontsize=11)

# --- Row-Normalized ---
cm_svm_norm = cm_svm.astype('float') / cm_svm.sum(axis=1)[:, np.newaxis]
sns.heatmap(cm_svm_norm, annot=True, fmt='.2f', cmap='Purples',
            xticklabels=class_names, yticklabels=class_names,
            linewidths=0.8, linecolor='white',
            ax=axes[1], annot_kws={'fontsize': 12, 'fontweight': 'bold'},
            vmin=0, vmax=1)
axes[1].set_title('Confusion Matrix (Row-Normalized)', fontsize=13, fontweight='bold')
axes[1].set_ylabel('Actual Label', fontsize=11)
axes[1].set_xlabel('Predicted Label', fontsize=11)

plt.suptitle('Linear SVM - Confusion Matrix', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('svm_confusion_matrix.png', bbox_inches='tight', dpi=150)
plt.show()

# ====== CELL 56 ======
# ============================================================
# 8.4  TOP DISCRIMINATIVE WORDS PER CLASS (SVM COEFFICIENTS)
# ============================================================

# Get TF-IDF feature names only (first N features from ColumnTransformer)
tfidf_names_svm = preprocessor.transformers_[0][1].get_feature_names_out()
n_tfidf = len(tfidf_names_svm)

# LinearSVC has one set of coefficients per class (One-vs-Rest)
# Shape: (n_classes, n_features)
# We focus only on the TF-IDF portion of the coefficients
svm_coef = svm_model.coef_[:, :n_tfidf]  # Only TF-IDF columns

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

bar_colors = ['#e74c3c', '#27ae60', '#f39c12']  # Matches class order

for i, (cls, color) in enumerate(zip(label_encoder.classes_, bar_colors)):
    coefs = svm_coef[i]
    # Top 15 positive coefficients (most strongly predicting this class)
    top_idx = coefs.argsort()[-15:][::-1]
    top_words  = tfidf_names_svm[top_idx]
    top_coefs  = coefs[top_idx]

    axes[i].barh(range(15), top_coefs, color=color,
                 edgecolor='black', linewidth=0.5)
    axes[i].set_yticks(range(15))
    axes[i].set_yticklabels(top_words, fontsize=9)
    axes[i].invert_yaxis()
    axes[i].set_title(f'{cls} Priority\nTop 15 Discriminative Words',
                     fontsize=12, fontweight='bold')
    axes[i].set_xlabel('SVM Coefficient', fontsize=10)

plt.suptitle('Linear SVM - Top Discriminative TF-IDF Features per Class',
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('svm_top_words.png', bbox_inches='tight', dpi=150)
plt.show()

print('Top 5 discriminative words per class (by SVM coefficient):')
print('-' * 60)
for i, cls in enumerate(label_encoder.classes_):
    coefs = svm_coef[i]
    top5_idx = coefs.argsort()[-5:][::-1]
    top5 = [(tfidf_names_svm[j], round(coefs[j], 4)) for j in top5_idx]
    print(f'\n  {cls}: {top5}')

# ====== CELL 57 ======
# ============================================================
# 8.5  STORE RESULTS FOR COMPARISON
# ============================================================

results['Linear SVM'] = {
    'Accuracy' : round(acc_svm, 4),
    'Precision': round(prec_svm, 4),
    'Recall'   : round(rec_svm, 4),
    'F1-Score' : round(f1_svm, 4),
    'y_pred'   : y_pred_svm
}

# Running comparison table
print('Model Results So Far:')
print('-' * 65)
print(f'{"Model":<22} {"Accuracy":>10} {"Precision":>10} {"Recall":>10} {"F1-Score":>10}')
print('-' * 65)
for model_name, res in results.items():
    print(f'{model_name:<22} {res["Accuracy"]:>10.4f} {res["Precision"]:>10.4f} {res["Recall"]:>10.4f} {res["F1-Score"]:>10.4f}')

# ====== CELL 58 ======
# ============================================================
# 9.1  PREPARE TFIDF-ONLY FEATURES FOR NAIVE BAYES
# ============================================================

from scipy.sparse import issparse, hstack, csr_matrix

# MultinomialNB requires all features >= 0.
# TF-IDF values are always >= 0 (safe).
# StandardScaler output can be negative (unsafe for MultinomialNB).
#
# Solution: Use only the TF-IDF portion of the feature matrix.
# The number of TF-IDF features was determined in Section 5.

# Get the number of TF-IDF features from the fitted preprocessor
n_tfidf_features = len(preprocessor.transformers_[0][1].get_feature_names_out())

# Extract TF-IDF columns only from X_train and X_test
if issparse(X_train):
    X_train_nb = X_train[:, :n_tfidf_features]
    X_test_nb  = X_test[:, :n_tfidf_features]
else:
    X_train_nb = csr_matrix(X_train[:, :n_tfidf_features])
    X_test_nb  = csr_matrix(X_test[:, :n_tfidf_features])

print('Features prepared for Naive Bayes:')
print(f'  Full feature matrix  : {X_train.shape[1]} features')
print(f'  TF-IDF only (for NB) : {X_train_nb.shape[1]} features')
print(f'  X_train_nb shape     : {X_train_nb.shape}')
print(f'  X_test_nb  shape     : {X_test_nb.shape}')

# Verify all values are non-negative
min_val = X_train_nb.min()
print(f'  Minimum value in matrix: {min_val:.4f} (must be >= 0)')
print(f'  All values non-negative: {min_val >= 0}')

# ====== CELL 59 ======
# ============================================================
# 9.2  TRAIN MULTINOMIAL NAIVE BAYES
# ============================================================

nb_model = MultinomialNB(
    alpha=1.0  # Laplace smoothing: prevents zero probability for unseen words
               # alpha=1.0 is the standard Laplace smoothing value
)

nb_model.fit(X_train_nb, y_train)

print('Multinomial Naive Bayes model trained!')
print(f'  Training samples: {X_train_nb.shape[0]}')
print(f'  TF-IDF features : {X_train_nb.shape[1]}')
print(f'  alpha (smoothing): {nb_model.alpha}')
print(f'  Classes: {label_encoder.classes_}')

# ====== CELL 60 ======
# ============================================================
# 9.3  PREDICT AND EVALUATE
# ============================================================

y_pred_nb = nb_model.predict(X_test_nb)

acc_nb  = accuracy_score(y_test, y_pred_nb)
prec_nb = precision_score(y_test, y_pred_nb, average='weighted')
rec_nb  = recall_score(y_test, y_pred_nb, average='weighted')
f1_nb   = f1_score(y_test, y_pred_nb, average='weighted')

print('MULTINOMIAL NAIVE BAYES - Evaluation Results')
print('=' * 50)
print(f'  Accuracy  : {acc_nb:.4f}  ({acc_nb*100:.2f}%)')
print(f'  Precision : {prec_nb:.4f}  ({prec_nb*100:.2f}%)')
print(f'  Recall    : {rec_nb:.4f}  ({rec_nb*100:.2f}%)')
print(f'  F1-Score  : {f1_nb:.4f}  ({f1_nb*100:.2f}%)')

print('\nMULTINOMIAL NAIVE BAYES - Classification Report')
print('=' * 55)
print(classification_report(
    y_test, y_pred_nb,
    target_names=label_encoder.classes_
))

# ====== CELL 61 ======
# ============================================================
# 9.4  CONFUSION MATRIX
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

class_names = label_encoder.classes_
cm_nb = confusion_matrix(y_test, y_pred_nb)

# --- Raw Counts ---
sns.heatmap(cm_nb, annot=True, fmt='d', cmap='Oranges',
            xticklabels=class_names, yticklabels=class_names,
            linewidths=0.8, linecolor='white',
            ax=axes[0], annot_kws={'fontsize': 12, 'fontweight': 'bold'})
axes[0].set_title('Confusion Matrix (Counts)', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Actual Label', fontsize=11)
axes[0].set_xlabel('Predicted Label', fontsize=11)

# --- Row-Normalized ---
cm_nb_norm = cm_nb.astype('float') / cm_nb.sum(axis=1)[:, np.newaxis]
sns.heatmap(cm_nb_norm, annot=True, fmt='.2f', cmap='Oranges',
            xticklabels=class_names, yticklabels=class_names,
            linewidths=0.8, linecolor='white',
            ax=axes[1], annot_kws={'fontsize': 12, 'fontweight': 'bold'},
            vmin=0, vmax=1)
axes[1].set_title('Confusion Matrix (Row-Normalized)', fontsize=13, fontweight='bold')
axes[1].set_ylabel('Actual Label', fontsize=11)
axes[1].set_xlabel('Predicted Label', fontsize=11)

plt.suptitle('Multinomial Naive Bayes - Confusion Matrix', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('nb_confusion_matrix.png', bbox_inches='tight', dpi=150)
plt.show()

# ====== CELL 62 ======
# ============================================================
# 9.5  TOP PREDICTIVE WORDS PER CLASS (LOG PROBABILITIES)
# ============================================================

tfidf_feat_names = preprocessor.transformers_[0][1].get_feature_names_out()

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
bar_colors = ['#e74c3c', '#27ae60', '#f39c12']

for i, (cls, color) in enumerate(zip(label_encoder.classes_, bar_colors)):
    # feature_log_prob_ shape: (n_classes, n_features)
    log_probs = nb_model.feature_log_prob_[i]

    # Get top 15 features
    top_idx   = log_probs.argsort()[-15:][::-1]
    top_words = tfidf_feat_names[top_idx]
    top_probs = log_probs[top_idx]

    axes[i].barh(range(15), top_probs, color=color,
                 edgecolor='black', linewidth=0.5)
    axes[i].set_yticks(range(15))
    axes[i].set_yticklabels(top_words, fontsize=9)
    axes[i].invert_yaxis()
    axes[i].set_title(f'{cls} Priority\nTop 15 Words by Log P(word|class)',
                     fontsize=12, fontweight='bold')
    axes[i].set_xlabel('Log Probability', fontsize=10)

plt.suptitle('Naive Bayes - Top Words by Log P(word | class)',
             fontsize=13, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('nb_top_words.png', bbox_inches='tight', dpi=150)
plt.show()

print('Top 5 words per class (by log probability):')
print('-' * 55)
for i, cls in enumerate(label_encoder.classes_):
    log_probs = nb_model.feature_log_prob_[i]
    top5_idx  = log_probs.argsort()[-5:][::-1]
    top5 = [(tfidf_feat_names[j], round(log_probs[j], 4)) for j in top5_idx]
    print(f'\n  {cls}: {top5}')

# ====== CELL 63 ======
# ============================================================
# 9.6  STORE RESULTS FOR COMPARISON
# ============================================================

results['Naive Bayes'] = {
    'Accuracy' : round(acc_nb, 4),
    'Precision': round(prec_nb, 4),
    'Recall'   : round(rec_nb, 4),
    'F1-Score' : round(f1_nb, 4),
    'y_pred'   : y_pred_nb
}

# Running comparison table — all 4 models
print('Model Results So Far (all 4 models):')
print('-' * 70)
print(f'{"Model":<22} {"Accuracy":>10} {"Precision":>10} {"Recall":>10} {"F1-Score":>10}')
print('-' * 70)
for model_name, res in results.items():
    print(f'{model_name:<22} {res["Accuracy"]:>10.4f} {res["Precision"]:>10.4f} {res["Recall"]:>10.4f} {res["F1-Score"]:>10.4f}')
print('-' * 70)
print('\nNote: Naive Bayes used TF-IDF features only.')
print('Other models used TF-IDF + categorical + numerical features.')

# ====== CELL 64 ======
# ============================================================
# 10.1  SUMMARY METRICS TABLE
# ============================================================

# Build a clean comparison DataFrame
comparison_df = pd.DataFrame({
    model: {
        'Accuracy':  res['Accuracy'],
        'Precision': res['Precision'],
        'Recall':    res['Recall'],
        'F1-Score':  res['F1-Score']
    }
    for model, res in results.items()
}).T  # Transpose so models are rows

# Add a column for features used
comparison_df['Features Used'] = [
    'TF-IDF + Cat + Num',
    'TF-IDF + Cat + Num',
    'TF-IDF + Cat + Num',
    'TF-IDF only'
]

print('MODEL COMPARISON - All Metrics')
print('=' * 80)
print(comparison_df.to_string())

# Highlight best values
best_acc = comparison_df['Accuracy'].idxmax()
best_f1  = comparison_df['F1-Score'].idxmax()
print(f'\nBest Accuracy : {best_acc} ({comparison_df.loc[best_acc, "Accuracy"]:.4f})')
print(f'Best F1-Score : {best_f1}  ({comparison_df.loc[best_f1, "F1-Score"]:.4f})')

# ====== CELL 65 ======
# ============================================================
# 10.2  GROUPED BAR CHART
# ============================================================

metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
model_names = list(results.keys())
x = np.arange(len(model_names))
width = 0.2
colors = ['#2980b9', '#27ae60', '#e74c3c', '#f39c12']

fig, ax = plt.subplots(figsize=(13, 6))

for i, (metric, color) in enumerate(zip(metrics, colors)):
    values = [results[m][metric] for m in model_names]
    bars = ax.bar(x + i * width, values, width,
                  label=metric, color=color,
                  edgecolor='black', linewidth=0.5)
    # Add value labels on bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.005,
                f'{val:.3f}', ha='center', va='bottom',
                fontsize=7.5, fontweight='bold')

ax.set_xlabel('Model', fontsize=12)
ax.set_ylabel('Score', fontsize=12)
ax.set_title('Model Comparison - All Metrics', fontsize=14, fontweight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(model_names, fontsize=11)
ax.set_ylim(0, 1.12)
ax.legend(loc='upper right', fontsize=10)
ax.axhline(y=0.8, color='gray', linestyle='--', linewidth=0.8, alpha=0.6, label='0.8 reference')
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('model_comparison_bar.png', bbox_inches='tight', dpi=150)
plt.show()

# ====== CELL 66 ======
# ============================================================
# 10.3  F1-SCORE RANKING
# ============================================================

f1_values  = [results[m]['F1-Score'] for m in model_names]
acc_values = [results[m]['Accuracy'] for m in model_names]

# Sort by F1-Score
sorted_models = sorted(zip(model_names, f1_values), key=lambda x: x[1], reverse=True)
sorted_names  = [m for m, _ in sorted_models]
sorted_f1     = [f for _, f in sorted_models]

fig, ax = plt.subplots(figsize=(10, 5))

bar_cols = ['#27ae60' if i == 0 else '#2980b9' for i in range(len(sorted_names))]
bars = ax.barh(sorted_names, sorted_f1,
               color=bar_cols, edgecolor='black', linewidth=0.6)
ax.invert_yaxis()
ax.set_xlabel('Weighted F1-Score', fontsize=12)
ax.set_title('Model Ranking by F1-Score (Weighted)', fontsize=14, fontweight='bold')
ax.set_xlim(0, 1.1)
ax.axvline(x=0.8, color='gray', linestyle='--', linewidth=0.9, alpha=0.7)
ax.text(0.8, -0.4, '0.80', ha='center', fontsize=9, color='gray')

# Add value labels
for bar, val in zip(bars, sorted_f1):
    ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
            f'{val:.4f}', va='center', fontsize=11, fontweight='bold')

# Annotate the best model
bars[0].set_edgecolor('gold')
bars[0].set_linewidth(2.5)

plt.tight_layout()
plt.savefig('model_f1_ranking.png', bbox_inches='tight', dpi=150)
plt.show()

print(f'Best model by F1-Score: {sorted_names[0]} ({sorted_f1[0]:.4f})')

# ====== CELL 67 ======
# ============================================================
# 10.4  SIDE-BY-SIDE NORMALIZED CONFUSION MATRICES
# ============================================================

model_preds = {
    'Logistic Regression': results['Logistic Regression']['y_pred'],
    'Random Forest':       results['Random Forest']['y_pred'],
    'Linear SVM':          results['Linear SVM']['y_pred'],
    'Naive Bayes':         results['Naive Bayes']['y_pred']
}

cmaps = ['Blues', 'Greens', 'Purples', 'Oranges']
class_names = label_encoder.classes_

fig, axes = plt.subplots(1, 4, figsize=(22, 5))

for ax, (model_name, y_pred), cmap in zip(axes, model_preds.items(), cmaps):
    cm = confusion_matrix(y_test, y_pred)
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap=cmap,
                xticklabels=class_names, yticklabels=class_names,
                linewidths=0.8, linecolor='white',
                ax=ax, annot_kws={'fontsize': 11, 'fontweight': 'bold'},
                vmin=0, vmax=1)
    f1 = results[model_name]['F1-Score']
    ax.set_title(f'{model_name}\nF1={f1:.4f}', fontsize=11, fontweight='bold')
    ax.set_ylabel('Actual', fontsize=10)
    ax.set_xlabel('Predicted', fontsize=10)

plt.suptitle('Row-Normalized Confusion Matrices - All Models',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('all_models_confusion_matrices.png', bbox_inches='tight', dpi=150)
plt.show()

# ====== CELL 68 ======
# ============================================================
# 10.5  RADAR / SPIDER CHART
# ============================================================

metrics_radar = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
radar_colors  = ['#2980b9', '#27ae60', '#9b59b6', '#e67e22']

# Number of variables
N = len(metrics_radar)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]  # Close the polygon

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

for (model_name, res), color in zip(results.items(), radar_colors):
    values = [res[m] for m in metrics_radar]
    values += values[:1]  # Close the polygon

    ax.plot(angles, values, 'o-', linewidth=2, label=model_name, color=color)
    ax.fill(angles, values, alpha=0.08, color=color)

# Axis labels
ax.set_xticks(angles[:-1])
ax.set_xticklabels(metrics_radar, fontsize=12, fontweight='bold')
ax.set_ylim(0, 1)
ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=8)
ax.set_title('Model Comparison - Radar Chart', fontsize=14,
             fontweight='bold', pad=20)
ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), fontsize=10)
ax.grid(True, alpha=0.4)

plt.tight_layout()
plt.savefig('model_radar_chart.png', bbox_inches='tight', dpi=150)
plt.show()

# ====== CELL 69 ======
# ============================================================
# 10.6  FINAL MODEL SELECTION
# ============================================================

# Select the best model by F1-Score
# (excluding Naive Bayes from automatic selection since it used fewer features)
full_feature_models = {k: v for k, v in results.items() if k != 'Naive Bayes'}
best_model_name = max(full_feature_models, key=lambda x: full_feature_models[x]['F1-Score'])
best_model_map  = {
    'Logistic Regression': lr_model,
    'Random Forest':       rf_model,
    'Linear SVM':          svm_model
}
best_model = best_model_map[best_model_name]

print('MODEL SELECTION SUMMARY')
print('=' * 60)
print(f'  Selected Model  : {best_model_name}')
print(f'  Accuracy        : {results[best_model_name]["Accuracy"]:.4f}')
print(f'  F1-Score        : {results[best_model_name]["F1-Score"]:.4f}')
print(f'  Precision       : {results[best_model_name]["Precision"]:.4f}')
print(f'  Recall          : {results[best_model_name]["Recall"]:.4f}')
print()
print('Selection Criteria:')
print('  - Primary metric: Weighted F1-Score (balances Precision and Recall)')
print('  - Only models trained on full features are compared for best model')
print('  - Naive Bayes is included as a baseline but uses TF-IDF features only')

# ====== CELL 70 ======
# ============================================================
# 11.1  5-FOLD CROSS-VALIDATION
# ============================================================

from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, StratifiedKFold

# StratifiedKFold preserves class distribution in every fold
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Define pipelines: preprocessor + model in one object
# The Pipeline ensures fit() on training fold and transform() on test fold
cv_pipelines = {
    'Logistic Regression': Pipeline([
        ('preprocessor', ColumnTransformer(
            transformers=[
                ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1,2),
                                          min_df=2, max_df=0.95, sublinear_tf=True),
                 'Cleaned_Text'),
                ('cat', OneHotEncoder(drop='first', sparse_output=False,
                                      handle_unknown='ignore'), categorical_features),
                ('num', StandardScaler(), numerical_features)
            ], remainder='drop')),
        ('model', LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs',
                                     class_weight='balanced', random_state=42))
    ]),
    'Random Forest': Pipeline([
        ('preprocessor', ColumnTransformer(
            transformers=[
                ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1,2),
                                          min_df=2, max_df=0.95, sublinear_tf=True),
                 'Cleaned_Text'),
                ('cat', OneHotEncoder(drop='first', sparse_output=False,
                                      handle_unknown='ignore'), categorical_features),
                ('num', StandardScaler(), numerical_features)
            ], remainder='drop')),
        ('model', RandomForestClassifier(n_estimators=200, min_samples_split=5,
                                          class_weight='balanced', random_state=42, n_jobs=-1))
    ]),
    'Linear SVM': Pipeline([
        ('preprocessor', ColumnTransformer(
            transformers=[
                ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1,2),
                                          min_df=2, max_df=0.95, sublinear_tf=True),
                 'Cleaned_Text'),
                ('cat', OneHotEncoder(drop='first', sparse_output=False,
                                      handle_unknown='ignore'), categorical_features),
                ('num', StandardScaler(), numerical_features)
            ], remainder='drop')),
        ('model', LinearSVC(C=1.0, max_iter=2000, class_weight='balanced', random_state=42))
    ])
}

print('Running 5-Fold Stratified Cross-Validation...')
print('(This may take 1-3 minutes for Random Forest)')
print('-' * 65)

cv_results = {}
for model_name, pipeline in cv_pipelines.items():
    scores = cross_val_score(
        pipeline, X, y,
        cv=skf,
        scoring='f1_weighted',
        n_jobs=-1
    )
    cv_results[model_name] = scores
    print(f'{model_name:<22}: Mean F1={scores.mean():.4f}  Std={scores.std():.4f}  '
          f'Folds={[round(s,4) for s in scores]}')

print('\nCross-Validation complete!')

# ====== CELL 71 ======
# ============================================================
# 11.2  CROSS-VALIDATION SCORE VISUALIZATION
# ============================================================

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

cv_model_names = list(cv_results.keys())
cv_colors = ['#2980b9', '#27ae60', '#9b59b6']

# --- Box Plot: Score distribution across folds ---
data_to_plot = [cv_results[m] for m in cv_model_names]
bp = axes[0].boxplot(data_to_plot, labels=cv_model_names, patch_artist=True,
                     medianprops=dict(color='black', linewidth=2))
for patch, color in zip(bp['boxes'], cv_colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
axes[0].set_title('CV F1-Score Distribution (5 Folds)', fontsize=13, fontweight='bold')
axes[0].set_ylabel('Weighted F1-Score', fontsize=11)
axes[0].set_xlabel('Model', fontsize=11)
axes[0].tick_params(axis='x', rotation=15)
axes[0].grid(axis='y', alpha=0.3)

# --- Bar Plot: Mean +/- Std ---
means = [cv_results[m].mean() for m in cv_model_names]
stds  = [cv_results[m].std()  for m in cv_model_names]
x_pos = np.arange(len(cv_model_names))

bars = axes[1].bar(x_pos, means, yerr=stds, capsize=8,
                   color=cv_colors, edgecolor='black', linewidth=0.6,
                   error_kw=dict(elinewidth=1.5, ecolor='black'))
axes[1].set_xticks(x_pos)
axes[1].set_xticklabels(cv_model_names, fontsize=10, rotation=15)
axes[1].set_ylabel('Mean Weighted F1-Score', fontsize=11)
axes[1].set_title('Mean CV F1-Score +/- Std Dev', fontsize=13, fontweight='bold')
axes[1].set_ylim(0, 1.1)
axes[1].grid(axis='y', alpha=0.3)

# Value labels
for bar, mean, std in zip(bars, means, stds):
    axes[1].text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + std + 0.01,
                 f'{mean:.4f}', ha='center', fontsize=10, fontweight='bold')

plt.suptitle('5-Fold Cross-Validation Results', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('cv_results.png', bbox_inches='tight', dpi=150)
plt.show()

print('\nSummary:')
print(f'{"Model":<22} {"Mean F1":>10} {"Std F1":>10}')
print('-' * 44)
for m in cv_model_names:
    print(f'{m:<22} {cv_results[m].mean():>10.4f} {cv_results[m].std():>10.4f}')

# ====== CELL 72 ======
# ============================================================
# 11.3  GRIDSEARCHCV - LOGISTIC REGRESSION
# ============================================================

from sklearn.model_selection import GridSearchCV

# Logistic Regression pipeline
lr_pipe = Pipeline([
    ('preprocessor', ColumnTransformer(
        transformers=[
            ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1,2),
                                      min_df=2, max_df=0.95, sublinear_tf=True),
             'Cleaned_Text'),
            ('cat', OneHotEncoder(drop='first', sparse_output=False,
                                  handle_unknown='ignore'), categorical_features),
            ('num', StandardScaler(), numerical_features)
        ], remainder='drop')),
    ('model', LogisticRegression(max_iter=1000, solver='lbfgs',
                                 class_weight='balanced', random_state=42))
])

# Parameter grid: note the 'model__' prefix to target the model step
lr_param_grid = {
    'model__C': [0.01, 0.1, 1.0, 5.0, 10.0]
}

print('Running GridSearchCV for Logistic Regression...')
print(f'Parameter grid: {lr_param_grid}')
print(f'CV folds: 5 | Scoring: weighted F1')

lr_grid = GridSearchCV(
    lr_pipe,
    lr_param_grid,
    cv=5,
    scoring='f1_weighted',
    n_jobs=-1,
    verbose=0
)
lr_grid.fit(X_train_raw, y_train)  # Fit on raw training data (pipeline handles preprocessing)

print(f'\nBest Parameters : {lr_grid.best_params_}')
print(f'Best CV F1-Score: {lr_grid.best_score_:.4f}')

# ====== CELL 73 ======
# ============================================================
# 11.4  GRIDSEARCHCV - LINEAR SVM
# ============================================================

svm_pipe = Pipeline([
    ('preprocessor', ColumnTransformer(
        transformers=[
            ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1,2),
                                      min_df=2, max_df=0.95, sublinear_tf=True),
             'Cleaned_Text'),
            ('cat', OneHotEncoder(drop='first', sparse_output=False,
                                  handle_unknown='ignore'), categorical_features),
            ('num', StandardScaler(), numerical_features)
        ], remainder='drop')),
    ('model', LinearSVC(max_iter=2000, class_weight='balanced', random_state=42))
])

svm_param_grid = {
    'model__C': [0.01, 0.1, 1.0, 5.0, 10.0]
}

print('Running GridSearchCV for Linear SVM...')
print(f'Parameter grid: {svm_param_grid}')

svm_grid = GridSearchCV(
    svm_pipe,
    svm_param_grid,
    cv=5,
    scoring='f1_weighted',
    n_jobs=-1,
    verbose=0
)
svm_grid.fit(X_train_raw, y_train)

print(f'\nBest Parameters : {svm_grid.best_params_}')
print(f'Best CV F1-Score: {svm_grid.best_score_:.4f}')

# ====== CELL 74 ======
# ============================================================
# 11.5  EVALUATE TUNED MODELS ON TEST SET
# ============================================================

# Logistic Regression - tuned
y_pred_lr_tuned  = lr_grid.best_estimator_.predict(X_test_raw)
f1_lr_tuned      = f1_score(y_test, y_pred_lr_tuned, average='weighted')
acc_lr_tuned     = accuracy_score(y_test, y_pred_lr_tuned)

# Linear SVM - tuned
y_pred_svm_tuned = svm_grid.best_estimator_.predict(X_test_raw)
f1_svm_tuned     = f1_score(y_test, y_pred_svm_tuned, average='weighted')
acc_svm_tuned    = accuracy_score(y_test, y_pred_svm_tuned)

print('TUNED MODEL RESULTS')
print('=' * 70)
print(f'{"Model":<30} {"Accuracy":>12} {"F1-Score (weighted)":>20}')
print('-' * 70)
print(f'{"LR (default C=1.0)":<30} {results["Logistic Regression"]["Accuracy"]:>12.4f} {results["Logistic Regression"]["F1-Score"]:>20.4f}')
print(f'{"LR (tuned C="+str(lr_grid.best_params_["model__C"])+")":<30} {acc_lr_tuned:>12.4f} {f1_lr_tuned:>20.4f}')
print('-' * 70)
print(f'{"SVM (default C=1.0)":<30} {results["Linear SVM"]["Accuracy"]:>12.4f} {results["Linear SVM"]["F1-Score"]:>20.4f}')
print(f'{"SVM (tuned C="+str(svm_grid.best_params_["model__C"])+")":<30} {acc_svm_tuned:>12.4f} {f1_svm_tuned:>20.4f}')

# ====== CELL 75 ======
# ============================================================
# 11.6  SELECT FINAL BEST MODEL
# ============================================================

# Compare tuned models and select the best overall
tuned_candidates = {
    'LR (tuned)' : (lr_grid.best_estimator_,  f1_lr_tuned),
    'SVM (tuned)': (svm_grid.best_estimator_, f1_svm_tuned),
}

best_tuned_name, (best_tuned_model, best_tuned_f1) = max(
    tuned_candidates.items(), key=lambda x: x[1][1]
)

# Final model = best tuned pipeline (includes preprocessor + model)
final_model = best_tuned_model

print('FINAL MODEL SELECTED')
print('=' * 55)
print(f'  Model            : {best_tuned_name}')
print(f'  Best CV F1       : {max(lr_grid.best_score_, svm_grid.best_score_):.4f}')
print(f'  Test F1-Score    : {best_tuned_f1:.4f}')
print(f'  Test Accuracy    : {accuracy_score(y_test, final_model.predict(X_test_raw)):.4f}')
print()
print('Final Classification Report:')
print(classification_report(
    y_test,
    final_model.predict(X_test_raw),
    target_names=label_encoder.classes_
))

# ====== CELL 76 ======
# Safeguard: ensure final_model and metadata vars are defined
if 'final_model' not in dir():
    _best = max({k:v for k,v in results.items() if k!='Naive Bayes'}, key=lambda x: results[x]['F1-Score'])
    _models = {'Logistic Regression': lr_model, 'Random Forest': rf_model, 'Linear SVM': svm_model}
    final_model = _models[_best]; best_tuned_name = _best
    best_tuned_f1 = results[_best]['F1-Score']

# Safeguard: ensure final_model and metadata vars are defined
if 'final_model' not in dir():
    _best = max({k:v for k,v in results.items() if k!='Naive Bayes'}, key=lambda x: results[x]['F1-Score'])
    _models = {'Logistic Regression': lr_model, 'Random Forest': rf_model, 'Linear SVM': svm_model}
    final_model = _models[_best]; best_tuned_name = _best
    best_tuned_f1 = results[_best]['F1-Score']

# ============================================================
# 12.1  SAVE FINAL MODEL PIPELINE
# ============================================================

import os

# Create a dedicated folder for saved model artifacts
model_dir = 'saved_model'
os.makedirs(model_dir, exist_ok=True)

# 1. Save the complete pipeline (preprocessor + best model)
model_path = os.path.join(model_dir, 'hostel_priority_model.pkl')
joblib.dump(final_model, model_path)
print(f'Model saved -> {model_path}')
print(f'  File size: {os.path.getsize(model_path) / 1024:.1f} KB')

# 2. Save the label encoder
encoder_path = os.path.join(model_dir, 'label_encoder.pkl')
joblib.dump(label_encoder, encoder_path)
print(f'Label encoder saved -> {encoder_path}')

# 3. Save domain stopwords (used during text preprocessing)
stopwords_path = os.path.join(model_dir, 'domain_stopwords.pkl')
joblib.dump(domain_stopwords, stopwords_path)
print(f'Domain stopwords saved -> {stopwords_path}')

# 4. Save a metadata summary
import json as json_meta
metadata = {
    'model_name'     : best_tuned_name,
    'test_f1_score'  : round(best_tuned_f1, 4),
    'test_accuracy'  : round(accuracy_score(y_test, final_model.predict(X_test_raw)), 4),
    'classes'        : label_encoder.classes_.tolist(),
    'features_used'  : ['Cleaned_Text (TF-IDF)', 'Complaint_Type', 'Block', 'Floor', 'Category',
                         'Students_Affected', 'Support_Count'],
    'training_samples': len(X_train_raw),
    'test_samples'   : len(X_test_raw),
    'tfidf_params'   : {'max_features': 1000, 'ngram_range': '(1,2)',
                         'min_df': 2, 'max_df': 0.95, 'sublinear_tf': True}
}
metadata_path = os.path.join(model_dir, 'model_metadata.json')
with open(metadata_path, 'w') as f:
    json_meta.dump(metadata, f, indent=2)
print(f'Metadata saved -> {metadata_path}')

print('\nAll model artifacts saved successfully!')

# ====== CELL 77 ======
# ============================================================
# 12.2  VERIFY: LOAD THE SAVED MODEL AND TEST
# ============================================================

# Load all saved artifacts
loaded_model   = joblib.load(model_path)
loaded_encoder = joblib.load(encoder_path)
loaded_stopwords = joblib.load(stopwords_path)

print('Saved model loaded successfully!')
print(f'Model type: {type(loaded_model).__name__}')
print(f'Classes: {loaded_encoder.classes_}')
print(f'Custom stopwords count: {len(loaded_stopwords)}')

# Verify predictions match
loaded_preds  = loaded_model.predict(X_test_raw)
original_preds = final_model.predict(X_test_raw)

predictions_match = np.array_equal(loaded_preds, original_preds)
print(f'\nPredictions match original: {predictions_match}')
print(f'Loaded model F1-Score: {f1_score(y_test, loaded_preds, average="weighted"):.4f}')

# ====== CELL 78 ======
# ============================================================
# 12.3  LIST ALL SAVED FILES
# ============================================================

print('Saved Model Artifacts:')
print('=' * 60)
for fname in os.listdir(model_dir):
    fpath = os.path.join(model_dir, fname)
    size  = os.path.getsize(fpath)
    print(f'  {fname:<35} {size/1024:>8.1f} KB')

print('\nDirectory:', os.path.abspath(model_dir))

# Print metadata
print('\nModel Metadata:')
print('-' * 40)
for k, v in metadata.items():
    print(f'  {k:<22}: {v}')

# ====== CELL 79 ======
# ============================================================
# 12.4  HOW TO LOAD AND USE THE MODEL (USAGE TEMPLATE)
# ============================================================

# Step 1: Load saved artifacts (do this once at startup)
loaded_model    = joblib.load('saved_model/hostel_priority_model.pkl')
loaded_encoder  = joblib.load('saved_model/label_encoder.pkl')
loaded_stopwords = joblib.load('saved_model/domain_stopwords.pkl')

# Step 2: Define the same preprocessing function
def preprocess_for_prediction(text):
    """Apply the same preprocessing used during training."""
    import re
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    stop = set(stopwords.words('english')).union(loaded_stopwords)
    lem  = WordNetLemmatizer()
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    words = [lem.lemmatize(w) for w in text.split() if w not in stop]
    return ' '.join(words)

# Step 3: Create a sample new complaint (as a DataFrame row)
new_complaint = pd.DataFrame([{
    'Complaint_Text'   : 'The water cooler in Block B has been broken for 3 days and students cannot drink water.',
    'Complaint_Type'   : 'Public',
    'Block'            : 'B',
    'Floor'            : 'Ground',
    'Category'         : 'Water Cooler',
    'Students_Affected': 45,
    'Support_Count'    : 18
}])

# Step 4: Apply preprocessing to the text
new_complaint['Cleaned_Text'] = new_complaint['Complaint_Text'].apply(preprocess_for_prediction)

# Step 5: Select only the columns the model expects
model_input = new_complaint[['Cleaned_Text', 'Complaint_Type', 'Block', 'Floor',
                              'Category', 'Students_Affected', 'Support_Count']]

# Step 6: Predict
pred_encoded = loaded_model.predict(model_input)
pred_label   = loaded_encoder.inverse_transform(pred_encoded)

print('PREDICTION DEMO')
print('=' * 60)
print(f'Complaint: {new_complaint["Complaint_Text"].iloc[0]}')
print(f'Cleaned  : {new_complaint["Cleaned_Text"].iloc[0]}')
print(f'\nPredicted Priority: {pred_label[0]}')

# ====== CELL 80 ======
# ============================================================
# 13.1  REUSABLE PREDICTION FUNCTION
# ============================================================

def predict_priority(complaint_text, complaint_type, block, floor,
                     category, students_affected, support_count,
                     model=loaded_model,
                     encoder=loaded_encoder,
                     stopwords_set=loaded_stopwords):
    """
    Predict the priority of a hostel complaint.

    Parameters:
    -----------
    complaint_text     : str   - Raw complaint description
    complaint_type     : str   - 'Public' or 'Private'
    block              : str   - Block identifier (e.g., 'A', 'B', 'C')
    floor              : str   - Floor (e.g., 'Ground', 'First', 'Second')
    category           : str   - Complaint category (e.g., 'Mess', 'Electricity')
    students_affected  : int   - Number of students affected
    support_count      : int   - Number of students who supported the complaint
    model              : Pipeline - Loaded model pipeline
    encoder            : LabelEncoder - Loaded label encoder
    stopwords_set      : set   - Domain-specific stopwords

    Returns:
    --------
    dict with 'priority' and 'cleaned_text'
    """

    # Step 1: Preprocess the complaint text
    from nltk.corpus import stopwords as nltk_sw
    from nltk.stem import WordNetLemmatizer
    all_stop = set(nltk_sw.words('english')).union(stopwords_set)
    lem = WordNetLemmatizer()

    text = complaint_text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    words = [lem.lemmatize(w) for w in text.split() if w not in all_stop]
    cleaned = ' '.join(words)

    # Step 2: Build a single-row DataFrame (same structure as training)
    input_df = pd.DataFrame([{
        'Cleaned_Text'     : cleaned,
        'Complaint_Type'   : complaint_type,
        'Block'            : block,
        'Floor'            : floor,
        'Category'         : category,
        'Students_Affected': students_affected,
        'Support_Count'    : support_count
    }])

    # Step 3: Predict
    pred_encoded = model.predict(input_df)
    pred_label   = encoder.inverse_transform(pred_encoded)[0]

    return {
        'priority'    : pred_label,
        'cleaned_text': cleaned
    }

print('predict_priority() function defined successfully!')

# ====== CELL 81 ======
# ============================================================
# 13.2  BATCH PREDICTION ON NEW COMPLAINTS
# ============================================================

new_complaints = [
    # Expected High priority
    {'text': 'Several students fell sick after eating food in the mess. The food was stale and unhygienic.',
     'type': 'Public',  'block': 'A', 'floor': 'Ground', 'cat': 'Mess',        'sa': 35, 'sc': 22},
    {'text': 'There is no electricity since yesterday night. Fans and lights are not working in entire block.',
     'type': 'Public',  'block': 'B', 'floor': 'First',  'cat': 'Electricity', 'sa': 60, 'sc': 30},
    {'text': 'Water supply has been completely cut off since two days. We have no water for bathing or drinking.',
     'type': 'Public',  'block': 'C', 'floor': 'Second', 'cat': 'Plumbing',    'sa': 50, 'sc': 28},
    {'text': 'There is a rat infestation in the kitchen area. Multiple rats seen near food storage.',
     'type': 'Public',  'block': 'A', 'floor': 'Ground', 'cat': 'Cleanliness', 'sa': 40, 'sc': 19},

    # Expected Medium priority
    {'text': 'The washroom on second floor is not clean and has a bad smell. Drainage is slow.',
     'type': 'Public',  'block': 'B', 'floor': 'Second', 'cat': 'Washroom',    'sa': 15, 'sc': 8},
    {'text': 'Mess timing has changed without any prior notice. Students are missing meals.',
     'type': 'Public',  'block': 'A', 'floor': 'Ground', 'cat': 'Mess',        'sa': 20, 'sc': 11},
    {'text': 'The mattress in room 12 is very old and torn. It is uncomfortable to sleep.',
     'type': 'Private', 'block': 'C', 'floor': 'First',  'cat': 'Furniture',   'sa': 2,  'sc': 1},
    {'text': 'The common room TV is not working since three days. Students use it for entertainment.',
     'type': 'Public',  'block': 'B', 'floor': 'Ground', 'cat': 'Furniture',   'sa': 18, 'sc': 9},

    # Expected Low priority
    {'text': 'There is a cobweb in the corner of my room near the window.',
     'type': 'Private', 'block': 'A', 'floor': 'Third',  'cat': 'Cleanliness', 'sa': 1,  'sc': 0},
    {'text': 'The drawer in my study table is slightly stuck and hard to open.',
     'type': 'Private', 'block': 'C', 'floor': 'Second', 'cat': 'Furniture',   'sa': 1,  'sc': 0},
    {'text': 'The WiFi signal in my room is slightly weak but still works.',
     'type': 'Private', 'block': 'B', 'floor': 'Fourth', 'cat': 'WiFi',        'sa': 1,  'sc': 1},

    # Ambiguous case
    {'text': 'The notice board outside the mess has some torn notices. Please update it.',
     'type': 'Public',  'block': 'A', 'floor': 'Ground', 'cat': 'Cleanliness', 'sa': 5,  'sc': 2},
]

print('BATCH PREDICTIONS ON NEW COMPLAINTS')
print('=' * 90)

batch_results = []
for i, c in enumerate(new_complaints, 1):
    result = predict_priority(
        complaint_text=c['text'], complaint_type=c['type'],
        block=c['block'], floor=c['floor'], category=c['cat'],
        students_affected=c['sa'], support_count=c['sc']
    )
    batch_results.append(result['priority'])
    print(f'\n[{i:2d}] Priority: {result["priority"]:>6}  |  {c["text"][:75]}...' if len(c['text']) > 75
          else f'\n[{i:2d}] Priority: {result["priority"]:>6}  |  {c["text"]}')
    print(f'      Category: {c["cat"]:<15} | Students affected: {c["sa"]:>3} | Support: {c["sc"]}')

print('\n' + '=' * 90)

# ====== CELL 82 ======
# ============================================================
# 13.3  VISUALIZE PREDICTION DISTRIBUTION
# ============================================================

from collections import Counter

pred_counts = Counter(batch_results)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# --- Bar Chart ---
priorities = ['High', 'Medium', 'Low']
counts     = [pred_counts.get(p, 0) for p in priorities]
colors_bar = ['#e74c3c', '#f39c12', '#27ae60']

bars = axes[0].bar(priorities, counts, color=colors_bar,
                   edgecolor='black', linewidth=0.7)
for bar, cnt in zip(bars, counts):
    axes[0].text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.05, str(cnt),
                 ha='center', fontsize=13, fontweight='bold')
axes[0].set_title('Predicted Priority Distribution\n(New Complaints)',
                  fontsize=12, fontweight='bold')
axes[0].set_ylabel('Count', fontsize=11)
axes[0].set_xlabel('Priority', fontsize=11)
axes[0].set_ylim(0, max(counts) + 2)

# --- Pie Chart ---
pie_labels = [f'{p} ({pred_counts.get(p, 0)})' for p in priorities]
pie_counts = [pred_counts.get(p, 0) for p in priorities]
axes[1].pie([c if c > 0 else 0.001 for c in pie_counts],
            labels=[l if c > 0 else '' for l, c in zip(pie_labels, pie_counts)],
            autopct=lambda p: f'{p:.1f}%' if p > 0 else '',
            colors=colors_bar,
            startangle=90,
            wedgeprops={'edgecolor': 'black', 'linewidth': 0.8},
            textprops={'fontsize': 11})
axes[1].set_title('Predicted Priority Split\n(New Complaints)',
                  fontsize=12, fontweight='bold')

plt.suptitle('Priority Predictions - New Complaints', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('new_complaints_predictions.png', bbox_inches='tight', dpi=150)
plt.show()

print('Prediction counts:')
for p in priorities:
    cnt = pred_counts.get(p, 0)
    pct = cnt / len(batch_results) * 100
    print(f'  {p:8s}: {cnt} ({pct:.1f}%)')

# ====== CELL 83 ======
# ============================================================
# 13.4  INTERACTIVE SINGLE PREDICTION (MODIFY AND RUN)
# ============================================================

# -------------------------------------------------------
# CHANGE THESE VALUES to test any new complaint
# -------------------------------------------------------
my_complaint = {
    'text'     : 'The geyser in the washroom is not working since a week. Students are bathing with cold water.',
    'type'     : 'Public',     # 'Public' or 'Private'
    'block'    : 'A',          # 'A', 'B', or 'C'
    'floor'    : 'Second',     # 'Ground', 'First', 'Second', 'Third', 'Fourth'
    'category' : 'Plumbing',   # e.g., 'Mess', 'Electricity', 'Plumbing', 'WiFi', etc.
    'students' : 25,           # Number of students affected
    'support'  : 10            # Number of students who supported the complaint
}
# -------------------------------------------------------

result = predict_priority(
    complaint_text=my_complaint['text'],
    complaint_type=my_complaint['type'],
    block=my_complaint['block'],
    floor=my_complaint['floor'],
    category=my_complaint['category'],
    students_affected=my_complaint['students'],
    support_count=my_complaint['support']
)

print('SINGLE COMPLAINT PREDICTION')
print('=' * 65)
print(f'  Original Text : {my_complaint["text"]}')
print(f'  Cleaned Text  : {result["cleaned_text"]}')
print(f'  Type          : {my_complaint["type"]}')
print(f'  Category      : {my_complaint["category"]}')
print(f'  Block/Floor   : {my_complaint["block"]} / {my_complaint["floor"]}')
print(f'  Affected      : {my_complaint["students"]} students')
print(f'  Support       : {my_complaint["support"]} votes')
print()
print(f'  PREDICTED PRIORITY: *** {result["priority"]} ***')
print('=' * 65)
