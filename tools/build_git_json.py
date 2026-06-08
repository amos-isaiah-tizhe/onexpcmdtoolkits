import re
import json
import pathlib
from html import unescape

SRC_FILE = pathlib.Path('git-termux.html')
OUT_FILE = pathlib.Path('assets/data/commands-git.json')

CATEGORY_ICON_DEFAULT = 'fa-brands fa-git'


def clean_text(html_text: str) -> str:
    if not html_text:
        return ''
    text = html_text
    text = text.replace('\r', '')
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
    text = re.sub(r'<.*?>', '', text, flags=re.S)
    text = unescape(text)
    text = re.sub(r'\n\s+', '\n', text)
    text = re.sub(r'\s+\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = re.sub(r'-{2,}', '-', slug)
    return slug.strip('-')


def extract_articles(html_section: str) -> list[dict]:
    articles = re.findall(r'(<article[^>]*class="command-card"[^>]*>.*?</article>)', html_section, flags=re.S | re.I)
    commands = []
    seen = set()

    for art in articles:
        code_match = re.search(r'<pre>\s*<code>(.*?)</code>\s*</pre>', art, flags=re.S | re.I)
        code = clean_text(code_match.group(1)) if code_match else ''
        if not code:
            continue
        title_match = re.search(r'<h3>(.*?)</h3>', art, flags=re.S | re.I)
        title = clean_text(title_match.group(1)) if title_match else code
        if title in seen:
            title = f'{title} {len(seen) + 1}'
        seen.add(title)

        description_match = re.search(r'<p[^>]*class="description"[^>]*>(.*?)</p>', art, flags=re.S | re.I)
        description = clean_text(description_match.group(1)) if description_match else ''

        how_match = re.search(r'<div[^>]*class="how-to-use"[^>]*>(.*?)</div>', art, flags=re.S | re.I)
        how = clean_text(how_match.group(1)) if how_match else ''

        when_match = re.search(r'<div[^>]*class="when-to-use"[^>]*>(.*?)</div>', art, flags=re.S | re.I)
        when = clean_text(when_match.group(1)) if when_match else ''

        tip_match = re.search(r'<div[^>]*class="tip-box"[^>]*>(.*?)</div>', art, flags=re.S | re.I)
        tip = clean_text(tip_match.group(1)) if tip_match else ''

        command = {
            'id': slugify(title),
            'title': title,
            'code': code,
            'description': description,
            'howToUse': how,
            'whenToUse': when,
        }
        if tip:
            command['tip'] = tip
        commands.append(command)

    return commands


def parse_section(section_html: str) -> dict:
    id_match = re.search(r'id="([^"]+)"', section_html)
    section_id = id_match.group(1) if id_match else slugify('section')
    icon_match = re.search(r'<h2>\s*<i[^>]*class="([^"]+)"[^>]*>.*?</i>\s*(.*?)</h2>', section_html, flags=re.S | re.I)
    if icon_match:
        icon = icon_match.group(1).strip()
        title = clean_text(icon_match.group(2))
    else:
        title_match = re.search(r'<h2>(.*?)</h2>', section_html, flags=re.S | re.I)
        title = clean_text(title_match.group(1)) if title_match else section_id
        icon = CATEGORY_ICON_DEFAULT
    desc_match = re.search(r'<p[^>]*class="cat-desc"[^>]*>(.*?)</p>', section_html, flags=re.S | re.I)
    description = clean_text(desc_match.group(1)) if desc_match else ''
    commands = extract_articles(section_html)
    return {
        'id': section_id,
        'title': title,
        'icon': icon,
        'description': description,
        'commands': commands,
    }


if not SRC_FILE.exists():
    raise FileNotFoundError(f'{SRC_FILE} not found')

html_text = SRC_FILE.read_text(encoding='utf-8')
main_split = html_text.split('<main id="mainContent">', 1)
if len(main_split) != 2:
    raise ValueError('No main placeholder found in git-termux.html')
header_html, remainder = main_split
footer_split = remainder.split('<footer class="footer">', 1)
if len(footer_split) != 2:
    raise ValueError('No footer found in git-termux.html')
placeholder_and_content, footer_html = footer_split
footer_html = '<footer class="footer">' + footer_html
# Remove any leftover inline script after the footer
footer_html = re.sub(r'<script>[\s\S]*?</script>\s*$', '', footer_html, flags=re.I)

section_content = placeholder_and_content
# Remove the placeholder block itself from parsing
section_content = section_content.replace('<main id="mainContent">\n      <!-- Commands will be dynamically rendered here from JSON -->\n    </main>', '')
section_content = section_content.strip()

# Split the content into sections; preserve any leading content before the first section as a setup section.
parts = re.split(r'(?=<section\b[^>]*class="category-section"[^>]*>)', section_content, flags=re.I | re.S)
leading_block = parts[0].strip()
section_blocks = parts[1:]

categories = []

if leading_block:
    leading_commands = extract_articles(leading_block)
    if leading_commands:
        categories.append({
            'id': 'cat-setup',
            'title': 'Setup & Config',
            'icon': 'fa-solid fa-gear',
            'description': 'Common setup and Git configuration commands for Termux and Acode.',
            'commands': leading_commands,
        })

for block in section_blocks:
    section = parse_section(block)
    if section['commands']:
        categories.append(section)

# Write JSON data
metadata = {
    'title': 'OneXportal Mobile Devs Toolkit — Complete Git Reference for Termux & Acode',
    'description': 'Git commands extracted from HTML source.',
    'author': 'Amos Isaiah Tizhe — OneXportal',
    'commandCount': sum(len(cat['commands']) for cat in categories),
    'lastUpdated': '2026-06-07',
}

output = {
    'metadata': metadata,
    'categories': categories,
}

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUT_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Wrote {metadata["commandCount"]} git commands into {OUT_FILE}')

# Rewrite HTML to keep only the placeholder in main
new_html = header_html + '<main id="mainContent">\n      <!-- Commands will be dynamically rendered here from JSON -->\n    </main>\n' + footer_html
SRC_FILE.write_text(new_html, encoding='utf-8')
print('Rewrote git-termux.html to remove old hardcoded command markup')
