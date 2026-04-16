import json
import random

cars_str = """デリカミニ
eKクロスEV
サクラ
FIT
Civic Type R
ステップワゴン
セレナ
ヴォクシー
ノア
N-BOX/ N-BOXカスタム
フリード
シエンタ
ヴェルファイア
アルファード
AQUA
NOTE
NOTE AURA
VEZEL
クロストレック
COROLLA CROSS
PRIUS
レヴォーグ
ARIA
アウトランダー(PHEV)
ハリアー
NX
CROWN(クロスオーバー)
CRWN(スポーツ)
CRWN(エステート)
RX
CRWN(セダン)
MIRAI
LS
ハスラー
スペーシア
ワゴンRスマイル
タント
ムーヴキャンバス
タフト
デイズ
eKワゴン/ eKクロス
ルークス
eKスペース
N-WGN/ N-WGNカスタム
ソリオ
SWIFT
SWIFT SPORTS
YARIS
GR YARIS
クロスビー
フロンクス
ロッキー
ライズ
KICKS
YARIS CROSS
LBX
MAZDA3 FB
COROLLA
カローラツーリング
COROLLA SPORT
GR COROLLA
CIVIC HB
LEAF
インプレッサスポーツ
BRZ
GR86
ZR-V
CX-30
UX
エクリプスクロス
フォレスター
WRX S4
オデッセイ
エクストレイル
CR-V e:FCEV
CX-5
RAV4
レヴォーグレイバック
レガシィアウトバック
ソルテラ
bZ4X
CX-60
CX-80
フェアレディZ
Supra
アコード
ES
RZ
ランドクルーザー250
ランドクルーザー300
GX
LX
センチュリー
LM
ワゴンR
N-ONE
N-VAN
アルト
ミライース
トール
ルーミー
MAZDA2
CX-3
MX-30
MAZDA3 SEDAN
WR-V
デリカD:5
IS
RC
LC
ラパン
SKYLINE
エルグランド
ジムニーシエラ
ロードスター
トライトン
ランドクルーザー70
ジムニー
コペン"""

makers_dict = {
  "トヨタ": ["ヴォクシー", "ノア", "シエンタ", "ヴェルファイア", "アルファード", "AQUA", "COROLLA", "PRIUS", "ハリアー", "CROWN", "CRWN", "MIRAI", "YARIS", "ライズ", "RAV4", "bZ4X", "Supra", "ランドクルーザー", "センチュリー", "ルーミー", "GR86"],
  "ホンダ": ["FIT", "Civic", "CIVIC", "ステップワゴン", "N-BOX", "フリード", "VEZEL", "N-WGN", "ZR-V", "オデッセイ", "CR-V", "アコード", "N-ONE", "N-VAN", "WR-V"],
  "日産": ["サクラ", "セレナ", "NOTE", "ARIA", "デイズ", "ルークス", "KICKS", "LEAF", "エクストレイル", "フェアレディZ", "SKYLINE", "エルグランド"],
  "三菱": ["デリカ", "eK", "アウトランダー", "エクリプスクロス", "トライトン"],
  "スバル": ["クロストレック", "レヴォーグ", "インプレッサ", "BRZ", "フォレスター", "WRX", "レガシィ", "ソルテラ"],
  "スズキ": ["ハスラー", "スペーシア", "ワゴンR", "ソリオ", "SWIFT", "クロスビー", "フロンクス", "アルト", "ラパン", "ジムニー"],
  "ダイハツ": ["タント", "ムーヴ", "タフト", "ロッキー", "ミライース", "トール", "コペン"],
  "マツダ": ["MAZDA", "CX-", "MX-", "ロードスター"],
  "レクサス": ["NX", "RX", "LS", "LBX", "UX", "ES", "RZ", "GX", "LX", "LM", "IS", "RC", "LC"]
}

def get_maker(name):
    for m, prefixes in makers_dict.items():
        if any(p in name for p in prefixes):
            return m
    return "その他"

def get_type(name, maker):
    n = name.lower()
    if 'cx-' in n or 'クロス' in n or 'cross' in n or 'suv' in n or 'ランドクルーザー' in n or 'ハリアー' in n or 'アウトランダー' in n or 'vezel' in n or 'ジムニー' in n or 'タフト' in n or 'ハスラー' in n or 'lx' in n or 'nx' in n or 'rx' in n or 'gx' in n:
        return "SUV"
    elif 'ヴォクシー' in n or 'ノア' in n or 'セレナ' in n or 'ステップワゴン' in n or 'アルファード' in n or 'ヴェルファイア' in n or 'フリード' in n or 'シエンタ' in n or 'lm' in n or 'エルグランド' in n or 'デリカ' in n:
        return "ミニバン"
    elif 'スポーツ' in n or 'sport' in n or 'z' in n or 'brz' in n or '86' in n or 'supra' in n or 'ロードスター' in n or 'type r' in n or 'rc' in n or 'lc' in n or 'コペン' in n:
        return "スポーツカー"
    elif maker in ["スズキ", "ダイハツ"] and "ソリオ" not in n and "トール" not in n and "ロッキー" not in n and "クロスビー" not in n:
        return "軽自動車"
    elif 'eK' in name or 'サクラ' in name or 'N-BOX' in name or 'デイズ' in name or 'ルークス' in name or 'N-WGN' in name or 'N-ONE' in name or 'N-VAN' in name:
        return "軽自動車"
    elif 'クラウン' in n or 'crown' in n or 'crwn' in n or 'ls' in n or 'es' in n or 'is' in n or 'スカイライン' in n or 'アコード' in n or 'プリウス' in n or 'mirai' in n:
        return "セダン"
    return "コンパクト/ハッチバック"

data = []
for idx, car in enumerate(cars_str.strip().split('\n')):
    cname = car.strip()
    if not cname: continue
    
    maker = get_maker(cname)
    btype = get_type(cname, maker)
    
    # Generate random monthly data
    base_prod = random.randint(1000, 10000)
    monthly_data = []
    for m in range(1, 13):
        prod = int(base_prod * random.uniform(0.8, 1.2))
        sales = int(prod * random.uniform(0.85, 1.1))
        monthly_data.append({"month": m, "production": prod, "sales": sales})
        
    data.append({
        "id": idx + 1,
        "name": cname,
        "maker": maker,
        "type": btype,
        "monthlyData": monthly_data
    })

with open('/Users/koichiro_oku/Documents/Antigravity/dashboard/data.js', 'w', encoding='utf-8') as f:
    f.write("const CAR_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")

print("Generated data.js")
