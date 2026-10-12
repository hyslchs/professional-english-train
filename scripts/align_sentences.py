"""Apply curated per-sentence translations; never zip independently split paragraphs."""
import json, re
from fetch_exams import ROOT, save

def align(english, translations, segments=None):
    # Split only at sentence punctuation followed by an uppercase word, not decimals/i.e.
    boundaries=[m.start() for m in re.finditer(r'(?<=[.!?])(?:[\"\x27])?\s+(?=[A-Z])',english)]
    starts=[0]
    ends=[]
    for boundary in boundaries:
        pos=boundary
        if english[pos] in '\"\x27': pos+=1
        ends.append(pos)
        while pos<len(english) and english[pos].isspace():pos+=1
        starts.append(pos)
    ends.append(len(english))
    if segments is not None:
        if ' '.join(segments) != english:
            raise ValueError('Curated reading segments must preserve the complete English text')
        starts, ends = [], []
        offset = 0
        for segment in segments:
            starts.append(offset)
            ends.append(offset + len(segment))
            offset += len(segment) + 1
    if len(starts)!=len(translations):
        raise ValueError(f'Sentence count mismatch: {len(starts)} English / {len(translations)} Chinese')
    pairs=[]
    for i,(start,end,zh) in enumerate(zip(starts,ends,translations)):
        if not zh.strip():raise ValueError('Empty sentence translation')
        next_start=starts[i+1] if i+1<len(starts) else len(english)
        pairs.append({'english':english[start:end],'zh_tw':zh,'start':start,'end':end,'separator_after':english[end:next_start]})
    assert ''.join(p['english']+p['separator_after'] for p in pairs)==english
    return pairs

def main():
    path=ROOT/'data/processed/exams.json'
    exams=json.loads(path.read_text(encoding='utf-8'))
    translations=json.loads((ROOT/'data/curated/sentence_translations.json').read_text(encoding='utf-8'))
    for article in exams['articles']:
        key=f"{article['year']}:{article['question']}"
        article.setdefault('question_type','english_to_chinese')
        try:article['sentences']=align(article['english'],translations[key],article.get('reading_segments'))
        except Exception as e:raise ValueError(f'{key}: {e}') from e
    save(path,exams)
    print(f"Aligned {sum(len(a['sentences']) for a in exams['articles'])} sentences in {len(exams['articles'])} articles")
if __name__=='__main__':main()
