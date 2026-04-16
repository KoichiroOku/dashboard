import pandas as pd
import numpy as np

file_path = '../20260323_演習.xlsx'
df = pd.read_excel(file_path, sheet_name='全車種分析_120')

col1 = '市街地での扱いやすさ(0~60km/h)'
print(df[col1].unique())
