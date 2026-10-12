"""Fetch every listing page; retain distinct bytes, including same-year papers."""
import hashlib, json, re, time, unicodedata
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
BASE = 'https://master.get.com.tw/exam/'
def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
def main():
    RAW.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers['User-Agent'] = 'Personal NTU LIS study archive/1.0'
    queue, visited, candidates, failures = [1], set(), [], []
    while queue:
        page = queue.pop(0)
        if page in visited: continue
        response = session.get(BASE+'List.aspx', params={'iPageNo':page,'sFilter':'圖書資訊','sSchool':'國立臺灣大學','sSearchView':'vSearch1'}, timeout=60)
        response.raise_for_status()
        visited.add(page)
        (RAW / f'listing-{page}.html').write_text(response.text, encoding='utf-8')
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.select('a[href]'):
            m = re.search(r'iPageNo=(\d+)', a['href'])
            if m and int(m[1]) not in visited: queue.append(int(m[1]))
        for row in soup.select('tr'):
            cells = row.find_all('td', recursive=False)
            if len(cells) != 5: continue
            school, subject, year = [unicodedata.normalize('NFKC', c.get_text('',strip=True)) for c in cells[1:4]]
            # Group-specific rows are preserved as candidates and deduplicated by SHA-256.
            if school not in ['國立臺灣大學-圖書資訊系碩士班','國立臺灣大學-圖書資訊系碩士班甲組','國立臺灣大學-圖書資訊系碩士班乙組']: continue
            if subject.replace(' ','') != '專業英文(J)': continue
            for a in cells[4].select('a[href]'):
                candidates.append({'year':int(year),'school':school,'source_pdf':urljoin(BASE,a['href']), 'listing_page':page})
        time.sleep(.2)
    papers, by_hash = [], {}
    for item in candidates:
        try:
            r = session.get(item['source_pdf'], timeout=60); r.raise_for_status()
            if not r.content.startswith(b'%PDF'): raise ValueError('Response is not a PDF')
            digest = hashlib.sha256(r.content).hexdigest()
            if digest in by_hash:
                by_hash[digest]['alternate_sources'].append(item); continue
            filename = f"{item['year']}-{digest[:12]}.pdf"
            (RAW / filename).write_bytes(r.content)
            paper = {**item,'sha256':digest,'file':filename,'alternate_sources':[]}
            papers.append(paper); by_hash[digest] = paper
            print(item['year'], filename)
        except Exception as e: failures.append({**item,'stage':'download','error':str(e)})
    save(RAW/'manifest.json',{'pages':sorted(visited),'candidates':candidates,'papers':papers,'failures':failures})
    print(f'{len(visited)} pages; {len(candidates)} candidates; {len(papers)} unique PDFs')
if __name__ == '__main__': main()
