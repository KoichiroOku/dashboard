import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from factor_analyzer import FactorAnalyzer
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.linear_model import LinearRegression
import prince
import os
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'Hiragino Sans'

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

cols = df.columns.tolist()
start_idx = cols.index('市街地での扱いやすさ(0~60km/h)')
end_idx = cols.index('リセールバリュー') + 1
eval_cols = cols[start_idx:end_idx]

for c in eval_cols:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df['総合評価(15点)'] = pd.to_numeric(df['総合評価(15点)'], errors='coerce')

df_clean = df.dropna(subset=eval_cols + ['総合評価(15点)']).copy()
X = df_clean[eval_cols].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

out_dir = 'analysis_output'
os.makedirs(out_dir, exist_ok=True)

# 1a. PCA (Cars)
pca = PCA(n_components=2)
principalComponents = pca.fit_transform(X_scaled)
df_clean['PC1'] = principalComponents[:, 0]
df_clean['PC2'] = principalComponents[:, 1]
plt.figure(figsize=(14, 12))
sns.scatterplot(x='PC1', y='PC2', hue='CATEGORY', data=df_clean, palette='Set2')
for i, row in df_clean.iterrows():
    plt.annotate(row['車種名'], (row['PC1'], row['PC2']), fontsize=7, alpha=0.8)
plt.title('PCA 車種のポジショニングマップ (Annotated with Car Names)')
plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} Variance)')
plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} Variance)')
plt.grid(True)
plt.savefig(f'{out_dir}/pca_map.png', dpi=150, bbox_inches='tight')
plt.close()

# 1b. PCA (Variables - 30 Evaluation Items)
loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
plt.figure(figsize=(14, 12))
plt.scatter(loadings[:, 0], loadings[:, 1], color='purple')
for i, feature in enumerate(eval_cols):
    plt.annotate(feature, (loadings[i, 0], loadings[i, 1]), fontsize=9, alpha=0.9, color='indigo')
    plt.arrow(0, 0, loadings[i, 0]*0.95, loadings[i, 1]*0.95, color='purple', alpha=0.3, head_width=0.02)
plt.title('PCA 30項目の評価項目散布図（変数負荷量マップ）')
plt.xlabel(f'PC1')
plt.ylabel(f'PC2')
plt.axhline(0, color='grey', ls='--')
plt.axvline(0, color='grey', ls='--')
plt.grid(True)
plt.savefig(f'{out_dir}/pca_variables_map.png', dpi=150, bbox_inches='tight')
plt.close()

# 2. Factor Analysis
fa = FactorAnalyzer(n_factors=3, rotation='varimax')
fa.fit(X_scaled)
fa_loadings = pd.DataFrame(fa.loadings_, index=eval_cols, columns=['Factor1', 'Factor2', 'Factor3'])
plt.figure(figsize=(8, 10))
sns.heatmap(fa_loadings, cmap='coolwarm', center=0, annot=True, fmt='.2f')
plt.title('Factor Loadings Heatmap')
plt.savefig(f'{out_dir}/factor_map.png', dpi=150, bbox_inches='tight')
plt.close()

# 3. Cluster Analysis
linked = linkage(X_scaled[:50], 'ward')
plt.figure(figsize=(12, 6))
dendrogram(linked, labels=df_clean['車種名'].values[:50], orientation='top', leaf_rotation=90)
plt.title('Hierarchical Clustering Dendrogram (Sample 50)')
plt.savefig(f'{out_dir}/dendrogram.png', dpi=150, bbox_inches='tight')
plt.close()

# 4a. Multiple Regression (Target: 総合評価)
y_score = df_clean['総合評価(15点)'].values
reg_score = LinearRegression().fit(X_scaled, y_score)
coef_df1 = pd.DataFrame({'Feature': eval_cols, 'Coefficient': reg_score.coef_}).sort_values('Coefficient', ascending=False)
plt.figure(figsize=(10, 8))
sns.barplot(x='Coefficient', y='Feature', data=coef_df1, palette='viridis')
plt.title('Multiple Regression Coefficients (Target: 総合評価)')
plt.savefig(f'{out_dir}/regression_score.png', dpi=150, bbox_inches='tight')
plt.close()

# 4b. Multiple Regression (Target: 車両販売価格)
df_price = df_clean.dropna(subset=['お薦めグレード価格(円)'])
if len(df_price) > 0:
    X_p = scaler.fit_transform(df_price[eval_cols].values)
    y_price = df_price['お薦めグレード価格(円)'].values
    reg_price = LinearRegression().fit(X_p, y_price)
    coef_df2 = pd.DataFrame({'Feature': eval_cols, 'Coefficient': reg_price.coef_}).sort_values('Coefficient', ascending=False)
    plt.figure(figsize=(10, 8))
    sns.barplot(x='Coefficient', y='Feature', data=coef_df2, palette='magma')
    plt.title('Multiple Regression Coefficients (Target: 車両販売価格)')
    plt.savefig(f'{out_dir}/regression_price.png', dpi=150, bbox_inches='tight')
    plt.close()

