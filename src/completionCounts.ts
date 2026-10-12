export const COMPLETION_KEY = 'lis-article-completions';

export function loadCompletionCounts(): Record<string, number> {
  try {
    const stored: unknown = JSON.parse(localStorage.getItem(COMPLETION_KEY) || '{}');
    if (!stored || typeof stored !== 'object' || Array.isArray(stored)) return {};
    return Object.fromEntries(Object.entries(stored).filter(([, count]) =>
      typeof count === 'number' && Number.isSafeInteger(count) && count >= 0));
  } catch {
    return {};
  }
}
