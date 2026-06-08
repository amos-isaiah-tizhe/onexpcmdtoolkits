import re
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
SNAP_DIR = Path(r"c:\Users\USER\AppData\Roaming\Code\User\workspaceStorage\d8c59bd25c3cb795ab9b64581faaa79d\GitHub.copilot-chat\chat-session-resources\8d06d0b4-458a-41ad-9d4a-a3dbded99f5a")
OUT_FILE = ROOT / 'assets' / 'data' / 'commands-git.json'

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", '-', s)
    s = re.sub(r"-+", '-', s).strip('-')
    return s or 'cmd'

def extract_from_file(p: Path):
    entries = []
    text = p.read_text(encoding='utf-8', errors='ignore').splitlines()
    i = 0
    while i < len(text):
        line = text[i].strip()
        m = re.search(r'heading\s+"(.+?)"\s+\[level=3\]', line)
        if m:
            title = m.group(1).strip()
            code = ''
            desc = ''
            # scan ahead for code and paragraph
            j = i+1
            paragraph_lines = []
            while j < len(text):
                l = text[j].strip()
                if re.search(r'heading\s+".+?"\s+\[level=3\]', l):
                    break
                cm = re.search(r'code\s+\[ref=[^\]]+\]:\s*(.*)', l)
                if cm and not code:
                    code = cm.group(1).strip()
                    # strip surrounding quotes
                    if (code.startswith('"') and code.endswith('"')) or (code.startswith("'") and code.endswith("'")):
                        code = code[1:-1]
                pm = re.search(r'paragraph\s+\[ref=[^\]]+\]:\s*(.*)', l)
                if pm:
                    val = pm.group(1).strip()
                    if val:
                        paragraph_lines.append(val)
                    # collect following '- text:' lines
                    k = j+1
                    while k < len(text) and text[k].strip().startswith('- text:'):
                        paragraph_lines.append(text[k].strip()[7:].strip())
                        k += 1
                j += 1
            if paragraph_lines:
                desc = ' '.join(paragraph_lines)
            entries.append({'title': title, 'command': code, 'description': desc})
            i = j
        else:
            i += 1
    return entries

def main():
    files = list(SNAP_DIR.rglob('content.txt'))
    if not files:
        print('No snapshot files found under', SNAP_DIR)
        return

    found = []
    for f in files:
        found.extend(extract_from_file(f))

    # load existing
    if OUT_FILE.exists():
        bak = OUT_FILE.with_suffix('.json.bak')
        OUT_FILE.replace(bak)
        existing = {'metadata': {}, 'categories': []}
        try:
            existing = json.loads(bak.read_text(encoding='utf-8'))
        except Exception:
            existing = {'metadata': {'title': 'Recovered Git Commands', 'description': '', 'author': '', 'commandCount': 0}, 'categories': [{'id': 'cat-git-all','title': 'Git Commands','commands': []}]}
    else:
        existing = {'metadata': {'title': 'Recovered Git Commands', 'description': '', 'author': '', 'commandCount': 0}, 'categories': [{'id': 'cat-git-all','title': 'Git Commands','commands': []}]}

    cmds = existing.get('categories', [])[0].get('commands', []) if existing.get('categories') else []
    before = len(cmds)
    seen = set((c.get('title','').strip(), c.get('command','').strip()) for c in cmds)
    for e in found:
        key = (e['title'].strip(), e['command'].strip())
        if key in seen:
            continue
        if not e['command']:
            # skip entries missing code
            continue
        cmds.append({'id': slugify(e['title']), 'title': e['title'], 'command': e['command'], 'description': e['description'], 'tags': ['git','termux']})
        seen.add(key)

    after = len(cmds)
    existing['categories'][0]['commands'] = cmds
    existing['metadata']['commandCount'] = after
    existing['metadata']['lastUpdated'] = datetime.utcnow().strftime('%Y-%m-%d')

    OUT_FILE.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Found {len(found)} commands in snapshots, added {after-before} new commands, total now {after}')

if __name__ == '__main__':
    main()
