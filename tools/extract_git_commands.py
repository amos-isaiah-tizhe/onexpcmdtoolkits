import re
import json
from html import unescape

IN_FILE = 'git-termux.html'
OUT_FILE = 'assets/data/commands-git.json'

with open(IN_FILE, 'r', encoding='utf-8') as f:
    html = f.read()

# Split articles
articles = re.split(r'<article[^>]*class="command-card"[^>]*>', html)
# first chunk is header
articles = articles[1:]

commands = []
cat_map = {}

for i, art in enumerate(articles):
    # find end of article
    art_content = art.split('</article>')[0]
    # Title
    m_title = re.search(r'<h3>(.*?)</h3>', art_content, re.S|re.I)
    title = unescape(m_title.group(1).strip()) if m_title else f'Command {i+1}'
    # Code block
    m_code = re.search(r'<pre><code>(.*?)</code></pre>', art_content, re.S|re.I)
    code = unescape(m_code.group(1).strip()) if m_code else ''
    # Description
    m_desc = re.search(r'<p class="description">(.*?)</p>', art_content, re.S|re.I)
    desc = ''
    if m_desc:
        desc = unescape(re.sub(r'<br\s*/?>', '\n', m_desc.group(1)).strip())
        desc = re.sub(r'<.*?>', '', desc)
    # how-to-use
    m_how = re.search(r'<div class="how-to-use">\s*<span class="label">.*?</span>(.*?)</div>', art_content, re.S|re.I)
    how = ''
    if m_how:
        how = unescape(re.sub(r'<.*?>', '', m_how.group(1)).strip())
        how = re.sub(r'\n\s+', '\n', how)
    # when-to-use
    m_when = re.search(r'<div class="when-to-use">\s*<span class="label">.*?</span>(.*?)</div>', art_content, re.S|re.I)
    when = ''
    if m_when:
        when = unescape(re.sub(r'<.*?>', '', m_when.group(1)).strip())
        when = re.sub(r'\n\s+', '\n', when)
    # tip
    m_tip = re.search(r'<div class="tip-box">\s*<p>(.*?)</p>\s*</div>', art_content, re.S|re.I)
    tip = ''
    if m_tip:
        tip = unescape(re.sub(r'<.*?>', '', m_tip.group(1)).strip())
    # danger badge (simple detect)
    isDanger = 'danger-badge' in art_content

    cmd = {
        'id': re.sub(r'[^a-z0-9\-]+', '-', title.lower()).strip('-'),
        'title': title,
        'code': code,
        'description': desc,
        'howToUse': how,
        'whenToUse': when,
    }
    if tip:
        cmd['tip'] = tip
    if isDanger:
        cmd['isDanger'] = True

    commands.append(cmd)

# Build final JSON structure (preserve existing metadata if present)
meta = {
    'title': 'OneXportal Mobile Devs Toolkit — Complete Git Reference for Termux & Acode',
    'description': '158 Git commands explained for beginners using Termux and Acode on Android.',
    'author': 'Amos Isaiah Tizhe — OneXportal',
    'commandCount': len(commands),
    'lastUpdated': '2026-06-06'
}

# For simplicity put all commands under one "Quick Reference" category if categories not explicit
data = {
    'metadata': meta,
    'categories': [
        {
            'id': 'cat-quickref',
            'title': 'Quick Reference',
            'icon': 'fa-solid fa-star',
            'description': 'Automatically extracted commands from HTML.',
            'commands': commands
        }
    ]
}

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f'Wrote {len(commands)} commands to {OUT_FILE}')
