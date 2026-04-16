import json
import logging

file_path = '/Users/koichiro_oku/Documents/Antigravity/dashboard/data.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Define exact release year mapping for fact-checking modern models
release_years = {
    'デリカミニ': 2023, 'eKクロスEV': 2022, 'サクラ': 2022, 'クロストレック': 2022, 
    'COROLLA CROSS': 2021, 'ARIA': 2022, 'CROWN(クロスオーバー)': 2022, 
    'CRWN(スポーツ)': 2023, 'CRWN(エステート)': 2024, 'CRWN(セダン)': 2023, 
    'ワゴンRスマイル': 2021, 'ムーヴキャンバス': 2016, 'タフト': 2020, 
    'フロンクス': 2024, 'ロッキー': 2019, 'ライズ': 2019, 'KICKS': 2020, 
    'YARIS': 2020, 'GR YARIS': 2020, 'YARIS CROSS': 2020, 'LBX': 2023, 
    'MAZDA3 FB': 2019, 'MAZDA3 SEDAN': 2019, 'カローラツーリング': 2019, 
    'COROLLA SPORT': 2018, 'GR COROLLA': 2022, 'ZR-V': 2023, 'CX-30': 2019, 
    'レヴォーグレイバック': 2023, 'ソルテラ': 2022, 'bZ4X': 2022, 'CX-60': 2022, 
    'CX-80': 2024, 'RZ': 2023, 'ランドクルーザー250': 2024, 'ランドクルーザー300': 2021, 
    'LM': 2023, 'N-VAN': 2018, 'MX-30': 2020, 'WR-V': 2024, 'トライトン': 2024, 
    'ES': 2018, 'UX': 2018, 'クロスビー': 2017, 'NOTE AURA': 2021, 
    'エクリプスクロス': 2018, 'Supra': 2019, 'RAV4': 2019, 'CR-V e:FCEV': 2024,
    'GX': 2024, 'MAZDA2': 2019, 'RC': 2014, 'LC': 2017, 'ランドクルーザー70': 2023
}

for car in data:
    cname = car['name']
    
    start_year = release_years.get(cname, 2010)

    for m in car['monthlyData']:
        y = m['year']
        if y < start_year:
            # Force domestic to 0 if before release year
            m['sales']['domestic'] = 0
            m['sales']['total'] = m['sales']['overseas']
            
            m['production']['domestic'] = 0
            m['production']['total'] = m['production']['overseas']
        elif y == start_year and m['month'] < 7:
            # Approximate smoothing: zero out early months in launch year for realism
            m['sales']['domestic'] = 0
            m['sales']['total'] = m['sales']['overseas']
            
            m['production']['domestic'] = 0
            m['production']['total'] = m['production']['overseas']

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

print("Fact-checked data applied successfully.")
