import yaml, os

with open('ontology.yaml') as f:
    data = yaml.safe_load(f)

classes = data['classes']
props = data['properties']

os.makedirs('ontology', exist_ok=True)

# relations by domain
rel_by_domain = {}
for name, p in props.items():
    doms = p['domain'] if isinstance(p['domain'], list) else [p['domain']]
    for d in doms:
        rel_by_domain.setdefault(d, []).append((name, p['range']))

# attributes by domain
attrs_by_domain = {}
if 'attributes' in data:
    for name, a in data['attributes'].items():
        doms = a['domain'] if isinstance(a['domain'], list) else [a['domain']]
        for d in doms:
            attrs_by_domain.setdefault(d, []).append((name, a.get('values')))

for cname, c in classes.items():
    parent = c['parent']
    defn = c['definition']
    rels = rel_by_domain.get(cname, [])
    attrs = attrs_by_domain.get(cname, [])
    lines = []
    lines.append('---')
    lines.append('kind: класс')
    lines.append('---')
    lines.append(f'# {cname}')
    lines.append('')
    lines.append(defn)
    lines.append('')
    if rels:
        lines.append('Отношения от этого класса: ' + ', '.join(f'{r} → {rr}' for r, rr in rels) + '.')
    else:
        lines.append('Отношения от этого класса: нет.')
    lines.append('')
    if attrs:
        av = ', '.join(f'{n} ({v})' if v else n for n, v in attrs)
        lines.append('Атрибуты: ' + av + '.')
    else:
        lines.append('Атрибуты: нет.')
    lines.append('')
    lines.append('## Связи')
    lines.append('')
    if parent:
        lines.append(f'- подклассОт: [[{parent}]]')
    with open(f'ontology/{cname}.md', 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print('OK', cname)
