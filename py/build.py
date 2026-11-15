import json, sys, base64, re, os, datetime
base = sys.argv[1]
d = json.load(open(base + '/py/data.json', encoding='utf8'))
nj = json.load(open(base + '/dl/ninja.json', encoding='utf8'))['lines']
# chaos per divine
ratios = [x['chaosValue'] / x['divineValue'] for x in nj if x.get('divineValue') and x['divineValue'] > 1]
DIV = round(sorted(ratios)[len(ratios) // 2], 1)

def split_drop(s):
    m = re.match(r'Act (\d+), (.*?), (.*)$', s)
    if m:
        return dict(act=int(m.group(1)), boss=m.group(2), zone=m.group(3))
    parts = s.split(', ', 1)
    return dict(boss=parts[0], zone=parts[1] if len(parts) > 1 else '')

def vtypes(f):
    r = json.load(open(f, encoding='utf8'))['result']
    return set(x['type'] for c in r if c['id'] == 'viscera' for x in c['entries'])
TI, TT = vtypes(base + '/dl/items.json'), vtypes(base + '/dl/twitems.json')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tradestats
STATS = tradestats.load_index(base + '/dl/stats.json')
items = []
for i, v in enumerate(d):
    drops = []
    for en, tw in zip(v['drops'], v['drops_tw'] or v['drops']):
        a, b = split_drop(en), split_drop(tw)
        drops.append(dict(act=a.get('act'), boss=b['boss'], bossEn=a['boss'], zone=b['zone'], zoneEn=a['zone']))
    tiers = {}
    for p in v['prices']:
        tiers.setdefault(p['tier'], []).append([p['variant'] or '', p['chaos'] or 0, p['listed'] or 0, p['name'], p['did'] or ''])
    for k in tiers:
        tiers[k].sort(key=lambda r: -r[1])
    act = None
    if v['folder'].startswith('Act'):
        act = int(v['folder'][3:])
    img = open(f"{base}/img/{v['folder']}_{v['file']}.webp", 'rb').read()
    items.append(dict(
        id=i, slug=v['slug'], ti=v['name'] in TI, tt=(v['name_tw'] in TT) and v['name_tw'], en=v['name'], tw=v['name_tw'] or v['name'], slot=v['slot'] or '',
        group='pin' if v['folder'] == 'PinnacleAndMapBosses' else 'act', act=act,
        drops=drops, mods=v['mods_tw'], modsEn=v['mods'], tiers=tiers,
        tq=tradestats.tier_filters(STATS, v['mods'], set(tiers)),
        img='data:image/webp;base64,' + base64.b64encode(img).decode()))

# fill slot for unpriced items from poedb? leave blank -> infer from ninja missing
grim = [
 ["The Arkhon", "The Shaper", "Shaper's Head"],
 ["The Malignance", "The Elder", "Elder's Head"],
 ["The Unraveller", "The Shaper + The Elder", ""],
 ["The Templar", "Venarius", "Venarius' Scripture"],
 ["The Collector", "The Maven", "Maven's Orrery"],
 ["The Awakened", "Sirus", "Sirus' Head"],
 ["The Emissary", "The Eater of Worlds", "Eater of Worlds' Head"],
 ["The Iridescent", "The Searing Exarch", "Searing Exarch's Descry"],
 ["The Fearsome", "Incarnation of Fear", "Incarnation of Fear's Head"],
 ["The Neglectful", "Incarnation of Neglect", "Incarnation of Neglect's Cube"],
 ["The Dreadful", "Incarnation of Dread", "Incarnation of Dread's Head"],
]
tpl = open(base + '/py/template.html', encoding='utf8').read()
out = tpl.replace('/*DATA*/null', json.dumps(dict(items=items, div=DIV, grim=grim, snap=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')), ensure_ascii=False, separators=(',', ':')))
dest = sys.argv[2] if len(sys.argv) > 2 else base + '/viscera.html'
if len(sys.argv) > 2:  # standalone site: full document skeleton
    out = ('<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
           '</head><body>' + out + '</body></html>')
os.makedirs(os.path.dirname(dest), exist_ok=True)
open(dest, 'w', encoding='utf8').write(out)
print('div', DIV, 'items', len(items), 'bytes', len(out.encode()))
print('no slot:', [x['en'] for x in items if not x['slot']])
multi = [x for x in items if len(x['tiers']) > 1]
print('per-tier trade links:', sum(1 for x in multi if x['tq']), '/', len(multi))
