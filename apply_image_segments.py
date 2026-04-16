import json
import logging

file_path = '/Users/koichiro_oku/Documents/Antigravity/dashboard/data.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for car in data:
    name = car['name']
    n = name.lower()
    
    btype = '不明'
    seg = '不明'

    # Kei
    kei_list = ['デリカミニ', 'ekクロスev', 'サクラ', 'ハスラー', 'スペーシア', 'ワゴンrスマイル', 'タント', 'ムーヴキャンバス', 'タフト', 'デイズ', 'ekワゴン', 'ルークス', 'ekスペース', 'n-wgn', 'n-box', 'n-one', 'ワゴンr', 'アルト', 'ミライース', 'ラパン', 'ジムニー', 'n-van', 'コペン']
    if any(k in n for k in kei_list) and not 'シエラ' in n:
        btype = '軽自動車'
        seg = 'Aセグメント(軽)'
        if 'コペン' in n:
            btype = 'スポーツ'

    # Compact
    compact_list = ['fit', 'aqua', 'note', 'swift', 'yaris', 'mazda2', 'ルーミー', 'トール', 'ソリオ', 'パッソ', 'ブーン', 'カローラスポーツ', 'mazda3 fb', 'civic hb', 'インプレッサ', 'leaf']
    if any(k in n for k in compact_list) and not 'cross' in n and not 'gr ' in n and not 'sports' in n:
        btype = 'コンパクト'
        seg = 'Bセグメント'
        if any(c in n for c in ['カローラスポーツ', 'mazda3 fb', 'civic hb', 'インプレッサ', 'leaf']):
            seg = 'Cセグメント'

    # Minivan
    minivan_list = ['シエンタ', 'フリード', 'ノア', 'ヴォクシー', 'ステップワゴン', 'セレナ', 'アルファード', 'ヴェルファイア', 'エルグランド', 'デリカd:5', 'オデッセイ', 'lm']
    if any(k in n for k in minivan_list):
        btype = 'ミニバン'
        if any(s in n for s in ['シエンタ', 'フリード']):
            seg = 'Sクラス'
        elif any(m in n for m in ['ノア', 'ヴォクシー', 'ステップワゴン', 'セレナ', 'デリカd:5']):
            seg = 'Mクラス'
        else:
            seg = 'Lクラス'

    # SUV
    suv_list = ['ライズ', 'ロッキー', 'フロンクス', 'wr-v', 'yaris cross', 'kicks', 'vezel', 'cx-3', 'lbx', 'corolla cross', 'zr-v', 'cx-30', 'ux', 'エクリプスクロス', 'mx-30', 'クロストレック', 'rav4', 'ハリアー', 'エクストレイル', 'cx-5', 'フォレスター', 'アウトランダー', 'nx', 'bz4x', 'ソルテラ', 'aria', 'crown(クロスオーバー)', 'crwn(スポーツ)', 'crwn(エステート)', 'cx-60', 'cx-80', 'rx', 'rz', 'ランドクルーザー', 'gx', 'lx', 'ジムニーシエラ', 'クロスビー']
    if any(k in n for k in suv_list):
        btype = 'SUV'
        if any(s in n for s in ['ライズ', 'ロッキー', 'フロンクス', 'wr-v', 'yaris cross', 'kicks', 'cx-3', 'lbx', 'ジムニーシエラ', 'クロスビー']):
            seg = 'Bセグメント'
        elif any(s in n for s in ['corolla cross', 'zr-v', 'cx-30', 'ux', 'エクリプスクロス', 'mx-30', 'クロストレック', 'vezel']):
            seg = 'Cセグメント'
        elif any(s in n for s in ['rav4', 'ハリアー', 'エクストレイル', 'cx-5', 'フォレスター', 'アウトランダー', 'nx', 'bz4x', 'ソルテラ', 'aria']):
            seg = 'Dセグメント'
        else:
            seg = 'E/Fセグメント'

    # Sedan
    sedan_list = ['mazda3 sedan', 'corolla', 'カローラ', 'prius', 'プリウス', 'アコード', 'skyline', 'wrx s4', 'es', 'is', 'crwn(セダン)', 'mirai', 'ls', 'センチュリー']
    if any(k in n for k in sedan_list) and not 'cross' in n and not 'sport' in n and not 'ツーリング' in n:
        btype = 'セダン'
        if any(s in n for s in ['mazda3 sedan', 'corolla', 'カローラ', 'prius', 'プリウス']):
            seg = 'Cセグメント'
        elif any(s in n for s in ['アコード', 'skyline', 'wrx s4', 'is']):
            seg = 'Dセグメント'
        else:
            seg = 'E/Fセグメント'

    # Station Wagon
    wagon_list = ['カローラツーリング', 'レヴォーグ', 'アウトバック', 'レイバック']
    if any(k in n for k in wagon_list):
        btype = 'ステーションワゴン'
        if 'カローラツーリング' in n:
            seg = 'Cセグメント'
        else:
            seg = 'Dセグメント'

    # Sports
    sports_list = ['gr yaris', 'swift sports', 'gr corolla', 'civic type r', 'brz', 'gr86', 'ロードスター', 'フェアレディz', 'supra', 'rc', 'lc', 'コペン']
    if any(k in n for k in sports_list):
        btype = 'スポーツ'
        if any(s in n for s in ['gr yaris', 'swift sports', 'ロードスター', 'コペン']):
            seg = 'Bセグメント(以下)'
        elif any(s in n for s in ['gr corolla', 'civic type r', 'brz', 'gr86']):
            seg = 'Cセグメント'
        elif 'lc' in n:
            seg = 'E/Fセグメント'
        else:
            seg = 'Dセグメント'
            
    # Others
    if 'トライトン' in n:
        btype = 'ピックアップトラック'
        seg = 'E/Fセグメント'

    # Assignment
    # Provide fallbacks if unidentified
    if btype == '不明':
        # Default logic checking existing type if any
        if car.get('type') in ['ミニバン', 'SUV', '軽自動車']:
            btype = car['type']
        else:
            btype = 'その他'
            
    if seg == '不明':
        seg = '未定義'

    car['type'] = btype
    car['segment'] = seg

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

print("Updated data.json with new Body Types and Segments successfully!")
