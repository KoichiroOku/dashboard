import pandas as pd
file_path = '../20260323_演習.xlsx'
xl = pd.ExcelFile(file_path)
print("Sheets:", xl.sheet_names)
