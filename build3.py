#!/usr/bin/env python3
"""build3.py - FRIENDS-ONLY dataset. Mutuals (278) only, and an edge exists
only when BOTH people follow each other. Plus travel attribution."""
import json,collections,datetime,random
M=json.load(open('mutuals_located.json'))
G=json.load(open('graph_mut.json'))
ME='222397560'
mp={m['pk'] for m in M}
fol={pk:set(v['f']) for pk,v in G.items()}
cov={pk for pk in mp if pk in fol and fol[pk]}
# ---- mutual<->mutual edges ----
links=[];covl=sorted(cov)
for i,a in enumerate(covl):
    for b in covl[i+1:]:
        if b in fol[a] and a in fol[b]: links.append((a,b))
deg=collections.Counter()
for a,b in links: deg[a]+=1; deg[b]+=1
# ---- label propagation communities ----
adj=collections.defaultdict(set)
for a,b in links: adj[a].add(b); adj[b].add(a)
lab={n:n for n in adj}
random.seed(11)
for _ in range(25):
    ns=list(adj); random.shuffle(ns); ch=0
    for n in ns:
        if not adj[n]: continue
        c=collections.Counter(lab[m] for m in adj[n]).most_common(1)[0][0]
        if c!=lab[n]: lab[n]=c; ch+=1
    if not ch: break
groups=collections.defaultdict(list)
for n,l in lab.items(): groups[l].append(n)
byun={m['pk']:m for m in M}
comms=[]
for l,mem in sorted(groups.items(),key=lambda x:-len(x[1])):
    if len(mem)<3: continue
    lead=max(mem,key=lambda n:deg[n])
    comms.append({'lead':byun[lead]['un'],'n':len(mem),'members':mem})
cid={}
for i,c in enumerate(comms):
    for m in c['members']: cid[m]=i
nodes=[{'id':ME,'un':'nnickkh','full':'Nicholas Halka','ver':True,'me':1,'deg':len(mp),'c':-1,'yr':0}]
for m in M:
    yr=int(m['d'][:4]) if m.get('d') else 0
    nodes.append({'id':m['pk'],'un':m['un'],'full':m.get('full') or m['un'],'ver':bool(m.get('ver')),
        'deg':deg.get(m['pk'],0),'c':cid.get(m['pk'],-1),'yr':yr,'d':m.get('d'),
        'loc':m.get('loc'),'cc':m.get('cc'),'kind':m.get('kind'),'trip':m.get('trip'),
        'cov':1 if m['pk'] in cov else 0})
L=[{'s':a,'t':b} for a,b in links]
# ---- aggregates ----
cc=collections.Counter(m.get('cc') for m in M if m.get('cc'))
trips=collections.Counter(m.get('trip') for m in M if m.get('trip'))
city=collections.Counter(m.get('loc') for m in M if m.get('loc'))
yrs=collections.Counter(int(m['d'][:4]) for m in M if m.get('d'))
mon=collections.Counter(m['d'][:7] for m in M if m.get('d'))
out={'nodes':nodes,'links':L,'comms':[{'lead':c['lead'],'n':c['n'],'members':c['members']} for c in comms],
 'cc':cc.most_common(),'trips':trips.most_common(),'city':city.most_common(30),
 'yrs':sorted(yrs.items()),'mon':sorted(mon.items()),
 'stats':{'mutuals':len(M),'edges':len(L),'covered':len(cov),'located':sum(1 for m in M if m.get('cc') or m.get('loc')),
          'countries':len(cc),'trips':len(trips)}}
json.dump(out,open('data3.json','w'),separators=(',',':'))
print(json.dumps(out['stats'],indent=1))
print('communities',[(c['lead'],c['n']) for c in comms][:12])
print('top cc',cc.most_common(12))
