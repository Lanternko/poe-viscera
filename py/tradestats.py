"""Per-tier trade filters for viscera.

Trade has no Lesser/Normal/Greater filter, so each tier is told apart by its
implicits, in this order:
  1. a stat every roll of this tier has and no other tier has;
  2. a stat all tiers share, by the first value's range (ranges must not overlap);
  3. excluding ("not") a stat each other tier always has and this tier never has.
Returns {tier: [[stat_id, min, max, negate], ...]} or None when the tiers
cannot all be told apart.
"""
import json, re

NUM = re.compile(r'\((-?[\d.]+)\D{1,3}?(-?[\d.]+)\)|(-?\d+(?:\.\d+)?)')
GROUPS = ('implicit', 'explicit')


def label_tier(lab, labels):
    if lab == 'Low':
        return 'Lesser'
    if lab == 'Med':
        return 'Normal'
    if lab.startswith('High') or lab == 'Uber':
        return 'Greater'
    if (lab == '' or lab.isdigit()) and 'Med' not in labels:
        return 'Normal'
    return None


def load_index(path):
    idx = {}
    for g in json.load(open(path, encoding='utf8'))['result']:
        if g['id'] in GROUPS:
            for e in g['entries']:
                idx.setdefault(e['text'], {})[g['id']] = e['id']
    return idx


def template(text):
    vals = []
    def rep(m):
        if m.group(1):
            vals.append((float(m.group(1)), float(m.group(2))))
        else:
            vals.append((float(m.group(3)),) * 2)
        return '#'
    return NUM.sub(rep, text), vals


def lookup(idx, text):
    t, vals = template(text)
    for c, v in ((t, vals), (t.lstrip('+'), vals), ('+' + t, vals), (text, [])):
        hit = idx.get(c)
        if hit:
            return next(hit[g] for g in GROUPS if g in hit), c, v
    return None


def parse_mod(idx, text):
    whole = lookup(idx, text)
    if whole:
        return [whole]
    return [p for p in (lookup(idx, line) for line in text.split('\n')) if p]


def trade_value(tt, vals):
    if not vals:
        return None
    if '# to #' in tt and len(vals) >= 2:
        return ((vals[0][0] + vals[1][0]) / 2, (vals[0][1] + vals[1][1]) / 2)
    return vals[0]


def num(x):
    return int(x) if float(x).is_integer() else x


def tier_filters(idx, mods, tiers):
    if len(tiers) < 2:
        return None
    labels = {m[0] for m in mods}
    by = {}
    for lab, text in mods:
        T = label_tier(lab, labels)
        if T in tiers:
            alt = parse_mod(idx, text)
            if not alt:
                return None
            by.setdefault(T, []).append({s[0]: s for s in alt})
    if set(by) != set(tiers):
        return None
    common = {T: set.intersection(*(set(a) for a in alts)) for T, alts in by.items()}
    anyof = {T: set.union(*(set(a) for a in alts)) for T, alts in by.items()}
    out = {}
    for T in by:
        others = [o for o in by if o != T]
        uniq = sorted(s for s in common[T] if all(s not in anyof[o] for o in others))
        if uniq:
            out[T] = [[uniq[0], None, None, 0]]
            continue
        found = None
        if len(by[T]) == 1:
            for sid in sorted(common[T]):
                s = by[T][0][sid]
                mine = trade_value(s[1], s[2])
                theirs = [trade_value(a[sid][1], a[sid][2]) for o in others for a in by[o] if sid in a]
                if mine and all(r and (r[1] < mine[0] or r[0] > mine[1]) for r in theirs):
                    lo, hi = sorted(mine)
                    found = [[sid, num(lo), num(hi), 0]]
                    break
        if not found:
            neg = []
            for o in others:
                c = sorted(s for s in common[o] if s not in anyof[T])
                if not c:
                    neg = None
                    break
                if c[0] not in [n[0] for n in neg]:
                    neg.append([c[0], None, None, 1])
            if neg:
                keep = sorted(common[T])
                found = ([[keep[0], None, None, 0]] if keep else []) + neg
        if not found:
            return None
        out[T] = found
    return out
