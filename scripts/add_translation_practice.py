"""Import the two Chinese-to-English passages checked against the scanned pages."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
passages = [
    (114, '2', [
        ('電子郵件是圖書館執行館務營運與服務讀者的重要資通訊工具，但同時也是資安威脅的主要來源。', 'Email is an important information and communication tool for library operations and services to patrons, but it is also a major source of information security threats.'),
        ('攻擊者可能會偽造資料庫廠商的系統更新通知、期刊出版社的電子期刊訂閱確認信，或是文獻傳遞申請等釣魚郵件。', 'Attackers may send phishing emails disguised as system update notifications from database vendors, electronic journal subscription confirmations from journal publishers, or document delivery requests.'),
        ('這些經過精心設計的社交工程攻擊，往往誘使使用者點選惡意連結，導致其在偽造的身份驗證頁面上輸入帳號與密碼。', 'These carefully crafted social engineering attacks often lure users into clicking malicious links and entering their usernames and passwords on fake authentication pages.'),
        ('一旦擁有管理者權限的帳號遭到盜用，攻擊者不僅能夠存取圖書館資訊系統的後端資料庫，更可能藉由資料庫管理權限，竊取讀者個資與電子資源採購合約等重要資訊。', "Once an account with administrator privileges has been compromised, attackers can not only access the backend database of the library's information system but may also exploit database administration privileges to steal sensitive information, such as patrons' personal data and contracts for the acquisition of electronic resources."),
    ]),
    (115, 'B', [
        ('圖書館學五律之第三律「每一書均有其讀者」指的是圖書館應使館藏充分流通。', 'The third of the Five Laws of Library Science, "Every book its reader," states that libraries should ensure that their collections are widely used.'),
        ('以下為具體做法之舉隅：1. 採用開架系統，便利讀者自由瀏覽，增加圖書與讀者接觸的機會。', 'Examples of practical measures include: 1) adopting an open-stack system that allows patrons to browse freely and increases opportunities for them to encounter books;'),
        ('2. 依主題分類排架，提供新書展示，凸顯館藏新穎性；書架張貼推薦標示以吸引讀者的注意；書架高度與架位安排以方便讀者利用為原則。', '2) arranging books on shelves by subject and displaying new books to highlight recent additions to the collection, placing recommendation signs on shelves to attract attention, and choosing shelf heights and layouts for ease of use;'),
        ('3. 參考館員應協助讀者找到所需圖書。', '3) having reference librarians help patrons find the books they need;'),
        ('4. 吸引潛在讀者成為圖書館的真正使用者。', 'and 4) attracting potential patrons and turning them into active library users.'),
        ('而第四律「節省讀者的時間」則是盡可能讓讀者的時間做最有效率的應用。', 'The fourth law, "Save the time of the reader," calls for making the most efficient use of patrons\' time.'),
        ('例如：開架閱覽可節省讀者找到所需圖書的時間；完備的主題分析目錄可助讀者將相關資料一網打盡；將利用頻繁的館藏配置在入口處並建立醒目的標示導引系統，可加速讀者及時找到適切的圖書。', 'For example, open-stack access reduces the time needed to find books; a comprehensive catalog with thorough subject analysis helps patrons locate all relevant materials; and placing frequently used materials near the entrance and providing a prominent signage and wayfinding system help patrons find suitable books promptly.'),
    ]),
]

def main():
    review_path = ROOT / 'data/curated/reviewed.json'
    sentence_path = ROOT / 'data/curated/sentence_translations.json'
    reviewed = json.loads(review_path.read_text(encoding='utf-8'))
    sentences = json.loads(sentence_path.read_text(encoding='utf-8'))
    manifest = json.loads((ROOT / 'data/raw/manifest.json').read_text(encoding='utf-8'))
    for year, question, pairs in passages:
        paper = next(p for p in manifest['papers'] if p['year'] == year)
        rows = reviewed[paper['sha256']]['articles']
        rows[:] = [r for r in rows if r['question'] != question]
        # Preserve wording while displaying long enumerations as shorter bilingual units.
        aligned_chinese = [p[0] for p in pairs]
        segments = None
        if year == 115:
            shorter_pairs = []
            for i, (zh, en) in enumerate(pairs):
                if i == 2:
                    zh_parts = zh.split('；')
                    en_parts = en.split(', ')
                    shorter_pairs.extend([
                        (zh_parts[0] + '；', en_parts[0] + ','),
                        (zh_parts[1] + '；', en_parts[1] + ','),
                        (zh_parts[2], en_parts[2]),
                    ])
                elif i == 6:
                    zh_parts = zh.split('；')
                    en_parts = en.split('; ')
                    shorter_pairs.extend((z + ('；' if j < 2 else ''), e + (';' if j < 2 else ''))
                                         for j, (z, e) in enumerate(zip(zh_parts, en_parts)))
                else:
                    shorter_pairs.append((zh, en))
            aligned_chinese = [p[0] for p in shorter_pairs]
            segments = [p[1] for p in shorter_pairs]
        rows.append({'year': year, 'question': question, 'page': 1,
                     'question_type': 'chinese_to_english',
                     'english': ' '.join(p[1] for p in pairs),
                     'zh_tw': ''.join(p[0] for p in pairs),
                     'translation_note': '英文為依原始中文試題撰寫的參考譯文，非官方答案；翻譯可有其他正確表達。',
                     'source_reviewed_on': '2026-10-12',
                     **({'reading_segments': segments} if segments else {})})
        sentences[f'{year}:{question}'] = aligned_chinese
    for path, data in [(review_path, reviewed), (sentence_path, sentences)]:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
