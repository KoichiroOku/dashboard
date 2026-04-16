import pandas as pd
file_path = '../20260323_演習.xlsx'
df = pd.read_excel(file_path, sheet_name='2025-2026', header=None, nrows=10)
for i in range(10):
    row = df.iloc[i].dropna().astype(str).tolist()
    if '車種名' in row or '価格(円)' in str(row):
        print(f"Row {i}:", row)
    for v in row:
        if '価格' in v or '価格(円)' in v:
            print(f"Row {i} Contains:", v)
