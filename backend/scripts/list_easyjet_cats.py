import json

with open('backend/data/structure_templates/easyjet.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("EasyJet Categories:")
for group in data['structure']['groups']:
    print(f"\nGroup: {group['name']}")
    for cat in group['categories']:
        print(f"  - {cat['name']}")
        if 'levels' in cat:
            for level in cat['levels']:
                print(f"      * {level['level']}")
