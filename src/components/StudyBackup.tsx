import {useRef, useState} from 'react';
import {makeBackup, parseBackup, type Backup, type StudyData} from '../studyBackup';

export function StudyBackup({data, onImport}: {data: StudyData; onImport: (backup: Backup) => void}) {
  const input = useRef<HTMLInputElement>(null);
  const [pending, setPending] = useState<Backup | null>(null);
  const [message, setMessage] = useState('');
  function download() {
    const backup = makeBackup(data);
    const url = URL.createObjectURL(new Blob([JSON.stringify(backup, null, 2)], {type: 'application/json'}));
    const link = document.createElement('a');
    link.href = url;
    link.download = `讀鍵-學習紀錄-${backup.exportedAt.slice(0, 10)}.json`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    setMessage('已匯出學習紀錄，請保留下載的檔案。');
  }
  async function read(file?: File) {
    setPending(null); setMessage('');
    if (!file) return;
    try {
      if (file.size > 1024 * 1024) throw Error('檔案過大，請選擇小於 1 MB 的學習紀錄檔。');
      setPending(parseBackup(await file.text()));
    } catch (error) { setMessage(error instanceof Error ? error.message : '無法讀取檔案。'); }
  }
  function apply() {
    if (!pending) return;
    try { onImport(pending); setPending(null); setMessage('已匯入並儲存學習紀錄。'); }
    catch { setMessage('瀏覽器無法儲存紀錄，匯入未完成。請確認網站儲存空間可用後再試。'); }
  }
  return <details className="backup-panel">
    <summary>學習紀錄備份 · 匯入／匯出</summary>
    <p>備份文章完成次數、單字熟悉度與中文顯示偏好。換裝置時，匯入下載的檔案即可接續學習。</p>
    <div className="backup-actions"><button onClick={download}>匯出學習紀錄</button><button onClick={() => input.current?.click()}>選擇紀錄檔匯入</button></div>
    <input ref={input} type="file" accept=".json,application/json" aria-label="學習紀錄檔案" hidden onChange={event => {void read(event.target.files?.[0]); event.target.value = '';}}/>
    {pending && <div className="backup-preview">
      <p>備份時間：{new Date(pending.exportedAt).toLocaleString('zh-TW')}<br/>包含 {Object.keys(pending.completions).length} 篇文章紀錄、{Object.keys(pending.marks).length} 個單字狀態。</p>
      <p>匯入會合併紀錄：同篇文章保留較高完成次數；檔案中的單字狀態與中文偏好會套用，其他紀錄保留。重複匯入不會累加次數。</p>
      <div className="backup-actions"><button className="known" onClick={apply}>確認匯入</button><button onClick={() => {setPending(null); setMessage('已取消匯入。');}}>取消</button></div>
    </div>}
    {message && <p role="status" className="backup-message">{message}</p>}
    <p className="hint">檔案只包含學習紀錄，不包含文章內容或未完成的英打。匯入檔案在此裝置處理，不會上傳。</p>
  </details>;
}
