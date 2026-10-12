import {useState} from 'react';
import type {Article} from '../main';

export function articleLabel(article: Article) {
  return article.question_type === 'supplementary'
    ? `延伸 ${article.question} · ${article.title}`
    : `${article.year} 年 · 第 ${article.question} 題`;
}

export function articleType(article: Article) {
  return article.question_type === 'supplementary' ? '中翻英延伸'
    : article.question_type === 'chinese_to_english' ? '中翻英' : '英翻中';
}

export function ArticleList({articles, counts, onPractice}: {
  articles: Article[]; counts: Record<string, number>; onPractice: (id: string) => void;
}) {
  const [search, setSearch] = useState('');
  const [type, setType] = useState('all');
  const [year, setYear] = useState('all');
  const [status, setStatus] = useState('all');
  const query = search.trim().toLocaleLowerCase();
  const visible = articles.filter(article =>
    `${articleLabel(article)} ${article.english} ${article.zh_tw}`.toLocaleLowerCase().includes(query)
    && (type === 'all' || article.question_type === type)
    && (year === 'all' || String(article.year) === year)
    && (status === 'all' || (counts[article.id] ? 'completed' : 'uncompleted') === status));
  const completed = articles.filter(article => counts[article.id] > 0).length;
  const total = articles.reduce((sum, article) => sum + (counts[article.id] || 0), 0);
  return <section className="panel article-list">
    <h2>總文章表</h2>
    <p className="vocabulary-summary" role="status">共 {articles.length} 篇 · 已完成 {completed} 篇 · 累計完成 {total} 次</p>
    <div className="article-controls">
      <input aria-label="搜尋文章" placeholder="搜尋標題、英文或中文全文…" value={search} onChange={event => setSearch(event.target.value)}/>
      <select aria-label="篩選文章題型" value={type} onChange={event => setType(event.target.value)}>
        <option value="all">全部題型</option><option value="english_to_chinese">英翻中</option><option value="chinese_to_english">中翻英</option><option value="supplementary">中翻英延伸</option>
      </select>
      <select aria-label="篩選文章年份" value={year} onChange={event => setYear(event.target.value)}>
        <option value="all">全部年份與延伸</option>
        {[...new Set(articles.filter(article => article.year !== null).map(article => article.year!))].map(value => <option key={value} value={value}>{value} 年</option>)}
        <option value="null">延伸文章</option>
      </select>
      <select aria-label="篩選文章完成狀態" value={status} onChange={event => setStatus(event.target.value)}>
        <option value="all">全部完成狀態</option><option value="uncompleted">尚未完成</option><option value="completed">已完成</option>
      </select>
    </div>
    <p className="hint">顯示 {visible.length} 篇。展開可閱讀完整中英對照。全文英打正確完成才計一次；次數從此功能啟用後開始，儲存在此瀏覽器。</p>
    <div className="article-table-wrap"><table className="article-table">
      <thead><tr><th scope="col">文章與完整中英對照</th><th scope="col">完成次數／練習</th></tr></thead>
      <tbody>{visible.map(article => <tr key={article.id}>
        <td><strong>{articleLabel(article)}</strong><span className="article-type">{articleType(article)}</span>
          <p className="article-preview" lang="en">{article.english.slice(0, 100)}{article.english.length > 100 ? '…' : ''}</p>
          <details><summary>完整中英對照 · {articleLabel(article)}</summary>
            <div className="article-fulltext">{article.sentences.map(sentence => <div className="sentence-pair" key={sentence.start}>
              <p className="sentence-chinese" lang="zh-Hant">{sentence.zh_tw}</p>
              <p className="article-english" lang="en">{sentence.english + sentence.separator_after}</p>
            </div>)}</div>
            {article.translation_note && <p className="hint">{article.translation_note}</p>}
            <a href={article.source_url || article.source_pdf} target="_blank" rel="noreferrer">{article.source_organization || '原始試題'} ↗</a>
          </details>
        </td>
        <td className="article-practice"><div className="article-count">{counts[article.id] || 0}<small> 次</small></div>
          <button aria-label={`開始練習：${articleLabel(article)}`} onClick={() => onPractice(article.id)}>開始英打 →</button>
        </td>
      </tr>)}</tbody>
    </table></div>
    {!visible.length && <p className="hint">沒有符合條件的文章，試試其他搜尋或篩選。</p>}
  </section>;
}
