# 讀・鍵｜臺大圖資專業英文

個人備考用的 React / TypeScript / Vite 網站。沒有帳號、後端或資料庫。

## 開始使用

```powershell
npm install
npm run dev
```

瀏覽 http://127.0.0.1:5173/ 。網站使用的三份 `public/data` JSON 已納入版本控制，下載專案即可建置；若要重新執行資料處理流程，需另外準備忽略的 `data/curated`、`data/processed`，或重新建立並核對資料。

## 已驗證資料（2026-10-08）

遍歷來源的全部 3 頁，共 44 筆科目資料，找到專業英文（J）的 12 筆下載連結，按 SHA-256 去重後得到 7 份 PDF。包含目前網站列出的甲、乙組；這些連結的 PDF 內容相同。112 年兩個下載連結也具有相同內容。程式依文件內容去重，不會用年份當唯一鍵；不同內容的同年試題會分別保留。

| 民國年 | PDF（本機檔名） | 英翻中 | 名詞解釋 |
|---|---|---:|---:|
| 109 | 109-3676e44c0571.pdf | 4 | 0 |
| 110 | 110-949e05468173.pdf | 3 | 4 |
| 111 | 111-026fb3b7c8f2.pdf | 2 | 7 |
| 112 | 112-01f45a2a4b3b.pdf | 3 | 0 |
| 113 | 113-8bcd750de22e.pdf | 3 | 4 |
| 114 | 114-6887e39ecbae.pdf | 1 | 0 |
| 115 | 115-241e16361ac6.pdf | 2 | 0 |

合計 18 篇英翻中、2 篇中翻英參考譯文（114 年第 2 題、115 年 B 題），共 20 篇英打文章、15 筆名詞解釋題、92 個去重詞彙。這是指定網站當下能取得的年份，不表示臺大歷年只有這些試題。下載來源及所有重複連結詳見 `data/raw/manifest.json`；逐份核對結果詳見 `data/processed/validation_report.json`。

## 資料流程

```powershell
python -m pip install -r requirements.txt
python scripts/fetch_exams.py
python -m pip install -r requirements-ocr.txt
python scripts/ocr_exams.py
python scripts/extract_questions.py
python scripts/build_vocabulary.py
python scripts/build_supplementary.py
python scripts/validate_data.py
```

- `fetch_exams.py`：從第一頁開始跟隨分頁，正規化括號、精確比對科目，下載 PDF，依內容雜湊去重。保留年份、原 URL、分頁及替代來源。只接受 `%PDF` 檔頭。
- `ocr_exams.py`：逐頁先嘗試 PDF 文字。沒有文字才產生頁面影像並用本機 RapidOCR 辨識。保留文字、座標與信心分數。第一次 OCR 可能需要數分鐘。
- `extract_questions.py`：文字抽取及題目標題／題號候選辨識，處理換行與斷字。OCR 不能保證完整，本次 109、113、115 年有漏行，已對照原始頁面補回；黏在一起的英文詞也已校訂。
- 正式輸出只接受 `data/curated/reviewed.json` 中與 PDF SHA-256 完全相符、已逐頁核對的內容。新 PDF 或變更內容會被隔離至 `failed_extractions.json`，原始候選仍在 `extraction_drafts.json`，不會冒充已核對資料。
- `build_vocabulary.py`：依名詞題及全文中的實際出現位置合併來源。名詞題全部收錄；文章詞彙使用人工選定且已查證的詞表。所有譯名附臺灣機構來源與查證摘述；中文解釋是簡短學習用改寫，非考試官方答案。
- `validate_data.py`：驗證 PDF 雜湊、ID 唯一性、全文清理、來源年份與 URL，以及每個名詞題皆進入詞彙庫。生成 JSON 驗證報告。

### 原始與校訂資料

`data/raw` 保留 HTML、PDF、逐頁圖片、OCR 結果及初始文字；`data/curated` 保留已核對英文、翻譯、名詞題及詞彙參考資料；`data/processed` 為可重建的 JSON；`public/data` 是網站本機使用副本。核對稿和 PDF 都在 `.gitignore`；網站使用的三份 JSON 依部署需求納入版本控制。

新資料需先檢查題型、完整段落、首尾句、題號、頁碼與 OCR 漏行，再在 `reviewed.json` 加入該 SHA-256 的核對紀錄。請勿把未核對稿標成 reviewed。本次一次性匯入程式留在 `data/curated/import_review.py`，它只適用已人工核對的初始七份試題，不能用來自動核可新題。

英打文本移除外層引文括號及題目配分，保留文內語句、引號、標點與原題文法；印刷用彎引號改為鍵盤可輸入的直引號，破折號及省略號也正規化。原始掃描頁仍可對照。

## 功能與指標

