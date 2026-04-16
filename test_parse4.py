import pandas as pd
import numpy as np
file_path = '../20260323_演習.xlsx'
df = pd.read_excel(file_path, sheet_name='全車種分析_120')
for col in df.columns:
    if '価格' in str(col) or '車両' in str(col) or '総合評価' in str(col):
        print(f"Col: '{col}'")
