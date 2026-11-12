#!/usr/bin/env python3
"""Синхронизирует все части «Предчувствия» из репозитория litmir.

  python3 tools/sync_from_litmir.py ../litmir

Главы копируются в books/<часть>/, пути к картинкам переписываются,
PNG конвертируются в JPG, иллюстрации только для этого сайта
(tools/extras.json) вставляются заново, saga.json пересобирается.
"""
import json, os, re, shutil, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'litmir'))
PARTS = [  # (id в этом сайте, slug в litmir, короткое имя)
    ('1', 'predchuvstvie', 'Сезон 1'),
    ('2', 'predchuvstvie-2', 'Сезон 2'),
    ('2-2', 'predchuvstvie-2-2', 'Часть 2.2'),
    ('2-3', 'predchuvstvie-2-3', 'Часть 2.3'),
    ('2-4', 'predchuvstvie-2-4', 'Часть 2.4'),
]
KEEP_COVER = {'2-2', '2-4'}  # обложки, сделанные специально для этого сайта

def to_jpg(src, dst):
    im = Image.open(src)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); bg = Image.new('RGB', im.size, (20, 18, 16)); bg.paste(im, mask=im.split()[-1]); im = bg
    im.convert('RGB').save(dst, 'JPEG', quality=85, progressive=True, optimize=True)

cat = json.load(open(os.path.join(LIT, 'novels', 'catalog.json')))
cat = cat if isinstance(cat, list) else cat['novels']
by = {n['slug']: n for n in cat}
extras = json.load(open(os.path.join(ROOT, 'tools', 'extras.json')))
saga = {'title': 'Предчувствие', 'author': 'Роберт Фадер',
        'genre': 'Постапокалипсис · Приключения · Любовный роман', 'rating': '16+', 'parts': []}

for pid, slug, short in PARTS:
    n = by[slug]; src = os.path.join(LIT, 'novels', slug); dst = os.path.join(ROOT, 'books', pid)
    os.makedirs(os.path.join(dst, 'img'), exist_ok=True)
    renames = {}
    simg = os.path.join(src, 'img')
    if os.path.isdir(simg):
        for f in sorted(os.listdir(simg)):
            base, ext = os.path.splitext(f)
            out = base + '.jpg'
            if ext.lower() in ('.jpg', '.jpeg'):
                shutil.copyfile(os.path.join(simg, f), os.path.join(dst, 'img', out))
            elif ext.lower() in ('.png', '.webp'):
                to_jpg(os.path.join(simg, f), os.path.join(dst, 'img', out))
            else:
                continue
            renames[f] = out
    if n.get('cover') and pid not in KEEP_COVER:
        c = os.path.join(LIT, n['cover'])
        (shutil.copyfile if c.lower().endswith(('.jpg', '.jpeg')) else to_jpg)(c, os.path.join(dst, 'cover.jpg'))
    chapters = []
    for ch in n['chapters']:
        md = open(os.path.join(src, ch['file']), encoding='utf-8').read()
        md = md.replace(f'novels/{slug}/img/', f'books/{pid}/img/')
        for a, b in renames.items():
            md = md.replace(f'books/{pid}/img/{a}', f'books/{pid}/img/{b}')
        for ex in extras.get(f"{pid}/{ch['file']}", []):
            lines = md.split('\n')
            i = next(k for k, l in enumerate(lines) if l.startswith(ex['after']))
            lines[i + 1:i + 1] = ['', ex['md']]
            md = '\n'.join(lines)
        open(os.path.join(dst, ch['file']), 'w', encoding='utf-8').write(md)
        c = {'file': ch['file'], 'title': ch['title']}
        if ch.get('label'): c['label'] = ch['label']
        chapters.append(c)
    saga['parts'].append({'id': pid, 'title': n['title'], 'short': short, 'year': n.get('year'),
                          'description': n.get('description', ''), 'cover': f'books/{pid}/cover.jpg',
                          'chapters': chapters})
    print(pid, len(chapters), 'глав')

json.dump(saga, open(os.path.join(ROOT, 'saga.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
