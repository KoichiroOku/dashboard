import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import prince
import json
import os
import warnings
warnings.filterwarnings('ignore')

file_path = '../20260323_演習.xlsx'
df = pd.read_excel(file_path, sheet_name='全車種分析_120')
df = df.dropna(subset=['メーカー', '車種名'])
df = df[df['メーカー'] != 'メーカー']

df_master = pd.read_excel(file_path, sheet_name='2025-2026', header=9)
if 'お薦めグレード価格(円)' in df_master.columns and '車種名' in df_master.columns:
    prices = df_master[['車種名', 'お薦めグレード価格(円)']].copy()
    prices['お薦めグレード価格(円)'] = pd.to_numeric(prices['お薦めグレード価格(円)'].astype(str).str.replace(',', ''), errors='coerce')
    df = pd.merge(df, prices, on='車種名', how='left')
else:
    df['お薦めグレード価格(円)'] = np.nan

# Clean body type missing values
df['ボディタイプ'] = df['ボディタイプ'].fillna('不明')
df['SEGMENT'] = df['SEGMENT'].fillna('不明')
df['CATEGORY'] = df['CATEGORY'].fillna('不明')

cols = df.columns.tolist()
start_idx = cols.index('市街地での扱いやすさ(0~60km/h)')
end_idx = cols.index('リセールバリュー') + 1
eval_cols = cols[start_idx:end_idx]

for c in eval_cols:
    df[c] = pd.to_numeric(df[c], errors='coerce')

df['総合評価(15点)'] = pd.to_numeric(df['総合評価(15点)'], errors='coerce')
df['コストパフォーマンス'] = pd.to_numeric(df['コストパフォーマンス'], errors='coerce')

df_clean = df.dropna(subset=eval_cols + ['総合評価(15点)']).copy()
X = df_clean[eval_cols].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Models
# PCA
pca = PCA(n_components=2)
principalComponents = pca.fit_transform(X_scaled)
df_clean['PC1'] = principalComponents[:, 0]
df_clean['PC2'] = principalComponents[:, 1]
pca_loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

# Regression
y_score = df_clean['総合評価(15点)'].values
reg_score = LinearRegression().fit(X_scaled, y_score)
score_coefs = reg_score.coef_

price_coefs = np.zeros(len(eval_cols))
df_price = df_clean.dropna(subset=['お薦めグレード価格(円)'])
if len(df_price) > 0:
    X_p = scaler.fit_transform(df_price[eval_cols].values)
    reg_price = LinearRegression().fit(X_p, df_price['お薦めグレード価格(円)'].values)
    price_coefs = reg_price.coef_

# CA
ca = prince.CA(n_components=2)
crosstab_ca = pd.crosstab(df_clean['車種名'], df_clean['CATEGORY'])
ca.fit(crosstab_ca)
ca_row = ca.row_coordinates(crosstab_ca)
ca_col = ca.column_coordinates(crosstab_ca)

# Quant III
ca3 = prince.CA(n_components=2)
crosstab3 = pd.crosstab(df_clean['車種名'], df_clean['SEGMENT'])
ca3.fit(crosstab3)
q3_row = ca3.row_coordinates(crosstab3)
q3_col = ca3.column_coordinates(crosstab3)

# Q1
df_dummy_s = pd.get_dummies(df_clean[['CATEGORY', 'SEGMENT']], drop_first=True)
reg_q1_s = LinearRegression().fit(df_dummy_s, df_clean['総合評価(15点)'])
q1_s_dict = dict(zip(df_dummy_s.columns, reg_q1_s.coef_))

q1_p_dict = {}
if len(df_price) > 0:
    df_dummy_p = pd.get_dummies(df_price[['CATEGORY', 'SEGMENT']], drop_first=True)
    reg_q1_p = LinearRegression().fit(df_dummy_p, df_price['お薦めグレード価格(円)'])
    q1_p_dict = dict(zip(df_dummy_p.columns, reg_q1_p.coef_))

# CS Portfolio
imp_t = []
ach_t = []
for c in eval_cols:
    imp = df_clean[c].corr(df_clean['総合評価(15点)'])
    ach = df_clean[c].mean()
    imp_t.append(imp)
    ach_t.append(ach)
imp_t = (np.array(imp_t) - np.nanmean(imp_t)) / np.nanstd(imp_t) * 10 + 50
ach_t = (np.array(ach_t) - np.nanmean(ach_t)) / np.nanstd(ach_t) * 10 + 50

car_score_t = (y_score - np.nanmean(y_score)) / np.nanstd(y_score) * 10 + 50
car_cp_raw = df_clean['コストパフォーマンス'].values
car_cp_t = (car_cp_raw - np.nanmean(car_cp_raw)) / np.nanstd(car_cp_raw) * 10 + 50

# Package JSON Data
CARS = []
for i, row in df_clean.reset_index().iterrows():
    cname = str(row['車種名'])
    CARS.append({
        'name': cname,
        'maker': str(row['メーカー']),
        'category': str(row['CATEGORY']),
        'segment': str(row['SEGMENT']),
        'body_type': str(row['ボディタイプ']),
        'cluster': str(row['クラスター']),
        'pc1': float(row['PC1']) if not np.isnan(row['PC1']) else 0,
        'pc2': float(row['PC2']) if not np.isnan(row['PC2']) else 0,
        'score_t': float(car_score_t[i]) if not np.isnan(car_score_t[i]) else 0,
        'cp_t': float(car_cp_t[i]) if not np.isnan(car_cp_t[i]) else 0,
        'ca_x': float(ca_row.loc[cname, 0]) if cname in ca_row.index else 0,
        'ca_y': float(ca_row.loc[cname, 1]) if cname in ca_row.index else 0,
        'q3_x': float(q3_row.loc[cname, 0]) if cname in q3_row.index else 0,
        'q3_y': float(q3_row.loc[cname, 1]) if cname in q3_row.index else 0
    })

VARIABLES = []
for i, c in enumerate(eval_cols):
    VARIABLES.append({
        'name': c,
        'pc1': float(pca_loadings[i, 0]),
        'pc2': float(pca_loadings[i, 1]),
        'reg_score': float(score_coefs[i]),
        'reg_price': float(price_coefs[i]),
        'imp_t': float(imp_t[i]) if not np.isnan(imp_t[i]) else 50,
        'ach_t': float(ach_t[i]) if not np.isnan(ach_t[i]) else 50
    })

CATEGORIES = []
for cat in ca_col.index:
    CATEGORIES.append({
        'name': str(cat),
        'ca_x': float(ca_col.loc[cat, 0]),
        'ca_y': float(ca_col.loc[cat, 1])
    })

SEGMENTS = []
for seg in q3_col.index:
    SEGMENTS.append({
        'name': str(seg),
        'q3_x': float(q3_col.loc[seg, 0]),
        'q3_y': float(q3_col.loc[seg, 1])
    })

def clean_dict(d):
    return {k: float(v) for k, v in d.items()}

DATA = {
    'CARS': CARS,
    'VARIABLES': VARIABLES,
    'CATEGORIES': CATEGORIES,
    'SEGMENTS': SEGMENTS,
    'Q1_SCORE': clean_dict(q1_s_dict),
    'Q1_PRICE': clean_dict(q1_p_dict),
    'VAR_EXPLAINED_1': float(pca.explained_variance_ratio_[0]),
    'VAR_EXPLAINED_2': float(pca.explained_variance_ratio_[1])
}

with open('analysis_data.js', 'w') as f:
    f.write('const ANALYSIS_DATA = ' + json.dumps(DATA, ensure_ascii=False) + ';\n')

print("Data exported successfully to analysis_data.js!")
