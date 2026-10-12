import {useState} from 'react';
import type {Word} from '../main';

export function VocabularyList({words}: {words: Word[]}) {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [marks, setMarks] = useState<Record<string, string>>(() => {
    try { return JSON.parse(localStorage.getItem('lis-marks') || '{}') || {}; }
    catch { return {}; }
  });
  const known = words.filter(word => marks[word.term] === 'known').length;
  const query = search.trim().toLocaleLowerCase();
  const visible = words.filter(word =>
    `${word.term} ${word.zh_tw} ${word.definition_zh_tw}`.toLocaleLowerCase().includes(query)
    && (filter === 'all' || (marks[word.term] === 'known' ? 'known' : 'learning') === filter));
  function toggle(term: string) {
    const next = {...marks, [term]: marks[term] === 'known' ? 'learning' : 'known'};
    setMarks(next);
    localStorage.setItem('lis-marks', JSON.stringify(next));
  }
  return <section className="panel vocabulary-list">
    <h2>總詞彙表</h2>
    <p className="vocabulary-summary" role="status">共 {words.length} 個 · 已認識 {known} 個 · 尚未認識 {words.length - known} 個</p>
    <div className="vocabulary-controls">
      <input aria-label="搜尋詞彙" placeholder="搜尋英文、中文或解釋…" value={search} onChange={event => setSearch(event.target.value)}/>
      <select aria-label="篩選熟悉程度" value={filter} onChange={event => setFilter(event.target.value)}>
        <option value="all">全部詞彙</option><option value="known">已認識</option><option value="learning">尚未認識</option>
      </select>
    </div>
    <p className="hint">顯示 {visible.length} 個。點擊狀態按鈕即可切換，紀錄與單字卡共用，儲存在此瀏覽器。</p>
    <div className="vocabulary-table-wrap"><table className="vocabulary-table">
      <thead><tr><th scope="col">詞彙與解釋</th><th scope="col">來源年份與題型</th><th scope="col">學習狀態</th></tr></thead>
      <tbody>{visible.map(word => <tr key={word.term}>
        <td><strong lang="en">{word.term}</strong><div className="word-chinese">{word.zh_tw}</div><p>{word.definition_zh_tw}</p>{word.source_type.includes('term_definition') && <span className="important-term">★ 名詞解釋題重點</span>}</td>
        <td>{word.source_years.map(year => <div key={year} className="word-origin">{year} 年（{[...new Set(word.source_question.filter(source => source.year === year).map(source => source.source_type === 'term_definition' ? '名詞解釋題' : '英翻中題'))].join('、')}）</div>)}</td>
        <td><button aria-label={`${word.term}：${marks[word.term] === 'known' ? '已認識' : '尚未認識'}`} aria-pressed={marks[word.term] === 'known'} className={marks[word.term] === 'known' ? 'known' : 'unknown'} onClick={() => toggle(word.term)}>{marks[word.term] === 'known' ? '✓ 已認識' : '尚未認識'}</button></td>
      </tr>)}</tbody>
    </table></div>
    {!visible.length && <p className="hint">沒有符合條件的詞彙，試試其他搜尋或篩選。</p>}
  </section>;
}
