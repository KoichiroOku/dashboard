import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'Hiragino Sans'

file_path = '../20260323_演習.xlsx'
df = pd.read_excel(file_path, sheet_name='全車種分析_120')
df = df.dropna(subset=['メーカー', '車種名'])
df = df[df['メーカー'] != 'メーカー']

cols = df.columns.tolist()
start_idx = cols.index('市街地での扱いやすさ(0~60km/h)')
end_idx = cols.index('リセールバリュー') + 1
eval_cols = cols[start_idx:end_idx]

for c in eval_cols:
    df[c] = pd.to_numeric(df[c], errors='coerce')

df_clean = df.dropna(subset=eval_cols).copy()
X = df_clean[eval_cols].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

linked = linkage(X_scaled, 'ward')

# Determine figure size based on number of cars so text is readable
fig_height = len(df_clean) * 0.15 # 120 * 0.15 = 18 inches
plt.figure(figsize=(10, fig_height))

# Horizontal dendrogram
dendrogram(linked, labels=df_clean['車種名'].values, orientation='left', leaf_font_size=8)
plt.title('全車種 階層型クラスター分析 (デンドログラム / トーナメント表)')
plt.xlabel('Distance (Ward)')
plt.grid(True, axis='x', alpha=0.3)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['bottom'].set_color('#888888')
plt.gca().spines['left'].set_color('#888888')

plt.tight_layout()
plt.savefig('analysis_dendrogram.svg', format='svg', bbox_inches='tight')
plt.close()
print("Saved analysis_dendrogram.svg")
