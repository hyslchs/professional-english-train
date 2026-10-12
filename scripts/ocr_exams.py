"""OCR only pages with no extractable text; keep page images and OCR evidence."""
import json
from pathlib import Path
import fitz
from rapidocr_onnxruntime import RapidOCR
from fetch_exams import RAW, save
def main():
    engine = RapidOCR()
    manifest = json.loads((RAW/'manifest.json').read_text(encoding='utf-8'))
    for paper in manifest['papers']:
        doc = fitz.open(RAW/paper['file']); pages = []
        for i,page in enumerate(doc):
            text = page.get_text().strip()
            if len(text) < 40:
                image = RAW/f"{Path(paper['file']).stem}-page-{i+1}.png"
                page.get_pixmap(matrix=fitz.Matrix(2,2)).save(image)
                result,_ = engine(str(image))
                save(image.with_suffix('.ocr.json'),result or [])
                text = '\n'.join(x[1] for x in (result or []))
            pages.append(text)
        (RAW/Path(paper['file']).with_suffix('.txt')).write_text('\n\f\n'.join(pages),encoding='utf-8')
        print(paper['year'],sum(map(len,pages)))
if __name__ == '__main__': main()
