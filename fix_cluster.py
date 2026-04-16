import pandas as pd
file_path = '../20260323_演習.xlsx'
df = pd.read_excel(file_path, sheet_name='全車種分析_120')
print(df['クラスター'].head(10))
