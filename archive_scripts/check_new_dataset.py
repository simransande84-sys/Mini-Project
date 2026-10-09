import pandas as pd

df = pd.read_csv(r'DATSETminiproject.csv')
print(f'Shape: {df.shape}')
print(f'Columns: {df.columns.tolist()}')
print(f'\nPriority counts:\n{df["Priority"].value_counts()}')
print(f'\nUnique Priority: {sorted(df["Priority"].unique())}')
print(f'Missing values:\n{df.isnull().sum()}')
print(f'Duplicates: {df.duplicated().sum()}')
print(f'\nStudents_Affected present: {"Students_Affected" in df.columns}')
print(f'Support_Count present: {"Support_Count" in df.columns}')
print(f'Critical in Priority: {"Critical" in df["Priority"].unique()}')
print(f'\nFirst Complaint_ID: {df["Complaint_ID"].iloc[0]}')
print(f'Last Complaint_ID: {df["Complaint_ID"].iloc[-1]}')
