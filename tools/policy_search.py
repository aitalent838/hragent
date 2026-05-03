from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'

def search_policy_docs(query: str):
    query_words = set(query.lower().split())
    results = []
    for path in DATA_DIR.glob('*.txt'):
        text = path.read_text(encoding='utf-8')
        score = sum(1 for w in query_words if w in text.lower())
        if score > 0:
            results.append({'source': path.name, 'score': score, 'text': text})
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:3]
