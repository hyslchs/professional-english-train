# 文章單字字卡與語境註解

滑鼠在英文單字上停留 700 毫秒顯示字卡。移開、捲動、縮放視窗或按 Esc 即關閉。
隱藏逐句中文時仍可使用字卡，英打字元位置及完成紀錄保持一致。

現有 33 篇文章、159 句、3,427 個英文單字出現位置都有繁體中文閱讀註解，
包含冠詞、介系詞、縮寫、所有格與帶連字號的詞。數字及標點不當作英文單字。

## 編寫方式與適用範圍

註解由助手依現有英文句子及上下文編寫。一般詞義由
`scripts/context_glossary.txt` 提供；片語、名稱及術語由
`scripts/context_phrases.txt` 提供；多義詞的具體解讀保留在
`scripts/build_context_glosses.py` 的文章 ID／句子規則中。
資料以句內字元起點存入 `sentence.word_meanings`，同一拼字在不同位置可顯示不同解讀。

片語不能逐字拆譯時，字卡會提供整組含義並標示英文詞組。
例如 `draws on` 是取用外部資料，`level the playing field` 是使競爭條件公平。
`authority` 在資訊素養文章中是來源的權威性，在人工監督文章中則是館員的權限。
冠詞及助動詞提供其句中語法作用，而不是強行對應單一中文字。

以下是實際參考的字典與專業資料，不代表全部 1,198 種拼字都已逐條查詢字典，
也不代表這些網站提供了本專案的官方中文譯文。中文解釋是依前後文自行撰寫，
未複製字典的完整條目或例句。

## 2026-10-15 查核參考

| 詞／用法 | 查核依據 | 本文採用的解讀 |
| --- | --- | --- |
| compromised | [Oxford: compromise（動詞，第 4 義）](https://www.oxfordlearnersdictionaries.com/definition/english/compromise_2) | 帳號遭入侵或安全性受破壞 |
| address／addressing | [Oxford: address（動詞，第 1 義）](https://www.oxfordlearnersdictionaries.com/definition/english/address_2) | 處理問題、回應資訊需求 |
| draws on | [Oxford: draw on/upon something](https://www.oxfordlearnersdictionaries.com/definition/english/draw-on) | 取用既有的外部文件或資料庫 |
| drawn from | [Oxford: draw（抽取／選取）](https://www.oxfordlearnersdictionaries.com/definition/english/draw_1) | 樣本由母體抽取 |
| while | [Oxford: while（連接詞）](https://www.oxfordlearnersdictionaries.com/definition/english/while_1?q=while) | 依句子分別為雖然、同時或對照 |
| in light of | [Cambridge: in the light of](https://dictionary.cambridge.org/dictionary/english/in-the-light-of) | 根據調查結果調整方案 |
| ground | [Cambridge: ground](https://dictionary.cambridge.org/dictionary/english/ground) | 讓回答以來源資料為依據 |
| authority | [Cambridge: authority](https://dictionary.cambridge.org/dictionary/english/authority) | 對來源的信賴與權威性，或被授予的權限；依文章區分 |
| recall／precision | [Stanford: Introduction to Information Retrieval, §8.3](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-unranked-retrieval-sets-1.html) | 召回率／精確率，採資訊檢索的專業定義 |

部分字典網址直接讀取失敗時使用同站搜尋結果核對；不把讀取失敗當作查核成功。
既有專業詞彙表及文章來源繼續保留於原資料中。

## 重建與檢查

`python scripts/build_context_glosses.py` 重建兩份公開文章資料的單字註解。
既有逐句對齊及延伸文章產生流程也會呼叫註解產生器。
新增未收錄的單字會停止重建並報出文章、句子和單字，補上並核對後才能繼續。
新文章仍需另行檢查完整語境，不能僅憑覆蓋率宣稱語意已核對。

`python tests/context_glosses_test.py` 檢查全文覆蓋、字元位置、片語與多義詞、
重建一致性、未知詞處理；`node tests/wordGloss.test.mjs` 檢查畫面使用的詞義查找。
