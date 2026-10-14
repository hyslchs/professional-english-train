"""Build local, occurrence-specific reading notes for the reviewed article corpus.

No runtime dictionary requests or API keys. Fail on new, unannotated words rather
than silently treating an arbitrary dictionary sense as a contextual translation.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r"[A-Za-z]+(?:['’\-][A-Za-z]+)*")


def read_entries(filename):
    entries = {}
    for line in (ROOT / 'scripts' / filename).read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        names, meaning = line.split('=', 1)
        for name in names.split('/'):
            if name.lower() in entries:
                raise ValueError(f'Duplicate entry: {name}')
            entries[name.lower()] = meaning
    return entries


LEXICON = read_entries('context_glossary.txt')
PHRASES = read_entries('context_phrases.txt')

# These readings were selected against the full English sentence, not just the
# spelling. Article ID + sentence index stays independent of array ordering.
OVERRIDES = {
    ('ntu-lis-115-241e16361ac6-translation-B', 1): {'measures': '實際措施；讓館藏被利用的具體作法'},
    ('ntu-lis-115-241e16361ac6-translation-C-1', 0): {'given': '給定的；此處指計算所採用的樣本數'},
    ('ntu-lis-115-241e16361ac6-translation-C-1', 5): {'means': '表示；這個顯著水準所代表的意思', 'chance': '機率；此處指發生錯誤判斷的可能性'},
    ('ntu-lis-114-6887e39ecbae-translation-3', 4): {'while': '雖然；此句承認 AI 的優點後轉而提醒品質風險', 'significant': '重要的；此處指 AI 帶來的明顯優點'},
    ('ntu-lis-113-8bcd750de22e-translation-2.1', 0): {'use': '使用詮釋資料；記錄資源使用情形的詮釋資料類型'},
    ('ntu-lis-113-8bcd750de22e-translation-2.2', 3): {'output': '學術產出；此處主要指發表的文獻', 'range': '涵蓋；研究範圍從……到……'},
    ('ntu-lis-113-8bcd750de22e-translation-2.3', 0): {'given': '特定的；研究者要初步了解的某個主題', 'significant': '相當大的；此處指研究所占比例，非統計顯著性'},
    ('ntu-lis-112-01f45a2a4b3b-translation-1', 1): {'significant': '重大的；此處指足以影響日常生活的意外'},
    ('ntu-lis-112-01f45a2a4b3b-translation-2', 3): {'work': '有待完成的工作；此處指建立公民科學資料的可信使用環境'},
    ('ntu-lis-112-01f45a2a4b3b-translation-3', 2): {'critical': '關鍵的；此處指疫情期間數位資源更加不可或缺'},
    ('ntu-lis-111-026fb3b7c8f2-translation-2.1', 0): {'measures': '衡量指標；用來評估文獻相關程度的量度'},
    ('ntu-lis-111-026fb3b7c8f2-translation-2.1', 1): {'outputs': '檢索結果；系統找出的文獻集合'},
    ('ntu-lis-111-026fb3b7c8f2-translation-2.1', 2): {'chance': '機會；讓使用者自行選擇檢索策略'},
    ('ntu-lis-110-949e05468173-translation-II-1', 0): {'work': '作品；此處指傳播的資訊或思想內容'},
    ('ntu-lis-110-949e05468173-translation-II-3', 0): {'as': '隨著；引出研究重心轉變的過程'},
    ('ntu-lis-110-949e05468173-translation-II-3', 1): {'links': '關聯；此處指資訊行為、素養與影響之間的關係'},
    ('ntu-lis-109-3676e44c0571-translation-1', 4): {'while': '相較之下；此處對照類別項目與量化數值的關係', 'measures': '測量值；圖表中由類別標籤對應的量化資料'},
    ('ntu-lis-109-3676e44c0571-translation-2', 4): {'some': '有些人；指問卷受訪者的一部分'},
    ('ntu-lis-109-3676e44c0571-translation-3', 1): {'while': '雖然；此處是讓步語氣，不是表示時間'},
    ('ntu-lis-109-3676e44c0571-translation-3', 3): {'organization': '資訊組織；對資源進行整理與安排'},
    ('supplementary-phishing', 3): {'opening': '開啟；此處指打開電子郵件附件'},
    ('supplementary-vendor-privacy', 3): {'collection': '資料蒐集；廠商收集使用者資料的行為', 'having': '讓；使蒐集活動被當成自動進行的預設'},
    ('supplementary-open-shelves', 2): {'while': '而；連接對兩種使用者需求的不同配置'},
    ('supplementary-ai-privacy-oversight', 4): {'authority': '權限；館員修正或拒絕不合適輸出的權利'},
    ('supplementary-ai-copyright-mining', 2): {'range': '多樣的範圍；此處指訓練資料的廣度'},
    ('supplementary-ai-copyright-mining', 3): {'while': '同時；採取授權作法時也考量研究及教育需求'},
}


def annotate_sentence(article, index, sentence):
    text = sentence['english']
    tokens = list(TOKEN.finditer(text))
    meanings = {}
    for token in tokens:
        word = token.group().lower()
        if word not in LEXICON:
            raise ValueError(f"Missing gloss: {article['id']} / {index} / {word}")
        meanings[str(token.start())] = LEXICON[word]
    # Apply shorter phrases first; a longer expression provides the more specific
    # context, e.g. digital reference service instead of reference service.
    for phrase, meaning in sorted(PHRASES.items(), key=lambda entry: len(entry[0])):
        for match in re.finditer(r'(?<![A-Za-z])' + re.escape(phrase) + r'(?![A-Za-z])', text, re.I):
            for token in tokens:
                if match.start() <= token.start() and token.end() <= match.end():
                    meanings[str(token.start())] = f'{meaning}（{text[match.start():match.end()]}）'
    overrides = OVERRIDES.get((article['id'], index), {})
    for token in tokens:
        if token.group().lower() in overrides:
            meanings[str(token.start())] = overrides[token.group().lower()]
    # Avoid offering irrelevant alternate senses for grammatical words.
    for token in tokens:
        key = str(token.start())
        if meanings[key] != LEXICON[token.group().lower()]:
            continue
        word = token.group().lower()
        tail = text[token.end():].lstrip().lower()
        if word in ('a', 'an'):
            meanings[key] = '不定冠詞；引出一個尚未特定的人或事物，中文常不另譯'
        elif word == 'the':
            meanings[key] = '定冠詞；限定上下文中的特定對象，中文常不另譯'
        elif word in ('has', 'have') and re.match(r'(been|shown|grown|to)\b', tail):
            meanings[key] = '完成式助動詞；與後面的分詞一起表示已發生的狀態'
        elif word == 'have':
            meanings[key] = '具有；此處指擁有某種特徵、能力或權利'
        elif word == 'has':
            meanings[key] = '具有；此處指包含某些內容或具有某種特徵'
        elif word in ('been', 'being'):
            meanings[key] = 'be 的分詞；與其他助動詞構成完成式或被動語態'
        elif word in ('is', 'are', 'be', 'was'):
            meanings[key] = '是；若後面接過去分詞，協助表示「被……」的語態'
        elif word in ('do', 'does'):
            meanings[key] = '助動詞；此處與 not 一起表示否定'
        elif word == "don't":
            meanings[key] = '不；do not 的縮寫，在此否定後面的動作'
        elif word == 'while' and text.startswith('Phishing'):
            meanings[key] = '同時；郵件偽裝成可信來源並要求收件者操作'
        elif word == 'to':
            if re.match(r'\d', tail):
                meanings[key] = '到……；表示數值範圍的終點'
            elif re.match(r'(the|a|an|our|their|them|and|frequency|high-resolution|librarianship|patrons|building|time|one|information)\b', tail):
                meanings[key] = '對於／給……；引出適用對象或目的範圍的介系詞'
            else:
                meanings[key] = '引出後面的動作（不定詞標記），表示要做……'
        elif word == 'that':
            meanings[key] = '連接從句；引出前述事物的說明或動作的內容'
    sentence['word_meanings'] = meanings
    return len(tokens)


def annotate_articles(articles):
    return sum(annotate_sentence(article, index, sentence)
               for article in articles for index, sentence in enumerate(article.get('sentences', [])))


def main():
    count = 0
    for filename in ('exams.json', 'supplementary.json'):
        path = ROOT / 'public/data' / filename
        data = json.loads(path.read_text(encoding='utf-8'))
        count += annotate_articles(data['articles'])
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Annotated {count} word occurrences with local contextual reading notes.')


if __name__ == '__main__':
    main()
