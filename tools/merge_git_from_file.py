import re
import json
from html import unescape

SRC = 'termux-ops-old.html'
DEST = 'assets/data/commands-git.json'

with open(DEST,'r',encoding='utf-8') as f:
    data = json.load(f)
    existing_codes = set(c.get('code','').strip() for c in data['categories'][0]['commands'])

with open(SRC,'r',encoding='utf-8') as f:
    html = f.read()

articles = re.split(r'<article[^>]*class="command-card"[^>]*>', html)[1:]
new_count = 0
for art in articles:
    art_content = art.split('</article>')[0]
    m_title = re.search(r'<h3>(.*?)</h3>', art_content, re.S|re.I)
    title = unescape(m_title.group(1).strip()) if m_title else None
    m_code = re.search(r'<pre><code>(.*?)</code></pre>', art_content, re.S|re.I)
    code = unescape(m_code.group(1).strip()) if m_code else ''
    if not code or code in existing_codes:
        continue
    m_desc = re.search(r'<p class="description">(.*?)</p>', art_content, re.S|re.I)
    desc = ''
    if m_desc:
        desc = unescape(re.sub(r'<br\s*/?>','\n', m_desc.group(1)).strip())
        desc = re.sub(r'<.*?>','',desc)
    m_how = re.search(r'<div class="how-to-use">\s*<span class="label">.*?</span>(.*?)</div>', art_content, re.S|re.I)
    how = unescape(re.sub(r'<.*?>','',m_how.group(1)).strip()) if m_how else ''
    m_when = re.search(r'<div class="when-to-use">\s*<span class="label">.*?</span>(.*?)</div>', art_content, re.S|re.I)
    when = unescape(re.sub(r'<.*?>','',m_when.group(1)).strip()) if m_when else ''
    m_tip = re.search(r'<div class="tip-box">\s*<p>(.*?)</p>\s*</div>', art_content, re.S|re.I)
    tip = unescape(re.sub(r'<.*?>','',m_tip.group(1)).strip()) if m_tip else ''

    cmd = {
        'id': re.sub(r'[^a-z0-9\-]+','-', (title or code).lower()).strip('-'),
        'title': title or code,
        'code': code,
        'description': desc,
        'howToUse': how,
        'whenToUse': when
    }
    if tip:
        cmd['tip'] = tip
    data['categories'][0]['commands'].append(cmd)
    existing_codes.add(code)
    new_count += 1

if new_count:
    data['metadata']['commandCount'] = len(data['categories'][0]['commands'])
    data['metadata']['lastUpdated'] = '2026-06-06'
    with open(DEST,'w',encoding='utf-8') as f:
        json.dump(data,f,indent=2,ensure_ascii=False)

print(f'Added {new_count} new commands (total now {len(data["categories"][0]["commands"])})')
