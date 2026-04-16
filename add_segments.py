import json

def get_segment(name, btype):
    n = name.lower()
    if btype == '軽自動車':
        return 'Aセグメント'
    
    b_class = ['yaris', 'ヤリス', 'note', 'ノート', 'fit', 'フィット', 'swift', 'スイフト', 'mazda2', 'aquau', 'aqua', 'ライズ', 'ロッキー', 'クロスビー', 'フロンクス', 'kicks', 'ルーミー', 'トール', 'wr-v']
    if any(b in n for b in b_class):
        return 'Bセグメント'
        
    c_class = ['corolla', 'カローラ', 'civic', 'シビック', 'impreza', 'インプレッサ', 'mazda3', 'prius', 'プリウス', 'cx-30', 'cx-3', 'leaf', 'リーフ', 'ux', 'エクリプスクロス', 'クロストレック', 'vezel', 'zr-v']
    if any(c in n for c in c_class):
        return 'Cセグメント'
        
    d_class = ['accord', 'アコード', 'skyline', 'スカイライン', 'legacy', 'レガシィ', 'levorg', 'レヴォーグ', 'cx-5', 'cx-60', 'harrier', 'ハリアー', 'rav4', 'フォレスター', 'アウトランダー', 'xtrail', 'エクストレイル', 'nx', 'is']
    if any(d in n for d in d_class):
        return 'Dセグメント'
        
    e_class = ['crown', 'クラウン', 'crwn', 'ls', 'es', 'rz', 'rx', 'lx', 'gx', 'lc', 'century', 'センチュリー', 'alphard', 'アルファード', 'vellfire', 'ヴェルファイア', 'lm', 'エルグランド', 'ランドクルーザー', 'フェアレディz', 'supra', 'rc']
    if any(e in n for e in e_class):
        return 'E/Fセグメント'
        
    if btype == 'ミニバン':
        if 'シエンタ' in n or 'フリード' in n:
            return 'Bセグメント'
        if 'ノア' in n or 'ヴォクシー' in n or 'ステップワゴン' in n or 'セレナ' in n:
            return 'C/Dセグメント'
            
    if 'ロードスター' in n or '86' in n or 'brz' in n or 'コペン' in n:
        return 'スポーツセグメント'
            
    return 'その他セグメント'

with open('/Users/koichiro_oku/Documents/Antigravity/dashboard/data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for car in data:
    car['segment'] = get_segment(car['name'], car.get('type', ''))

with open('/Users/koichiro_oku/Documents/Antigravity/dashboard/data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

print("Segments added to data.json")
