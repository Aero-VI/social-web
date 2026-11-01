#!/usr/bin/env python3
"""build2.py - v2 dataset for friends.aeroverra.com
 - ALL 547 followings as nodes (not just the 252 with edges)
 - fb (follows-back) comes from the DYI export = authoritative, 278
 - followed_back_ts -> year, for the timeline visual
 - communities carry their real lead name, not 'Cluster A'
 - growth.json: monthly follower acquisition from the 1.1M DYI timestamps
"""
import json, collections, datetime, os

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, 'ig-export-out')

following = json.load(open(f'{BASE}/following.json'))
mut = json.load(open(f'{BASE}/mutuals_dyi.json'))
old = json.load(open(f'{BASE}/data.json'))

mut_by_pk = {m['pk']: m for m in mut}
links = old['links']
oldnodes = {n['id']: n for n in old['nodes']}

# in-degree over the crawled edge set
indeg = collections.Counter()
for l in links:
    indeg[l['t']] += 1

ME = '222397560'
nodes = [{'id': ME, 'un': 'nnickkh', 'full': 'Nicholas Halka', 'ver': True,
          'deg': 0, 'c': -1, 'me': 1, 'fb': 1, 'yr': 0}]

for f in following:
    pk = f['pk']
    o = oldnodes.get(pk, {})
    m = mut_by_pk.get(pk)
    yr = 0
    if m and m.get('followed_back_ts'):
        yr = datetime.datetime.utcfromtimestamp(m['followed_back_ts']).year
    nodes.append({
        'id': pk,
        'un': f['un'],
        'full': f.get('full') or '',
        'ver': bool(f.get('ver')),
        'deg': indeg.get(pk, 0),
        'c': o.get('c', -2),          # -2 = no edge data
        'me': 0,
        'fb': 1 if m else 0,
        'yr': yr,
        'ts': (m or {}).get('followed_back_ts', 0),
    })

known = {n['id'] for n in nodes}
links = [l for l in links if l['s'] in known and l['t'] in known]

# communities: keep ids, attach real lead names + live counts
comm = {c['c']: dict(c) for c in old['communities']}
cnt_all = collections.Counter(n['c'] for n in nodes if n['c'] >= 0)
cnt_mut = collections.Counter(n['c'] for n in nodes if n['c'] >= 0 and n['fb'])
communities = []
for cid, c in sorted(comm.items(), key=lambda kv: -cnt_all.get(kv[0], 0)):
    if cnt_all.get(cid, 0) < 2:
        continue
    communities.append({'c': cid, 'lead': c['lead'], 'leadfull': c.get('leadfull', ''),
                        'n': cnt_all.get(cid, 0), 'nmut': cnt_mut.get(cid, 0),
                        'top': c.get('top', [])[:5]})

years = collections.Counter(n['yr'] for n in nodes if n['fb'] and n['yr'])
yearlist = [{'y': y, 'n': years[y]} for y in sorted(years)]

stats = {
    'following': len(following),
    'mutual': sum(1 for n in nodes if n['fb'] and not n['me']),
    'oneway': sum(1 for n in nodes if not n['fb'] and not n['me']),
    'verified': sum(1 for n in nodes if n['ver'] and not n['me']),
    'verified_mut': sum(1 for n in nodes if n['ver'] and n['fb'] and not n['me']),
    'edges': len(links),
    'communities': len(communities),
    'followers': 1103885,
}

json.dump({'nodes': nodes, 'links': links, 'communities': communities,
           'years': yearlist, 'stats': stats},
          open(f'{BASE}/data2.json', 'w'), separators=(',', ':'))

# ---- follower growth, monthly, from the DYI export -------------------------
src = '/home/aeroverra/azula-bot/workspace/ig-export/out/followers.json'
if os.path.exists(src):
    fol = json.load(open(src))
    months = collections.Counter()
    for _, ts in fol.items():
        d = datetime.datetime.utcfromtimestamp(ts)
        months[f'{d.year}-{d.month:02d}'] += 1
    series, run = [], 0
    for ym in sorted(months):
        run += months[ym]
        series.append({'m': ym, 'n': months[ym], 'cum': run})
    json.dump({'series': series, 'total': sum(months.values())},
              open(f'{BASE}/growth.json', 'w'), separators=(',', ':'))
    print('growth months:', len(series), 'total', sum(months.values()))

print(json.dumps(stats, indent=1))
print('nodes', len(nodes), 'links', len(links), 'communities', len(communities))
print('years', yearlist)
