import pandas as pd
file_path = '../20260323_演習.xlsx'
df_eval = pd.read_excel(file_path, sheet_name='全車種分析_120')
df_eval = df_eval.dropna(subset=['メーカー', '車種名'])
df_eval = df_eval[df_eval['メーカー'] != 'メーカー']

df_master = pd.read_excel(file_path, sheet_name='2025-2026', header=9)

if 'お薦めグレード価格(円)' in df_master.columns and '車種名' in df_master.columns:
    prices = df_master[['車種名', 'お薦めグレード価格(円)']].copy()
    prices['お薦めグレード価格(円)'] = pd.to_numeric(prices['お薦めグレード価格(円)'].astype(str).str.replace(',', ''), errors='coerce')
    merged = pd.merge(df_eval, prices, on='車種名', how='left')
    print("Merged shape:", merged.shape)
    print("Valid prices:", merged['お薦めグレード価格(円)'].notnull().sum())
    print("Sample rows:")
    print(merged[['車種名', 'お薦めグレード価格(円)']].head())
