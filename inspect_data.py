import json

with open('data.js', 'r') as f:
    js_content = f.read()

# Strip "const INITIAL_DATA = " and trailing ";"
json_str = js_content.replace('const INITIAL_DATA = ', '').strip()
if json_str.endswith(';'):
    json_str = json_str[:-1]

data = json.loads(json_str)

# Inspect what months exist for 2026
found_2026 = {}
for car in data:
    for monthly in car.get('monthlyData', []):
        year = monthly.get('year')
        month = monthly.get('month')
        if year == 2026:
            key = f"{year}-{month:02d}"
            # Check if there's production or sales > 0 to be sure it's not just placeholder 0s
            prod = monthly.get('production', {}).get('domestic', 0)
            sales = monthly.get('sales', {}).get('domestic', 0)
            
            if key not in found_2026:
                found_2026[key] = {'count': 0, 'total_prod': 0, 'total_sales': 0}
                
            found_2026[key]['count'] += 1
            found_2026[key]['total_prod'] += prod
            found_2026[key]['total_sales'] += sales

print("Found data for 2026:")
for k in sorted(found_2026.keys()):
    print(f"{k}: {found_2026[k]}")
    
