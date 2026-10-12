import json, hashlib
from fetch_exams import ROOT, RAW
def main():
    manifest=json.loads((RAW/'manifest.json').read_text(encoding='utf-8'))
    exams=json.loads((ROOT/'data/processed/exams.json').read_text(encoding='utf-8'))
    vocab=json.loads((ROOT/'data/processed/vocabulary.json').read_text(encoding='utf-8'))['vocabulary']
    hashes={p['sha256']:p for p in manifest['papers']}
    assert len(hashes)==len(manifest['papers'])
    for digest,p in hashes.items(): assert hashlib.sha256((RAW/p['file']).read_bytes()).hexdigest()==digest
    assert len({a['id'] for a in exams['articles']})==len(exams['articles'])
    for a in exams['articles']:
        assert a['question_type'] in ('english_to_chinese','chinese_to_english')
        assert a['sentences'] and all(s['zh_tw'] for s in a['sentences'])
        assert ''.join(s['english']+s['separator_after'] for s in a['sentences'])==a['english']
        for s in a['sentences']:
            assert a['english'][s['start']:s['end']]==s['english']
        assert a['source_sha256'] in hashes and a['source_pdf']==hashes[a['source_sha256']]['source_pdf']
        assert a['year']==hashes[a['source_sha256']]['year']
        assert a['review_status']=='visually_verified' and a['zh_tw'] and a['english']
        assert '\n' not in a['english'] and not any(s in a['english'] for s in ['試題','節次','科目'])
    for q in exams['term_questions']: assert any(v['term']==q['vocabulary_key'] and 'term_definition' in v['source_type'] for v in vocab)
    assert len({v['term'].casefold() for v in vocab})==len(vocab)
    for v in vocab:
        assert v['source_years'] and v['source_question'] and v['source_pdf'] and v['reference_sources']
        assert all(s['url'].startswith('https://') and s['evidence'] for s in v['reference_sources'])
        for o in v['source_question']:
            if o['source_type']=='translation':
                assert any(a['year']==o['year'] and a['question']==o['question'] and a['source_pdf']==o['source_pdf'] and o['original_term'].casefold() in a['english'].casefold() for a in exams['articles'])
    report=[]
    for p in sorted(hashes.values(),key=lambda p:p['year']):
        report.append({'year':p['year'],'file':p['file'],'source_pdf':p['source_pdf'],'articles':len([a for a in exams['articles'] if a['source_sha256']==p['sha256']]),'term_questions':len([q for q in exams['term_questions'] if q['source_sha256']==p['sha256']])})
    from fetch_exams import save
    save(ROOT/'data/processed/validation_report.json',{'papers':report,'articles':len(exams['articles']),'vocabulary':len(vocab),'status':'passed'})
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
