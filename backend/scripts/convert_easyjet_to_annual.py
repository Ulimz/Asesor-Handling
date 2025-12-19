#!/usr/bin/env python3
"""
Convert EasyJet monthly salaries to annual (× 14 pagas)
"""
import json
import os

def convert_to_annual():
    json_path = os.path.join(os.getcwd(), 'backend', 'data', 'structure_templates', 'easyjet.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("🔄 Converting EasyJet salaries from monthly to annual...\n")
    
    # Convert salaries in structure.groups
    for group in data['structure']['groups']:
        for category in group['categories']:
            # Base salary
            if 'base_salary_2025' in category:
                old_val = category['base_salary_2025']
                category['base_salary_2025'] = round(old_val * 14, 2)
                print(f"✅ {category['name']} - Base: {old_val}€ → {category['base_salary_2025']}€")
            
            # Ad personam
            if 'ad_personam' in category:
                old_val = category['ad_personam']
                category['ad_personam'] = round(old_val * 14, 2)
                if old_val > 0:
                    print(f"   Ad Personam: {old_val}€ → {category['ad_personam']}€")
            
            # Plus función fixed (Jefes de Área)
            if 'plus_funcion_fixed' in category:
                old_val = category['plus_funcion_fixed']
                # Plus Función se paga en 12 meses, no 14
                category['plus_funcion_fixed'] = round(old_val * 12, 2)
                print(f"   Plus Función (×12): {old_val}€ → {category['plus_funcion_fixed']}€")
            
            # Progression plus per level
            for level in category.get('levels', []):
                if 'progression_plus' in level:
                    old_val = level['progression_plus']
                    level['progression_plus'] = round(old_val * 14, 2)
                    if old_val > 0:
                        print(f"   {level['level']} - Progresión: {old_val}€ → {level['progression_plus']}€")
    
    # Save back
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print("\n✅ Conversion complete! Saved to easyjet.json")

if __name__ == "__main__":
    convert_to_annual()
