import re
import json
import pathlib

SNAP_DIR = pathlib.Path(r"c:\Users\USER\AppData\Roaming\Code\User\workspaceStorage\d8c59bd25c3cb795ab9b64581faaa79d\GitHub.copilot-chat\chat-session-resources\8d06d0b4-458a-41ad-9d4a-a3dbded99f5a")
OUT_FILE = pathlib.Path('assets/data/commands-git.json')

# Load existing commands (if present)
existing = {'codes': set(), 'titles': set(), 'commands': []}
if OUT_FILE.exists():
    j = json.loads(OUT_FILE.read_text(encoding='utf-8'))
    for cat in j.get('categories', []):
        for cmd in cat.get('commands', []):
            existing['codes'].add(cmd.get('code','').strip())
            existing['titles'].add(cmd.get('title','').strip())
            existing['commands'].append(cmd)
else:
    j = None

# Read all snapshot content.txt files in that resource folder
snap_files = list(SNAP_DIR.rglob('*/content.txt')) + list(SNAP_DIR.glob('*/content.txt'))
# also include top-level content.txt files
snap_files = list(SNAP_DIR.glob('**/content.txt'))
lines = []
for f in snap_files:
    try:
        txt = f.read_text(encoding='utf-8')
        lines.extend(txt.splitlines())
    except Exception:
        continue

# Fallback: if no snapshot found, try direct path
if not lines:
    fallback = SNAP_DIR / 'toolu_bdrk_01AUiBSgk5kVJYgRJKzji7cZ__vscode-1780773878728' / 'content.txt'
    if fallback.exists():
        lines = fallback.read_text(encoding='utf-8').splitlines()

# Parser: look for heading level 3 for command title, then within following 60 lines find code:, paragraph (description), 'How to use', 'When to use', 'Tip:'
commands_found = []
for i, ln in enumerate(lines):
    m = re.search(r'heading "(.+?)" \[level=3\]', ln)
    if m:
        title = m.group(1).strip()
        # look ahead
        code = ''
        description = ''
        how = ''
        when = ''
        tip = ''
        j = i+1
        limit = i + 80
        while j < len(lines) and j < limit:
            l = lines[j].strip()
            # code lines
            mc = re.search(r'^code \[ref=.*?\]:\s*(.*)$', l)
            if mc and not code:
                code = mc.group(1).strip()
            # paragraph lines (first paragraph as description)
            mp = re.search(r'^paragraph \[ref=.*?\]:\s*(.*)$', l)
            if mp and not description:
                description = mp.group(1).strip()
            # How to use label
            if re.search(r'How to use', l, flags=re.I):
                # next few paragraph lines
                k = j+1
                parts = []
                while k < len(lines) and k < j+6:
                    mpp = re.search(r'^\s*-?\s*paragraph \[ref=.*?\]:\s*(.*)$', lines[k])
                    if mpp:
                        parts.append(mpp.group(1).strip())
                    elif lines[k].strip().startswith('- text:'):
                        parts.append(lines[k].split(':',1)[1].strip())
                    k += 1
                how = '\n'.join([p for p in parts if p])
            # When to use label
            if re.search(r'When to use', l, flags=re.I):
                k = j+1
                parts = []
                while k < len(lines) and k < j+6:
                    mpp = re.search(r'^\s*-?\s*paragraph \[ref=.*?\]:\s*(.*)$', lines[k])
                    if mpp:
                        parts.append(mpp.group(1).strip())
                    elif lines[k].strip().startswith('- text:'):
                        parts.append(lines[k].split(':',1)[1].strip())
                    k += 1
                when = '\n'.join([p for p in parts if p])
            # Tip detection
            if 'Tip:' in l or '💡' in l:
                # capture the line content after Tip:
                t = l
                if 'Tip:' in l:
                    t = l.split('Tip:')[-1].strip(' "')
                else:
                    # try to capture following paragraph
                    mpp = re.search(r'^\s*-?\s*paragraph \[ref=.*?\]:\s*(.*)$', lines[j+1]) if j+1 < len(lines) else None
                    t = mpp.group(1).strip() if mpp else ''
                tip = t
            # break if next heading level2 or level3 encountered
            if re.search(r'heading "', l) and j > i+1:
                break
            j += 1
        # normalize code
        code_norm = code.replace('\n', '\n').strip()
        if code_norm and 'git' in code_norm.lower():
            cmd = {
                'id': re.sub(r'[^a-z0-9\-]+','-', title.lower()).strip('-'),
                'title': title,
                'code': code_norm,
                'description': description,
                'howToUse': how,
                'whenToUse': when
            }
            if tip:
                cmd['tip'] = tip
            commands_found.append(cmd)

# Merge into existing, avoiding duplicates by code
added = 0
for cmd in commands_found:
    if cmd['code'] in existing['codes']:
        continue
    existing['commands'].append(cmd)
    existing['codes'].add(cmd['code'])
    existing['titles'].add(cmd['title'])
    added += 1

# If we had original JSON structure, try to place commands by categories; otherwise put under cat-git-all
if j and isinstance(j, dict) and j.get('categories'):
    # naive: append all new commands to first category
    j = json.loads(OUT_FILE.read_text(encoding='utf-8'))
    if j.get('categories'):
        for c in j['categories']:
            # append any commands not already in that category
            if c.get('commands') is not None:
                existing_codes = set([x.get('code','') for x in c['commands']])
                for cmd in existing['commands']:
                    if cmd.get('code','') not in existing_codes:
                        c['commands'].append(cmd)
                        existing_codes.add(cmd.get('code',''))
        # update metadata
        j['metadata']['commandCount'] = sum(len(cat.get('commands',[])) for cat in j['categories'])
        OUT_FILE.write_text(json.dumps(j, indent=2, ensure_ascii=False), encoding='utf-8')
else:
    out = {
        'metadata': {
            'title': 'OneXportal Mobile Devs Toolkit — Complete Git Reference for Termux & Acode',
            'description': 'Git commands merged from snapshots and source.',
            'author': 'Amos Isaiah Tizhe — OneXportal',
            'commandCount': len(existing['commands']),
            'lastUpdated': '2026-06-07'
        },
        'categories': [
            {
                'id': 'cat-git-all',
                'title': 'Git Commands',
                'icon': 'fa-brands fa-git',
                'description': 'All Git-related commands merged from snapshots',
                'commands': existing['commands']
            }
        ]
    }
    OUT_FILE.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

print(f'Found {len(commands_found)} commands in snapshots, added {added} new commands, total now {OUT_FILE.read_text(encoding="utf-8").count('"title"')//1}')
