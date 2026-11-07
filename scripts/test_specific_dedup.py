import json
import re

COMMON_STOPWORDS = {
    'отключение', 'аварийное', 'энергоснабжения', 'водоснабжения', 'бригада', 
    'выехала', 'информация', 'проведение', 'период', 'новороссийск', 'район', 
    'районе', 'улице', 'работает', 'продолжаются', 'восстановительные', 
    'электросети', 'кубани', 'юзэс', 'сообщает', 'ноября', 'года', 'часов',
    'плановые', 'авария', 'жителей', 'просим', 'соблюдать', 'время'
}

def extract_signature_tokens(title, text):
    # Strip emojis and punctuation
    raw = title + " " + text[:100]
    cleaned = re.sub(r'[^\w\sа-яёА-ЯЁ0-9]', ' ', raw.lower())
    tokens = {w for w in cleaned.split() if len(w) > 2 and w not in COMMON_STOPWORDS}
    return tokens

def are_duplicates(item1, item2):
    tokens1 = extract_signature_tokens(item1['title'], item1.get('text', ''))
    tokens2 = extract_signature_tokens(item2['title'], item2.get('text', ''))
    
    if not tokens1 or not tokens2:
        return False
        
    common = tokens1 & tokens2
    # If 2 or more specific location/object words match
    if len(common) >= 2:
        return True
    # Or if 1 very distinctive word matches (e.g. горпищенко, озереевка, семигорский)
    if len(common) >= 1 and (len(common) / min(len(tokens1), len(tokens2)) >= 0.5):
        return True
        
    return False

with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

news = data['news']
unique_news = []
duplicates_removed = []

for item in news:
    is_dup = False
    for existing in unique_news:
        if are_duplicates(item, existing):
            is_dup = True
            duplicates_removed.append((item, existing))
            break
    if not is_dup:
        unique_news.append(item)

print(f"Total: {len(news)}, Kept: {len(unique_news)}, Removed: {len(duplicates_removed)}")
for dup, orig in duplicates_removed:
    print(f"\n[DUPLICATE REMOVED]:")
    print(f"  DROP: [{dup.get('source_name')}] {ascii(dup.get('title')[:60])}")
    print(f"  KEEP: [{orig.get('source_name')}] {ascii(orig.get('title')[:60])}")

print("\n--- FINAL UNIQUE FEED ---")
for i, n in enumerate(unique_news, 1):
    print(f"{i}. [{n.get('source_name')}] {ascii(n.get('title')[:60])}")
