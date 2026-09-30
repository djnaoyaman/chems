import os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def write(V):
    for wid, (ja, en) in V.items():
        for lang, body in (('ja', ja), ('en', en)):
            p = os.path.join(ROOT, 'texts', lang, f'{wid}.md')
            open(p, 'w', encoding='utf-8').write('rev: 1\n\n## view\n' + body.strip() + '\n')
    print('wrote', len(V), 'views')
