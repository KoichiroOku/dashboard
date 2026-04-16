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
import statsmodels.api as sm
import statsmodels.formula.api as smf
import os

# Font setup for Mac
plt.rcParams['font.family'] = 'Hiragino Sans'

# Disable warnings
import warnings
warnings.filterwarnings('ignore')

file_path = '../20260323_演習.xlsx'
df = pd.read_excel(file_path, sheet_name='全車種分析_120')
df = df.dropna(subset=['メーカー', '車種名'])
df = df[df['メーカー'] != 'メーカー']

cols = df.columns.tolist()
start_idx = cols.index('市街地での扱いやすさ(0~60km/h)')
end_idx = cols.index('リセールバリュー') + 1
eval_cols = cols[start_idx:end_idx]

# Clean numeric data
for c in eval_cols:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df['総合評価(15点)'] = pd.to_numeric(df['総合評価(15点)'], errors='coerce')

df_clean = df.dropna(subset=eval_cols + ['総合評価(15点)']).copy()
X = df_clean[eval_cols].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

out_dir = 'analysis_output'
os.makedirs(out_dir, exist_ok=True)

# 1. PCA
pca = PCA(n_components=2)
principalComponents = pca.fit_transform(X_scaled)
df_clean['PC1'] = principalComponents[:, 0]
df_clean['PC2'] = principalComponents[:, 1]
plt.figure(figsize=(10, 8))
sns.scatterplot(x='PC1', y='PC2', hue='CATEGORY', data=df_clean, palette='Set2')
plt.title('PCA Positioning Map')
plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} Variance)')
plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} Variance)')
plt.savefig(f'{out_dir}/pca_map.png', dpi=150, bbox_inches='tight')
plt.close()

# 2. Factor Analysis
fa = FactorAnalyzer(n_factors=3, rotation='varimax')
fa.fit(X_scaled)
loadings = pd.DataFrame(fa.loadings_, index=eval_cols, columns=['Factor1', 'Factor2', 'Factor3'])
plt.figure(figsize=(8, 10))
sns.heatmap(loadings, cmap='coolwarm', center=0, annot=True, fmt='.2f')
plt.title('Factor Loadings Heatmap')
plt.savefig(f'{out_dir}/factor_map.png', dpi=150, bbox_inches='tight')
plt.close()

# 3. Cluster Analysis
linked = linkage(X_scaled[:50], 'ward') # Limit to 50 for readable dendrogram
plt.figure(figsize=(12, 6))
dendrogram(linked, labels=df_clean['車種名'].values[:50], orientation='top', leaf_rotation=90)
plt.title('Hierarchical Clustering Dendrogram (Sample 50)')
plt.savefig(f'{out_dir}/dendrogram.png', dpi=150, bbox_inches='tight')
plt.close()

# 4. Multiple Regression (Target: 総合評価(15点))
y = df_clean['総合評価(15点)'].values
reg = LinearRegression()
reg.fit(X_scaled, y)
coef_df = pd.DataFrame({'Feature': eval_cols, 'Coefficient': reg.coef_}).sort_values('Coefficient', ascending=False)
plt.figure(figsize=(10, 8))
sns.barplot(x='Coefficient', y='Feature', data=coef_df, palette='viridis')
plt.title('Multiple Regression Coefficients (Target: 総合評価)')
plt.savefig(f'{out_dir}/regression.png', dpi=150, bbox_inches='tight')
plt.close()

# 5. Correspondence Analysis (Using 'メーカー' and 'CATEGORY')
ca = prince.CA(n_components=2, n_iter=10)
crosstab = pd.crosstab(df_clean['メーカー'], df_clean['CATEGORY'])
ca.fit(crosstab)
ca.plot(crosstab, x_component=0, y_component=1, show_row_labels=True, show_column_labels=True)
plt.title('Correspondence Analysis Map (Maker vs Category)')
plt.savefig(f'{out_dir}/correspondence_map.png', dpi=150, bbox_inches='tight')
plt.close()

# 6. Quantification Theory III (Same as above conceptually, map categories to items)
# I will use segment cross table
ca3 = prince.CA(n_components=2, n_iter=10)
crosstab3 = pd.crosstab(df_clean['メーカー'], df_clean['SEGMENT'])
ca3.fit(crosstab3)
ca3.plot(crosstab3, x_component=0, y_component=1)
plt.title('Quantification Theory III Map (Maker vs Segment)')
plt.savefig(f'{out_dir}/quant3_map.png', dpi=150, bbox_inches='tight')
plt.close()

# 7. Quantification Theory I (Multiple regression with categorical variables)
df_quant1 = df_clean[['総合評価(15点)', 'メーカー', 'CATEGORY']].copy()
df_quant1 = pd.get_dummies(df_quant1, columns=['メーカー', 'CATEGORY'], drop_first=True)
X_q1 = df_quant1.drop('総合評価(15点)', axis=1)
y_q1 = df_quant1['総合評価(15点)']
reg_q1 = LinearRegression().fit(X_q1, y_q1)
coef_q1 = pd.DataFrame({'Category': X_q1.columns, 'Coefficient': reg_q1.coef_}).sort_values('Coefficient')
plt.figure(figsize=(8, 8))
sns.barplot(x='Coefficient', y='Category', data=coef_q1, palette='magma')
plt.title('Quantification Theory I Coefficients')
plt.savefig(f'{out_dir}/quant1.png', dpi=150, bbox_inches='tight')
plt.close()

# 8. Conjoint Analysis (Mock Implementation)
# Construct an orthogonal array mock-up for car purchase preference
profiles = pd.DataFrame({
    'Brand': ['Toyota', 'Honda', 'Nissan', 'Toyota', 'Honda', 'Nissan'],
    'Price': ['Low', 'High', 'Low', 'High', 'Low', 'High'],
    'Engine': ['Gas', 'Gas', 'EV', 'EV', 'Hybrid', 'Hybrid'],
    'Preference': [80, 50, 70, 40, 90, 60]
})
df_conj = pd.get_dummies(profiles[['Brand', 'Price', 'Engine']], drop_first=True)
df_conj['Preference'] = profiles['Preference']
res = smf.ols('Preference ~ ' + ' + '.join(df_conj.columns.drop('Preference')), data=df_conj).fit()
conj_coefs = pd.DataFrame({'Attribute': res.params.index[1:], 'Utility': res.params.values[1:]})
plt.figure(figsize=(6, 4))
sns.barplot(x='Utility', y='Attribute', data=conj_coefs, palette='Set1')
plt.title('Conjoint Analysis (Mock Profile Utility)')
plt.savefig(f'{out_dir}/conjoint.png', dpi=150, bbox_inches='tight')
plt.close()

print("Analysis complete. Images generated in analysis_output/ directory.")
