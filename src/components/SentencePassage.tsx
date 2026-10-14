import {useEffect, useRef, useState} from 'react';
import {createPortal} from 'react-dom';
import {findWordGloss, type GlossEntry} from '../wordGloss';

export type Sentence = {
  english: string;
  zh_tw: string;
  start: number;
  end: number;
  separator_after: string;
  word_meanings?: Record<string, string>;
};

export function SentencePassage({sentences, input, showChinese, onChange, completed, words = []}: {
  words?: GlossEntry[];
  sentences: Sentence[];
  input: string;
  showChinese: boolean;
  onChange: (value: string) => void;
  completed: boolean;
}) {
  const editor = useRef<HTMLTextAreaElement>(null);
  const passage = useRef<HTMLDivElement>(null);
  const [focused, setFocused] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [card, setCard] = useState<{term: string; meaning?: string; contextual: boolean; chinese: string; x: number; y: number; below: boolean} | null>(null);
  const dismiss = () => {
    if (timer.current !== null) clearTimeout(timer.current);
    timer.current = null;
    setCard(null);
  };
  useEffect(() => {
    const escape = (event: KeyboardEvent) => {if (event.key === 'Escape') dismiss();};
    window.addEventListener('scroll', dismiss, true);
    window.addEventListener('resize', dismiss);
    window.addEventListener('keydown', escape);
    return () => {
      if (timer.current !== null) clearTimeout(timer.current);
      window.removeEventListener('scroll', dismiss, true);
      window.removeEventListener('resize', dismiss);
      window.removeEventListener('keydown', escape);
    };
  }, []);
  const hover = (element: HTMLElement, sentence: Sentence, start: number, end: number) => {
    dismiss();
    timer.current = setTimeout(() => {
      const rect = element.getBoundingClientRect();
      const gloss = findWordGloss(sentence.english, start, end, words, sentence.word_meanings);
      setCard({term: gloss?.term || sentence.english.slice(start, end), meaning: gloss?.meaning,
        contextual: gloss?.contextual || false, chinese: sentence.zh_tw,
        x: Math.max(12, Math.min(rect.left + rect.width / 2 - 160, window.innerWidth - 332)),
        y: rect.top < 250 ? rect.bottom + 10 : rect.top - 10, below: rect.top < 250});
    }, 700);
  };
  useEffect(() => {
    if (!focused || !input.length) return;
    const cursor = passage.current?.querySelector('.cursor');
    const bounds = cursor?.getBoundingClientRect();
    if (!bounds) return;
    // Move only when the caret leaves the reading area. Instant movement avoids
    // overlapping scroll animations while characters are arriving quickly.
    const margin = Math.min(80, window.innerHeight / 4);
    const delta = bounds.bottom > window.innerHeight - margin
      ? bounds.bottom - (window.innerHeight - margin * 2)
      : bounds.top < margin ? bounds.top - margin * 2 : 0;
    if (delta) window.scrollBy({top: delta, behavior: 'instant'});
  }, [input, focused]);
  const focusEditor = () => {
    editor.current?.focus({preventScroll: true});
    editor.current?.setSelectionRange(input.length, input.length);
  };
  return <div className={`inline-typing ${focused ? 'is-focused' : ''}`}>
    <p className="typing-guide" id="typing-guide">{completed ? '文章已完成，可以重新練習。' : focused ? '正在輸入 · 綠色正確，紅色錯誤 · Backspace 可修改' : '點擊英文文章，直接開始打字'} · 滑鼠停在單字上 0.7 秒可看本句詞義</p>
    <textarea ref={editor} className="inline-input" aria-label="文章英打" aria-describedby="typing-guide"
      spellCheck={false} autoCapitalize="off" autoCorrect="off" value={input} readOnly={completed}
      onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
      onPaste={event => event.preventDefault()}
      onSelect={event => event.currentTarget.setSelectionRange(input.length, input.length)}
      onChange={event => onChange(event.target.value)} />
    <div ref={passage} className="passage sentence-passage" aria-label="逐句對照文章" onClick={focusEditor}>
    {sentences.map((sentence, index) => <div className="sentence-pair" key={sentence.start}>
      {showChinese && <p className="sentence-chinese" lang="zh-Hant" aria-label={`第 ${index + 1} 句中文`}>{sentence.zh_tw}</p>}
      <div className="sentence-english" lang="en" aria-label={`第 ${index + 1} 句英文`}>
        {Array.from((sentence.english + sentence.separator_after).matchAll(/[A-Za-z]+(?:['’\-][A-Za-z]+)*|[^A-Za-z]+/g)).map(match => {
          const token = match[0], tokenStart = match.index;
          const isWord = /^[A-Za-z]/.test(token);
          return <span key={tokenStart} className={isWord ? 'hover-word' : undefined}
            onMouseEnter={isWord ? event => hover(event.currentTarget, sentence, tokenStart, tokenStart + token.length) : undefined}
            onMouseLeave={isWord ? dismiss : undefined} aria-describedby={card && isWord && card.term === token ? 'word-gloss-card' : undefined}>
        {[...token].map((character, offset) => {
          const position = sentence.start + tokenStart + offset;
          const state = position < input.length
            ? character === input[position] ? 'correct' : 'wrong'
            : position === input.length ? 'cursor' : '';
          return <span key={position} className={state}>{character}</span>;
        })}</span>;
        })}
      </div>
    </div>)}
    </div>
    {card && createPortal(<div id="word-gloss-card" role="tooltip" className="word-gloss-card"
      style={{left: card.x, top: card.y, transform: card.below ? undefined : 'translateY(-100%)'}}>
      <strong lang="en">{card.term}</strong>
      <p>{card.meaning || '此單字尚未收錄詞義'}</p>
      <small>{card.contextual ? '本句詞義 · 依語境編寫' : card.meaning ? '已收錄詞彙譯名 · 請搭配本句理解' : '可參考本句中文'}</small>
      <div className="word-gloss-context">{card.chinese}</div>
    </div>, document.body)}
  </div>;
}
