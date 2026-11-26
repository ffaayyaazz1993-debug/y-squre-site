"""Restamp the generated header and terminal assets across all HTML pages.

Used for site-wide skin changes where a full regen would prune published
article directories. It only touches <head> asset tags and the header block.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_lib
import gen_nav

ROOT = gen_lib.ROOT
CSS = gen_lib.asset('/assets/css/market.css')
JS = gen_lib.asset('/assets/js/market.js')
HEADER = gen_nav.header()

changed = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in ('.git', 'node_modules')]
    for fn in filenames:
        if not fn.endswith('.html'):
            continue
        path = os.path.join(dirpath, fn)
        try:
            s = open(path, encoding='utf-8').read()
        except (OSError, UnicodeDecodeError):
            continue
        orig = s

        if '</head>' in s:
            if 'market.css' not in s:
                s = s.replace('</head>',
                              f'  <link rel="stylesheet" href="{CSS}">\n</head>', 1)
            if 'market.js' not in s:
                s = s.replace('</head>',
                              f'  <script src="{JS}" defer></script>\n</head>', 1)

        pat = re.compile(
            r'<a class="skip-link".*?</a>\s*<header class="site-header">.*?</header>',
            re.S)
        if pat.search(s):
            s = pat.sub(HEADER, s, count=1)
        elif '<header class="site-header">' in s:
            s = re.sub(r'<header class="site-header">.*?</header>', HEADER, s,
                       count=1, flags=re.S)

        if s != orig:
            open(path, 'w', encoding='utf-8', newline='\n').write(s)
            changed.append(os.path.relpath(path, ROOT).replace('\\', '/'))

print(f'restamped {len(changed)} pages')
for p in changed[:20]:
    print(' ', p)
if len(changed) > 20:
    print(f'  ... and {len(changed) - 20} more')
