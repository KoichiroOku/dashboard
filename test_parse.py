import pandas as pd
import numpy as np

file_path = '../20260323_演習.xlsx'
df = pd.read_excel(file_path, sheet_name='全車種分析_120')

print("All columns:", list(df.columns))
print("Data head for numerical columns:", df.select_dtypes(include=[np.number]).columns.tolist())
