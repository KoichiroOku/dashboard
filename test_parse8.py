import pandas as pd
file_path = '../20260323_演習.xlsx'
df = pd.read_excel(file_path, sheet_name='2025-2026')
print(list(df.columns))
