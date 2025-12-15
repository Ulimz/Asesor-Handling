import json
import os

def check():
    path = '/app/data/general_xml.json'
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    table_count = 0
    pipe_count = 0
    articles_with_tables = []

    for art in data.get('articles', []):
        content = art.get('content', '')
        if "|" in content:
            table_count += 1
            pipe_count += content.count("|")
            articles_with_tables.append(art.get('article', 'Unknown'))
            if "ANEXO" in art.get('article', '').upper():
                 print(f"Found table in {art['article']}! Length: {len(content)}")
                 print(f"Sample: {content[content.find('|'):content.find('|')+100]}...")

    print(f"Total articles with tables: {table_count}")
    print(f"Total pipe characters: {pipe_count}")
    print(f"Articles with tables: {articles_with_tables}")

if __name__ == "__main__":
    check()
