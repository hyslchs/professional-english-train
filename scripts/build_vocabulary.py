"""Merge verified terminology with actual question occurrences, never guess translations."""
import json, re, shutil
from fetch_exams import ROOT, save
def main():
    data = json.loads((ROOT/'data/processed/exams.json').read_text(encoding='utf-8'))
    glossary = json.loads((ROOT/'data/curated/glossary.json').read_text(encoding='utf-8'))
    vocabulary = []
    for entry in glossary:
        occurrences=[]
        needles=[entry['term'],*entry.get('matches',[])]
        for q in data['term_questions']:
            if q['vocabulary_key']==entry['term']:
                occurrences.append({'year':q['year'],'question':q['question'],'source_pdf':q['source_pdf'],'source_type':'term_definition','original_term':q['english']})
        for a in data['articles']:
            matched = next((m.group(0) for term in needles if (m := re.search(r'(?<!\w)'+re.escape(term)+r'(?!\w)',a['english'],re.I))), None)
            contextual = next((c for c in entry.get('context_matches', []) if c['year']==a['year'] and c['question']==a['question'] and c['text'] in a['english']), None)
            if matched or contextual:
                occurrence={'year':a['year'],'question':a['question'],'source_pdf':a['source_pdf'],'source_type':'translation','original_term':matched or contextual['text']}
                if contextual: occurrence['source_note']=contextual['note']
                occurrences.append(occurrence)
        if not occurrences: continue
        assert entry['reference_sources'] and entry['zh_tw'] and entry['definition_zh_tw']
        vocabulary.append({k:v for k,v in entry.items() if k not in ('matches','context_matches')} | {'source_years':sorted({o['year'] for o in occurrences}),'source_type':sorted({o['source_type'] for o in occurrences}),'source_question':occurrences,'source_pdf':sorted({o['source_pdf'] for o in occurrences})})
    missing = {q['vocabulary_key'] for q in data['term_questions']}-{v['term'] for v in vocabulary}
    if missing: raise ValueError(f'Unverified required terms: {missing}')
    vocabulary.sort(key=lambda v:('term_definition' not in v['source_type'],v['term'].lower()))
    save(ROOT/'data/processed/vocabulary.json',{'vocabulary':vocabulary})
    output=ROOT/'public/data';output.mkdir(parents=True,exist_ok=True)
    for name in ['exams.json','vocabulary.json','failed_extractions.json']:
        shutil.copy2(ROOT/'data/processed'/name,output/name)
    print(f'{len(vocabulary)} verified vocabulary entries; static data refreshed')
if __name__ == '__main__': main()
