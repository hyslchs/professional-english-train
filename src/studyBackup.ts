export const MARKS_KEY = 'lis-marks';
export const CHINESE_KEY = 'lis-show-chinese';
export type Marks = Record<string, 'known' | 'learning'>;
export type StudyData = {completions: Record<string, number>; marks: Marks; showChinese: boolean};
export type Backup = StudyData & {app: 'lis-english-study'; version: 1; exportedAt: string};

function record(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}
function safeKey(key: string) {
  return key.length > 0 && key.length <= 300 && !['__proto__', 'constructor', 'prototype'].includes(key);
}
export function loadMarks(): Marks {
  try {
    const value: unknown = JSON.parse(localStorage.getItem(MARKS_KEY) || '{}');
    if (!record(value)) return {};
    return Object.fromEntries(Object.entries(value).filter(([key, mark]) => safeKey(key) && (mark === 'known' || mark === 'learning'))) as Marks;
  } catch { return {}; }
}
export function loadShowChinese() {
  try { return localStorage.getItem(CHINESE_KEY) !== 'false'; } catch { return true; }
}
export function makeBackup(data: StudyData): Backup {
  return {app: 'lis-english-study', version: 1, exportedAt: new Date().toISOString(), ...data};
}
export function parseBackup(text: string): Backup {
  let value: unknown;
  try { value = JSON.parse(text); } catch { throw Error('檔案不是有效的 JSON，請選擇本站匯出的紀錄檔。'); }
  if (!record(value) || value.app !== 'lis-english-study' || value.version !== 1 ||
      typeof value.exportedAt !== 'string' || !Number.isFinite(Date.parse(value.exportedAt)) ||
      !record(value.completions) || !record(value.marks) || typeof value.showChinese !== 'boolean') {
    throw Error('這不是支援的學習紀錄檔，請選擇本站匯出的紀錄檔。');
  }
  for (const [key, count] of Object.entries(value.completions)) {
    if (!safeKey(key) || typeof count !== 'number' || !Number.isSafeInteger(count) || count < 0)
      throw Error('檔案含有無效的文章完成次數，未匯入任何紀錄。');
  }
  for (const [key, mark] of Object.entries(value.marks)) {
    if (!safeKey(key) || (mark !== 'known' && mark !== 'learning'))
      throw Error('檔案含有無效的單字狀態，未匯入任何紀錄。');
  }
  return {app: 'lis-english-study', version: 1, exportedAt: value.exportedAt,
    completions: {...value.completions} as Record<string, number>, marks: {...value.marks} as Marks, showChinese: value.showChinese};
}
export function mergeBackup(current: StudyData, imported: StudyData): StudyData {
  const completions = {...current.completions};
  for (const [id, count] of Object.entries(imported.completions)) completions[id] = Math.max(completions[id] || 0, count);
  return {completions, marks: {...current.marks, ...imported.marks}, showChinese: imported.showChinese};
}
