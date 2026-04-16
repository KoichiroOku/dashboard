import pandas as pd
import numpy as np

file_path = '../20260323_演習.xlsx'
df = pd.read_excel(file_path, sheet_name='全車種分析_120')
# Drop trailing junk
df = df.dropna(subset=['メーカー', '車種名'])
df = df[df['メーカー'] != 'メーカー'] # in case of repeated header

# Find col start and end
cols = df.columns.tolist()
start_idx = cols.index('市街地での扱いやすさ(0~60km/h)')
end_idx = cols.index('リセールバリュー') + 1

eval_cols = cols[start_idx:end_idx]
print(f"Num rows: {len(df)}")
print(f"Eval cols ({len(eval_cols)}):", eval_cols)