# 5. Correspondence Analysis (車種名 vs CATEGORY)
ca = prince.CA(n_components=2)
crosstab = pd.crosstab(df_clean['車種名'], df_clean['CATEGORY'])
ca.fit(crosstab)
row_coords = ca.row_coordinates(crosstab)
col_coords = ca.column_coordinates(crosstab)
plt.figure(figsize=(14, 12))
sns.scatterplot(x=row_coords.iloc[:, 0], y=row_coords.iloc[:, 1], color='blue', alpha=0.5, label='Car')
sns.scatterplot(x=col_coords.iloc[:, 0], y=col_coords.iloc[:, 1], color='red', marker='X', s=100, label='Category')
for i, txt in enumerate(row_coords.index):
    plt.annotate(txt, (row_coords.iloc[i, 0], row_coords.iloc[i, 1]), fontsize=7, alpha=0.7)
for i, txt in enumerate(col_coords.index):
    plt.annotate(txt, (col_coords.iloc[i, 0], col_coords.iloc[i, 1]), fontsize=12, color='red', weight='bold')
plt.title('Correspondence Analysis Map (Car Name vs Category)')
plt.legend()
plt.grid(True)
plt.savefig(f'{out_dir}/correspondence_map.png', dpi=150, bbox_inches='tight')
plt.close()

# 6. Quantification Theory III (車種名 vs SEGMENT)
ca3 = prince.CA(n_components=2)
crosstab3 = pd.crosstab(df_clean['車種名'], df_clean['SEGMENT'])
ca3.fit(crosstab3)
row_coords3 = ca3.row_coordinates(crosstab3)
col_coords3 = ca3.column_coordinates(crosstab3)
plt.figure(figsize=(14, 12))
sns.scatterplot(x=row_coords3.iloc[:, 0], y=row_coords3.iloc[:, 1], color='green', alpha=0.5, label='Car')
sns.scatterplot(x=col_coords3.iloc[:, 0], y=col_coords3.iloc[:, 1], color='orange', marker='s', s=100, label='Segment')
for i, txt in enumerate(row_coords3.index):
    plt.annotate(txt, (row_coords3.iloc[i, 0], row_coords3.iloc[i, 1]), fontsize=7, alpha=0.7)
for i, txt in enumerate(col_coords3.index):
    plt.annotate(txt, (col_coords3.iloc[i, 0], col_coords3.iloc[i, 1]), fontsize=12, color='darkorange', weight='bold')
plt.title('Quantification Theory III Map (Car Name vs Segment)')
plt.legend()
plt.grid(True)
plt.savefig(f'{out_dir}/quant3_map.png', dpi=150, bbox_inches='tight')
plt.close()

# 7a. Quantification Theory I (Target: 総合評価(15点))
df_q1_s = df_clean.dropna(subset=['総合評価(15点)', 'CATEGORY', 'SEGMENT'])
df_dummy_s = pd.get_dummies(df_q1_s[['CATEGORY', 'SEGMENT']], drop_first=True)
y_q1_s = df_q1_s['総合評価(15点)']
reg_q1_s = LinearRegression().fit(df_dummy_s, y_q1_s)
coef_q1_s = pd.DataFrame({'Factor': df_dummy_s.columns, 'Coefficient': reg_q1_s.coef_}).sort_values('Coefficient')
plt.figure(figsize=(8, 8))
sns.barplot(x='Coefficient', y='Factor', data=coef_q1_s, palette='cool')
plt.title('Quantification Theory I Coefficients (Target: 総合評価)')
plt.savefig(f'{out_dir}/quant1_score.png', dpi=150, bbox_inches='tight')
plt.close()

# 7b. Quantification Theory I (Target: 車両販売価格)
df_q1_p = df_clean.dropna(subset=['お薦めグレード価格(円)', 'CATEGORY', 'SEGMENT'])
if len(df_q1_p) > 0:
    df_dummy_p = pd.get_dummies(df_q1_p[['CATEGORY', 'SEGMENT']], drop_first=True)
    y_q1_p = df_q1_p['お薦めグレード価格(円)']
    reg_q1_p = LinearRegression().fit(df_dummy_p, y_q1_p)
    coef_q1_p = pd.DataFrame({'Factor': df_dummy_p.columns, 'Coefficient': reg_q1_p.coef_}).sort_values('Coefficient')
    plt.figure(figsize=(8, 8))
    sns.barplot(x='Coefficient', y='Factor', data=coef_q1_p, palette='autumn')
    plt.title('Quantification Theory I Coefficients (Target: 車両販売価格)')
    plt.savefig(f'{out_dir}/quant1_price.png', dpi=150, bbox_inches='tight')
    plt.close()

print("Script run fully completed.")
