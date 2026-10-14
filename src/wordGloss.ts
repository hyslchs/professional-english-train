export type GlossEntry = {term: string; zh_tw: string};
export type Gloss = {term: string; meaning: string; contextual: boolean};

// Offsets identify occurrences, so the same spelling may have different senses.
export function findWordGloss(text: string, start: number, end: number,
  entries: GlossEntry[], meanings?: Record<string, string>): Gloss | null {
  const term = text.slice(start, end);
  if (meanings?.[String(start)]) return {term, meaning: meanings[String(start)], contextual: true};
  const normalized = text.toLowerCase();
  const matches = entries.flatMap(entry => {
    const needle = entry.term.toLowerCase();
    if (!needle) return [];
    const occurrences = [];
    let position = normalized.indexOf(needle);
    while (position !== -1) {
      const finish = position + needle.length;
      if (position <= start && finish >= end &&
        !/[a-z0-9]/i.test(text[position - 1] || '') && !/[a-z0-9]/i.test(text[finish] || '')) {
        occurrences.push({term: text.slice(position, finish), meaning: entry.zh_tw, contextual: false});
      }
      position = normalized.indexOf(needle, position + 1);
    }
    return occurrences;
  });
  return matches.sort((a, b) => b.term.length - a.term.length)[0] || null;
}
