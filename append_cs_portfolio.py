import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

plt.rcParams['font.family'] = 'Hiragino Sans'
out_dir = 'analysis_output'

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
df['総合評価(15点)'] = pd.to_numeric(df['総合評価(15点)'], errors='coerce')
df_clean = df.dropna(subset=eval_cols + ['総合評価(15点)']).copy()

# CS Portfolio (30 Items)
# Calculation: Importance (Correlation with Target) vs Achievement (Mean)
importance = []
achievement = []
for c in eval_cols:
    corr = df_clean[c].corr(df_clean['総合評価(15点)'])
    mean_val = df_clean[c].mean()
    importance.append(corr)
    achievement.append(mean_val)

imp_arr = np.array(importance)
ach_arr = np.array(achievement)

# Calculate 偏差値 (T-score)
imp_t = (imp_arr - np.nanmean(imp_arr)) / np.nanstd(imp_arr) * 10 + 50
ach_t = (ach_arr - np.nanmean(ach_arr)) / np.nanstd(ach_arr) * 10 + 50

plt.figure(figsize=(14, 12))
plt.scatter(imp_t, ach_t, color='teal', s=100, alpha=0.7)
for i, feature in enumerate(eval_cols):
    plt.annotate(feature, (imp_t[i], ach_t[i]), fontsize=10, alpha=0.9)

plt.axhline(50, color='grey', ls='--')
plt.axvline(50, color='grey', ls='--')
plt.title('CSポートフォリオ分析（30評価項目）: 偏差値 (0-100)', fontsize=16)
plt.xlabel('重要度 偏差値 (総合評価との相関)', fontsize=12)
plt.ylabel('達成度 偏差値 (平均スコア)', fontsize=12)

# Quadrant labels
plt.text(70, 70, '重点維持領域\n(高重要・高達成)', color='darkgreen', fontsize=12, ha='center', va='center', alpha=0.5, weight='bold')
plt.text(70, 30, '最優先改善領域\n(高重要・低達成)', color='darkred', fontsize=12, ha='center', va='center', alpha=0.5, weight='bold')
plt.text(30, 70, '要観察・維持領域\n(低重要・高達成)', color='darkblue', fontsize=12, ha='center', va='center', alpha=0.5, weight='bold')
plt.text(30, 30, '優先度低領域\n(低重要・低達成)', color='gray', fontsize=12, ha='center', va='center', alpha=0.5, weight='bold')

plt.xlim(10, 90)
plt.ylim(10, 90)
plt.grid(True, alpha=0.3)
plt.savefig(f'{out_dir}/cs_portfolio_items.png', dpi=150, bbox_inches='tight')
plt.close()


# CS Portfolio (120 Cars)
# X: 総合評価 (Overall Evaluation), Y: コストパフォーマンス (Cost Performance)
car_score = df_clean['総合評価(15点)'].values
car_cp = df_clean['コストパフォーマンス'].values

score_t = (car_score - np.nanmean(car_score)) / np.nanstd(car_score) * 10 + 50
cp_t = (car_cp - np.nanmean(car_cp)) / np.nanstd(car_cp) * 10 + 50

plt.figure(figsize=(14, 12))
sns.scatterplot(x=score_t, y=cp_t, hue='CATEGORY', data=df_clean, palette='Set1', s=80, alpha=0.8)
for i, txt in enumerate(df_clean['車種名']):
    plt.annotate(txt, (score_t[i], cp_t[i]), fontsize=8, alpha=0.8)

plt.axhline(50, color='grey', ls='--')
plt.axvline(50, color='grey', ls='--')
plt.title('車種CSポートフォリオ: 総合評価 vs コスパ（偏差値）', fontsize=16)
plt.xlabel('総合評価 偏差値', fontsize=12)
plt.ylabel('コストパフォーマンス 偏差値', fontsize=12)

# Quadrant labels
plt.text(70, 70, 'スターバリュー領域\n(高評価・高コスパ)', color='darkgreen', fontsize=12, ha='center', va='center', alpha=0.5, weight='bold')
plt.text(70, 30, 'プレミアム領域\n(高評価・低コスパ)', color='darkorange', fontsize=12, ha='center', va='center', alpha=0.5, weight='bold')
plt.text(30, 70, 'エコ・エントリー領域\n(低評価・高コスパ)', color='darkblue', fontsize=12, ha='center', va='center', alpha=0.5, weight='bold')
plt.text(30, 30, 'ニッチ・再考領域\n(低評価・低コスパ)', color='gray', fontsize=12, ha='center', va='center', alpha=0.5, weight='bold')

plt.xlim(10, 90)
plt.ylim(10, 90)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha=0.3)
plt.savefig(f'{out_dir}/cs_portfolio_cars.png', dpi=150, bbox_inches='tight')
plt.close()

print("CS Portfolio plots generated successfully.")
