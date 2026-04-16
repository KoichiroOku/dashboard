import pandas as pd
file_path = '../20260323_演習.xlsx'
df = pd.read_excel(file_path, sheet_name='全車種分析_120')
print("Columns in df:", [c for c in df.columns if 'セグメント' in c or 'ボディ' in c or 'SEGMENT' in c])
