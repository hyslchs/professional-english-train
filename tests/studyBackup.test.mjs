import assert from 'node:assert/strict';
import fs from 'node:fs';
import ts from 'typescript';
const source = fs.readFileSync(new URL('../src/studyBackup.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(source, {compilerOptions: {module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022}}).outputText;
const {makeBackup, parseBackup, mergeBackup, loadMarks, loadShowChinese} = await import('data:text/javascript;base64,' + Buffer.from(compiled).toString('base64'));
const current = {completions: {a: 5, b: 2}, marks: {first: 'known', second: 'learning'}, showChinese: true};
const imported = {completions: {a: 3, c: 7}, marks: {second: 'known'}, showChinese: false};
const backup = makeBackup(imported);
assert.deepEqual(parseBackup(JSON.stringify(backup)), backup);
const merged = mergeBackup(current, backup);
assert.deepEqual(merged, {completions: {a: 5, b: 2, c: 7}, marks: {first: 'known', second: 'known'}, showChinese: false});
assert.deepEqual(mergeBackup(merged, backup), merged, 'Repeated imports must not inflate counts');
for (const bad of ['not json', 'null', '[]', JSON.stringify({...backup, version: 2}), JSON.stringify({...backup, completions: {a: -1}}), JSON.stringify({...backup, completions: {a: 1.5}}), JSON.stringify({...backup, marks: {a: 'invalid'}}), JSON.stringify({...backup, showChinese: 'false'}), JSON.stringify({...backup, exportedAt: 'bad'}), JSON.stringify({...backup, marks: JSON.parse('{"__proto__":"known"}')}), JSON.stringify({...backup, completions: {a: Number.MAX_SAFE_INTEGER + 1}})]) {
  assert.throws(() => parseBackup(bad));
}
const stored = new Map([['lis-marks', '{"valid":"known","wrong":"x"}'], ['lis-show-chinese', 'false']]);
globalThis.localStorage = {getItem: key => stored.get(key) ?? null};
assert.deepEqual(loadMarks(), {valid: 'known'});
assert.equal(loadShowChinese(), false);
globalThis.localStorage = {getItem() {throw Error('Unavailable');}};
assert.deepEqual(loadMarks(), {});
assert.equal(loadShowChinese(), true);
console.log('Passed: backup round-trip, merge, repeat import, invalid files, unsafe keys and unavailable storage');