- 英打：選年、選文章、隨機、翻譯開關、逐字正誤標示、Backspace／游標編輯、進度、耗時及完成統計。貼上會被阻止。
- 文章包含英翻中及中翻英，共 20 篇、94 組對照。中翻英保留已核對的中文試題，以助手撰寫的英文參考譯文作為英打目標，非官方答案。115 年長列舉依項目與分句拆成較短的中英文對照，整篇共 11 段，保留原文與標點。選單及文章標頭標明題型；中文位於對應英文上方。「顯示中文／隱藏中文」可隨時切換，且會記住瀏覽器偏好，不影響英打進度。
- 逐句譯文保留在 `data/curated/sentence_translations.json`。`extract_questions.py` 會自動呼叫 `align_sentences.py`，比對中英文句數並保留英文原文位置及句間空白，驗證所有英文句子拼接後與原文完全相同。
- WPM = 正確字元數 ÷ 5 ÷ 經過分鐘數（含空白標點）。Accuracy = 目前文字中正確字元比例，修正後更新；不是歷史按鍵錯誤率。完成要求全文完全相符，因此完成時 Accuracy 為 100%。
- 單字卡：點擊／Space 翻面、上一張／下一張、Fisher–Yates 隨機排序、名詞解釋題重要標記、來源年份、譯名查證連結、「認識／不熟」。熟悉程度以 localStorage 儲存在目前瀏覽器。
- 總文章表：包含英翻中、中翻英及延伸文章，共33篇。搜尋標題與中英文全文，按題型、年份與完成狀態篩選；展開可閱讀完整分段對照及來源，點擊「開始英打」直接練習該篇。
- 每篇完成次數：全文完全正確時加1，同一次完成只計一次，重新練習完成後再次累加。以文章ID為鍵儲存在此瀏覽器的`lis-article-completions`，總表與英打共用，重新整理保留。從功能啟用後開始累計；既有練習未留下紀錄，無法補算。清除網站資料或更換瀏覽器不會保留此紀錄。若瀏覽器無法儲存，畫面會顯示提示。
- 中文翻譯是閱讀輔助，不是官方答案。115 年 C-1 原題對顯著水準的說法較簡化，另附翻譯說明。

### 中翻英延伸練習（2026-10-12）

另加入8篇依NIST、ALA/RUSA、IFLA/UNESCO官方文章或指南改寫的短篇，共730字、40組中英對照，與20篇考古題合計28篇。每篇86–99字、5小段，聚焦114年的資安／個資與115年的圖書館實務服務。年份選單可選「中翻英延伸」集中練習，不附虛構考試年份。每篇附官方來源、採用範圍、對應題目、詞彙與句型提示，並明確標示改寫而非來源原文、官方譯文或歷屆考題。部分來源為歷史指南或封存的基礎介紹，僅採服務原則與穩定概念。

`scripts/build_supplementary.py`保留八篇原創改寫及來源查核紀錄，可重建`data/processed/supplementary.json`及`public/data/supplementary.json`，驗證短篇長度、中英文重組、字元位置及詞彙實際出現。重建後執行`npm run build`更新正式預覽。來源清單與五天練習安排見`docs/supplementary-sources.md`。

## 驗證

本次已實跑 crawler、逐頁核對全部 7 份 PDF、產生並驗證 JSON，以及執行 TypeScript／正式建置。網站測試細節見 `VALIDATION.md`。

```powershell
npm run build
npm run preview
```

## 本機使用範圍

開發與預覽伺服器綁定 127.0.0.1。網站可透過 GitHub Pages 部署；`dist` 含完整練習文字，仍不直接納入版本控制。部署技術設定不包含考古題、文章及各來源的公開重發布授權判斷。

文章英打：點擊英文文章直接輸入，正確／錯誤字元與目前游標即時顯示在原文上；Backspace 修改。沒有另外顯示的輸入框。中文仍逐句放在英文上方，可自由開關。

總詞彙表：可搜尋英文／中文／解釋，篩選已認識或尚未認識，逐詞切換狀態。與單字卡共用瀏覽器學習紀錄；未標記與不熟都歸為尚未認識。


## GitHub Pages 部署

線上網站：https://hyslchs.github.io/professional-english-train/

網站透過 `.github/workflows/deploy.yml` 在推送至 `main` 後自動建置並發布。
GitHub 儲存庫 Settings → Pages 的 Source 使用 GitHub Actions。
正式建置的路徑由 Pages 設定提供；本機開發仍使用 `/`。

網站需要的三份已核對資料 `public/data/exams.json`、`vocabulary.json`、`supplementary.json` 已納入版本控制與部署。
原始 PDF、OCR、中間資料及失敗抽取報告不納入部署來源。
公開的練習資料並不代表原始來源授予再利用授權；來源資訊保留於資料與網站中。
學習紀錄儲存在目前瀏覽器，不提供帳號或跨裝置同步。


### 學習紀錄備份

各功能頁上方的「學習紀錄備份 · 匯入／匯出」可匯出 JSON，包含文章完成次數、單字熟悉度與中文顯示偏好。下載後可帶到其他裝置匯入。
匯入會先驗證格式並顯示摘要，按「確認匯入」才儲存。同篇文章保留較高完成次數，不相加；檔案中的單字狀態與中文偏好會套用，其他紀錄保留。重複匯入不會增加次數。
檔案不包含文章內容或未完成的英打，僅在裝置內處理。匯入失敗不套用畫面狀態；儲存寫入失敗時會嘗試恢復原紀錄。
驗證：`node tests/studyBackup.test.mjs`、`npm run build`。


2026-10-14 AI主題擴充：新增延伸9–13共5篇，涵蓋生成式AI與RAG、AI素養與幻覺、隱私與人工監督、偏誤與數位落差、著作權與文字資料探勘。延伸共13篇1136字、65組對照，全題庫33篇。新篇每篇80–83字、5段；來源與內容保留於scripts/ai_practice.py，build_supplementary.py可重建。既有文章ID保留，完成次數依原ID續存。
