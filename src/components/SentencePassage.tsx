import {useEffect, useRef, useState} from 'react';

export type Sentence = {
  english: string;
  zh_tw: string;
  start: number;
  end: number;
  separator_after: string;
};

export function SentencePassage({sentences, input, showChinese, onChange, completed}: {
  sentences: Sentence[];
  input: string;
  showChinese: boolean;
  onChange: (value: string) => void;
  completed: boolean;
}) {
  const editor = useRef<HTMLTextAreaElement>(null);
  const passage = useRef<HTMLDivElement>(null);
  const [focused, setFocused] = useState(false);
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
    <p className="typing-guide" id="typing-guide">{completed ? '文章已完成，可以重新練習。' : focused ? '正在輸入 · 綠色正確，紅色錯誤 · Backspace 可修改' : '點擊英文文章，直接開始打字'}</p>
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
        {[...(sentence.english + sentence.separator_after)].map((character, offset) => {
          const position = sentence.start + offset;
          const state = position < input.length
            ? character === input[position] ? 'correct' : 'wrong'
            : position === input.length ? 'cursor' : '';
          return <span key={position} className={state}>{character}</span>;
        })}
      </div>
    </div>)}
    </div>
  </div>;
}
