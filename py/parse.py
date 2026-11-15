import re, json, sys, html as H
base = sys.argv[1]

def strip(s):
    s = re.sub(r'<span class="ndash">.*?</span>', '–', s)
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    return H.unescape(s).strip()

def parse(path):
    h = open(path, encoding='utf8', errors='replace').read()
    start = h.find('row row-cols-1 row-cols-lg-2')
    end = h.find('id="Wickerman" class="tab-pane')
    body = h[start:end]
    cards = body.split('<div class="col"><div class="d-flex border-top rounded">')[1:]
    out = {}
    for c in cards:
        slug = re.search(r'href="([^"]+)"', c).group(1)
        img = re.search(r'src="([^"]+)"', c).group(1)
        name = strip(re.search(r'<div class="flex-grow-1 ms-2"><a [^>]*>(.*?)</a>', c).group(1))
        drops = [strip(x) for x in re.findall(r'Drop: <span[^>]*>(.*?)</span></div>', c)]
        mods = []
        for m in re.findall(r'<div class="explicitMod">(.*?)</div>', c):
            lab = re.match(r'<span class="text-secondary">([^<]*): </span>', m)
            label = lab.group(1) if lab else ''
            text = strip(m[lab.end():] if lab else m)
            mods.append([label, text])
        key = slug + '|' + img
        out[key] = dict(slug=slug, img=img, name=name, drops=drops, mods=mods)
    return out

us = parse(base + '/dl/us.html')
tw = parse(base + '/dl/tw.html')
items = []
for k, v in us.items():
    t = tw.get(k, {})
    v['name_tw'] = t.get('name', '')
    v['drops_tw'] = t.get('drops', [])
    v['mods_tw'] = t.get('mods', [])
    v['folder'] = v['img'].split('/Viscera/')[1].split('/')[0]
    v['file'] = v['img'].split('/')[-1].replace('.webp', '')
    items.append(v)

# poe.ninja prices
nj = json.load(open(base + '/dl/ninja.json', encoding='utf8'))['lines']
if len(nj) < 50:
    sys.exit(f'poe.ninja returned only {len(nj)} lines; keep the previous deploy')
import base64
def icon_file(u):
    p = u.split('/gen/image/')[1].split('/')[0]
    p += '=' * (-len(p) % 4)
    return json.loads(base64.urlsafe_b64decode(p))[2]['f'].split('/')[-1]
prices = {}
for x in nj:
    f = icon_file(x['icon'])
    nm = x['name']
    tier = 'Greater' if nm.startswith('Greater ') else 'Lesser' if nm.startswith('Lesser ') else 'Normal'
    prices.setdefault(f, []).append(dict(name=nm, tier=tier, variant=x.get('variant'),
        chaos=x.get('chaosValue'), div=x.get('divineValue'), listed=x.get('listingCount'), slot=x.get('itemType'), did=x.get('detailsId')))
for v in items:
    v['prices'] = prices.get(v['file'], [])
    v['slot'] = v['prices'][0]['slot'] if v['prices'] else ''
missing = [v['name'] for v in items if not v['prices']]
json.dump(items, open(base + '/py/data.json', 'w', encoding='utf8'), ensure_ascii=False)
print(len(us), len(tw), len(items), 'no price:', len(missing), missing[:40])
print(json.dumps(items[0], ensure_ascii=False)[:1500])
print(json.dumps(items[-3], ensure_ascii=False)[:1500])
