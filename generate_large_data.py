import json
import random
import re
import os

js_path = '/Users/koichiro_oku/Documents/Antigravity/dashboard/data.js'
json_path = '/Users/koichiro_oku/Documents/Antigravity/dashboard/data.json'

with open(js_path, 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'const CAR_DATA = (\[.*\]);', text, flags=re.DOTALL)
old_data = json.loads(match.group(1))

new_data = []

for car_index, car in enumerate(old_data):
    monthly_data = []
    # Seed specific randomness per car
    random.seed(car_index)
    base_prod = random.randint(1000, 10000)
    
    for year in range(2010, 2027):
        for month in range(1, 13):
            # simulate missing future data (like end of 2026)
            if year == 2026 and month > 12:
                break
                
            base_prod = max(100, int(base_prod * random.uniform(0.95, 1.05)))
            
            # seasonal dip in August (factory stop) and Jan
            seasonal_factor = 1.0
            if month in [1, 8]:
                seasonal_factor = 0.8
            # spike in March (financial year end)
            elif month == 3:
                seasonal_factor = 1.3
                
            total_prod = int(base_prod * seasonal_factor)
            dom_ratio = random.uniform(0.4, 0.8)
            dom_prod = int(total_prod * dom_ratio)
            ovs_prod = total_prod - dom_prod
            
            total_sales = int(total_prod * random.uniform(0.85, 1.2))
            dom_ratio_s = random.uniform(0.4, 0.8)
            dom_sales = int(total_sales * dom_ratio_s)
            ovs_sales = total_sales - dom_sales
            
            monthly_data.append({
                "year": year,
                "month": month,
                "production": { "total": total_prod, "domestic": dom_prod, "overseas": ovs_prod },
                "sales": { "total": total_sales, "domestic": dom_sales, "overseas": ovs_sales }
            })
            
    # sort
    monthly_data.sort(key=lambda x: (x['year'], x['month']))
    
    new_data.append({
        "id": car['id'],
        "name": car['name'],
        "maker": car['maker'],
        "type": car['type'],
        "monthlyData": monthly_data
    })

# Write to data.json
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(new_data, f, ensure_ascii=False)

# Remove data.js to clean up
if os.path.exists(js_path):
    os.remove(js_path)
    
print("Successfully generated 2010-2026 data.json")
