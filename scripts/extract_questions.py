"""Extract text first; scan-only papers use cached OCR. Publish only reviewed SHA-bound records."""
import json, re
import pdfplumber
from fetch_exams import ROOT, RAW, save
PROCESSED = ROOT/'data/processed'
def normalize(text):
    text = re.sub(r'([A-Za-z])-\s*\n\s*([a-z])',r'\1\2',text)
    return re.sub(r'\s+',' ',text).strip()
def candidate_questions(text):
    """Conservative candidates only: heading-gated blocks, never published unreviewed."""
    articles, terms, active = [], [], None
    buffer=[]
    question=None
    def flush():
        nonlocal buffer
        if question and buffer:
            (articles if active=='translation' else terms).append({'question':question,'text':normalize('\n'.join(buffer)),'status':'needs_review'})
        buffer=[]
    for line in text.splitlines():
        lower=re.sub(r'\s+','',line.lower())
        if (('terms' in lower or 'concepts' in lower) and ('explain' in lower or 'define' in lower)):
            flush(); active='term_definition'; question=None; continue
        if (('translate' in lower and ('intochinese' in lower or 'textstochinese' in lower)) or
            re.search(r'英文.*(?:翻|译|譯).*(?:中文)',line) or re.search(r'本段落.*(?:翻|译|譯).*(?:中文)',line)):
            flush(); active='translation'; question=None
            inline_question=re.match(r'^\s*(\d+)[.．]',line)
            if inline_question and '本段落' in line: question=inline_question[1]
            continue
        if (('translate' in lower and 'intoenglish' in lower) or re.search(r'中文.*(?:翻|译|譯).*英文',line) or 'paraphrasing' in lower):
            flush(); active=None;question=None;continue
        if re.search(r'^(?:試[题題]|题[号號]|題號|科目|節次|筛次|共.*[页頁])',line.strip()):continue
        if not active:continue
        m=re.match(r'^\s*((?:[IVX]+|I1|II|[A-C])[-.]\d+|\d+(?:\.\d+)?)[.．]?\s*(.*)',line)
        if m:
            flush();question=m[1];buffer=[m[2]]
            if active=='term_definition':flush();question=None
        elif question:buffer.append(line)
    flush()
    return {'articles':articles,'term_questions':terms}
def main():
    manifest = json.loads((RAW/'manifest.json').read_text(encoding='utf-8'))
    review_path = ROOT/'data/curated/reviewed.json'
    reviewed = json.loads(review_path.read_text(encoding='utf-8')) if review_path.exists() else {}
    articles, terms, failures, drafts = [], [], list(manifest['failures']), []
    for paper in manifest['papers']:
        try:
            with pdfplumber.open(RAW/paper['file']) as doc:
                text = '\n\f\n'.join(p.extract_text() or '' for p in doc.pages)
            method = 'pdf_text'
            if len(text.strip()) < 40:
                method = 'ocr_visual_review'
                text = (RAW/paper['file']).with_suffix('.txt').read_text(encoding='utf-8')
                if not text.strip(): raise ValueError('Scanned PDF: run ocr_exams.py and review page images')
            drafts.append({**paper,'extraction_method':method,'text':text,'candidates':candidate_questions(text),'status':'needs_visual_review'})
            review = reviewed.get(paper['sha256'])
            if not review or review.get('status') != 'reviewed':
                raise ValueError('No SHA-256-bound reviewed extraction; raw candidate withheld')
            for row in review['articles']:
                if not row['zh_tw'] or len(row['english'])<50: raise ValueError('Incomplete reviewed article')
                english = normalize(row['english']).translate(str.maketrans({'’':"'",'‘':"'",'“':'"','”':'"','—':'--','…':'...'}))
                articles.append({**row,'english':english,'year':paper['year'],'id':f"ntu-lis-{paper['year']}-{paper['sha256'][:12]}-translation-{row['question']}",'source_pdf':paper['source_pdf'],'source_sha256':paper['sha256'],'extraction_method':method,'review_status':'visually_verified','translation_status':'assistant_translation_reviewed','normalization_note':'Line wrapping removed; typographic quotes/dashes normalized for keyboard entry. '+('English is an assistant reference translation of the verified Chinese source.' if row.get('question_type')=='chinese_to_english' else 'Source wording retained.')})
            for row in review['terms']:
                terms.append({**row,'year':paper['year'],'source_pdf':paper['source_pdf'],'source_sha256':paper['sha256']})
        except Exception as e: failures.append({'year':paper['year'],'source_pdf':paper['source_pdf'],'stage':'extraction_review','error':str(e)})
    save(PROCESSED/'extraction_drafts.json',drafts)
    save(PROCESSED/'failed_extractions.json',failures)
    save(PROCESSED/'exams.json',{'articles':sorted(articles,key=lambda x:(-x['year'],x['question'])),'term_questions':terms})
    from align_sentences import main as align_sentences
    align_sentences()
    print(f'{len(articles)} reviewed articles; {len(terms)} term questions; {len(failures)} failures')
if __name__ == '__main__': main()
