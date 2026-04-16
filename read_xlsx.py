import pandas as pd
file_path = '/Users/koichiro_oku/Documents/Antigravity/20260323_演習.xlsx'
try:
    xl = pd.ExcelFile(file_path)
    print("Sheets:", xl.sheet_names)
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        print(f"\n--- Sheet: {sheet} ---")
        print("Shape:", df.shape)
        print("Columns:", df.columns.tolist()[:20], "..." if len(df.columns) > 20 else "")
        print("First few rows:")
        print(df.head(2))
except Exception as e:
    print(e)
