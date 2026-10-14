"""Corpus coverage and contextual regressions; no dictionary/network needed."""
import copy
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('gloss_builder', ROOT / 'scripts/build_context_glosses.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
articles = []
for name in ('exams.json', 'supplementary.json'):
    articles.extend(json.loads((ROOT / 'public/data' / name).read_text(encoding='utf-8'))['articles'])

count = 0
for article in articles:
    assert ''.join(s['english'] + s['separator_after'] for s in article['sentences']) == article['english']
    for sentence in article['sentences']:
        assert article['english'][sentence['start']:sentence['end']] == sentence['english']
        tokens = list(builder.TOKEN.finditer(sentence['english']))
        assert set(sentence['word_meanings']) == {str(token.start()) for token in tokens}
        assert all(isinstance(value, str) and re.search('[\u3400-\u9fff]', value) for value in sentence['word_meanings'].values())
        rebuilt = copy.deepcopy(sentence)
        builder.annotate_sentence(article, article['sentences'].index(sentence), rebuilt)
        assert rebuilt == sentence, 'Committed glosses must match the curated source rules'
        count += len(tokens)


def meaning(article_id, sentence_index, word, occurrence=0):
    article = next(a for a in articles if a['id'] == article_id)
    sentence = article['sentences'][sentence_index]
    token = [t for t in builder.TOKEN.finditer(sentence['english']) if t.group().lower() == word][occurrence]
    return sentence['word_meanings'][str(token.start())]


assert '入侵' in meaning('supplementary-phishing', 4, 'compromised')
assert '權限' in meaning('supplementary-ai-privacy-oversight', 4, 'authority')
assert '權威性' in meaning('ntu-lis-110-949e05468173-translation-II-2', 1, 'authority')
assert '召回率' in meaning('ntu-lis-111-026fb3b7c8f2-translation-2.1', 2, 'recall')
assert '精確率' in meaning('ntu-lis-111-026fb3b7c8f2-translation-2.1', 2, 'precision')
assert '依據' in meaning('supplementary-ai-generative-rag', 2, 'ground')
assert '取用' in meaning('supplementary-ai-generative-rag', 2, 'draws')
assert '給定' in meaning('ntu-lis-115-241e16361ac6-translation-C-1', 0, 'given')
assert '特定' in meaning('ntu-lis-113-8bcd750de22e-translation-2.3', 0, 'given')
assert '鑒於' in meaning('ntu-lis-115-241e16361ac6-translation-C-1', 3, 'given')
assert '雖然' in meaning('ntu-lis-114-6887e39ecbae-translation-3', 4, 'while')
assert '同時' in meaning('supplementary-phishing', 0, 'while')
assert '公平' in meaning('ntu-lis-112-01f45a2a4b3b-translation-3', 1, 'field')
assert '參考服務櫃臺' in meaning('supplementary-open-shelves', 3, 'reference')
assert '資料蒐集' in meaning('supplementary-vendor-privacy', 3, 'collection')
assert '不定詞標記' not in meaning('ntu-lis-115-241e16361ac6-translation-C-1', 0, 'to')
assert '具有' in meaning('ntu-lis-109-3676e44c0571-translation-2', 1, 'has')
assert count == 3427 and len(articles) == 33
unknown = {'english': 'Uncuratedword.', 'zh_tw': '未收錄詞', 'start': 0, 'end': 14, 'separator_after': ''}
try:
    builder.annotate_sentence({'id': 'new-article'}, 0, unknown)
except ValueError as error:
    assert 'uncuratedword' in str(error)
else:
    raise AssertionError('Unknown words must not silently get an arbitrary gloss')
print(f'Passed: {len(articles)} articles, {count} occurrences, exact offsets, contextual senses, phrases and deterministic rebuild')
