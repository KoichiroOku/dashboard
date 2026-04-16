import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import prince
import os
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.family'] = 'Hiragino Sans'

file_path = '../20260323_演習.xlsx'
df = pd.read_excel(file_path, sheet_name='全車種分析_120')
df = df.dropna(subset=['メーカー', '車種名'])
df = df[df['メーカー'] != 'メーカー']

out_dir = 'analysis_output'

# Correspondence Analysis (Maker vs Category)
ca = prince.CA(n_components=2)
crosstab = pd.crosstab(df['メーカー'], df['CATEGORY'])
ca.fit(crosstab)
row_coords = ca.row_coordinates(crosstab)
col_coords = ca.column_coordinates(crosstab)

plt.figure(figsize=(10, 8))
sns.scatterplot(x=row_coords.iloc[:, 0], y=row_coords.iloc[:, 1], color='blue', label='Maker (Rows)')
sns.scatterplot(x=col_coords.iloc[:, 0], y=col_coords.iloc[:, 1], color='red', marker='x', label='Category (Cols)')
for i, txt in enumerate(row_coords.index):
    plt.annotate(txt, (row_coords.iloc[i, 0], row_coords.iloc[i, 1]))
for i, txt in enumerate(col_coords.index):
    plt.annotate(txt, (col_coords.iloc[i, 0], col_coords.iloc[i, 1]))
plt.title('Correspondence Analysis Map (Maker vs Category)')
plt.grid(True)
plt.savefig(f'{out_dir}/correspondence_map.png', dpi=150, bbox_inches='tight')
plt.close()

# Quantification Theory III (Maker vs Segment)
ca3 = prince.CA(n_components=2)
crosstab3 = pd.crosstab(df['メーカー'], df['SEGMENT'])
ca3.fit(crosstab3)
row_coords3 = ca3.row_coordinates(crosstab3)
col_coords3 = ca3.column_coordinates(crosstab3)

plt.figure(figsize=(10, 8))
sns.scatterplot(x=row_coords3.iloc[:, 0], y=row_coords3.iloc[:, 1], color='green', label='Maker')
sns.scatterplot(x=col_coords3.iloc[:, 0], y=col_coords3.iloc[:, 1], color='orange', marker='s', label='Segment')
for i, txt in enumerate(row_coords3.index):
    plt.annotate(txt, (row_coords3.iloc[i, 0], row_coords3.iloc[i, 1]))
for i, txt in enumerate(col_coords3.index):
    plt.annotate(txt, (col_coords3.iloc[i, 0], col_coords3.iloc[i, 1]))
plt.title('Quantification Theory III Map (Maker vs Segment)')
plt.grid(True)
plt.savefig(f'{out_dir}/quant3_map.png', dpi=150, bbox_inches='tight')
plt.close()
