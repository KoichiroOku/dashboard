import pandas as pd
file_path = '../20260323_演習.xlsx'
xl = pd.ExcelFile(file_path)
for sheet in xl.sheet_names:
    df = xl.parse(sheet)
    for col in df.columns:
        if '円' in str(col) or '価格' in str(col) or '万' in str(col):
            print(f"Sheet: {sheet}, Col: {col}")
