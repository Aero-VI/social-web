# v2 2026-11-01: adds follows-back flag (fb), named/auto-labelled communities, per-node neighbour lists.
import json,random,collections
F=json.load(open('following.json')); bypk={x['pk']:x for x in F}
G=json.load(open('graph_raw.json'))
ME='222397560'
try: MUT=json.load(open('mutuals.json'))
except Exception: MUT={}
edges=[]; indeg=collections.Counter(); mut={}
for un,v in G.items():
    a=v['pk']; s=set(v['f'])&set(bypk); mut[a]=len(s)
    for b in s:
        if b!=a: edges.append((a,b)); indeg[b]+=1
keep=set(v['pk'] for v in G.values()) | {p for p,c in indeg.items() if c>=1}
edges=[(a,b) for a,b in edges if a in keep and b in keep]
adj=collections.defaultdict(set)
for a,b in edges: adj[a].add(b); adj[b].add(a)
lab={n:i for i,n in enumerate(keep)}
random.seed(3); order=list(keep)
for it in range(25):
    random.shuffle(order); ch=0
    for n in order:
        if not adj[n]: continue
        c=collections.Counter(lab[m] for m in adj[n] if m in lab)
        if c:
            best=c.most_common(1)[0][0]
            if lab[n]!=best: lab[n]=best; ch+=1
    if ch==0: break
sizes=collections.Counter(lab.values())
top=[c for c,_ in sizes.most_common(8)]
cmap={c:i for i,c in enumerate(top)}
def ci(p): return cmap.get(lab[p],8)
# ---- auto-name each community by its highest in-degree member ----
members=collections.defaultdict(list)
for p in keep: members[ci(p)].append(p)
cinfo=[]
for c in range(9):
    m=members.get(c,[])
    if not m: continue
    m.sort(key=lambda p:(-indeg.get(p,0),-mut.get(p,0)))
    head=m[0]
    verif=sum(1 for p in m if bypk[p]['ver'])
    cinfo.append({'c':c,'n':len(m),'lead':bypk[head]['un'],
                  'leadfull':bypk[head]['full'][:24],'ver':verif,
                  'top':[bypk[p]['un'] for p in m[:5]]})
nodes=[{'id':ME,'un':'nnickkh','full':'Nicholas Halka','ver':True,'deg':len(F),'mut':len(F),'c':-1,'me':1,'fb':1}]
for p in keep:
    u=bypk[p]
    nodes.append({'id':p,'un':u['un'],'full':u['full'][:28],'ver':u['ver'],
                  'deg':indeg.get(p,0),'mut':mut.get(p,0),'c':ci(p),'me':0,
                  'fb':int(MUT.get(str(p),0))})
links=[{'s':a,'t':b} for a,b in edges]
for v in G.values(): links.append({'s':ME,'t':v['pk'],'me':1})
nmut=sum(1 for n in nodes if n['fb'] and not n['me'])
out={'nodes':nodes,'links':links,'communities':cinfo,
     'stats':{'following':len(F),'verified':sum(1 for x in F if x['ver']),
              'crawled':len(G),'edges':len(links),'nodes':len(nodes),
              'communities':len(cinfo),'mutuals':sum(MUT.values()),
              'checked':len(MUT),'mutnodes':nmut},
     'topmut':sorted([{'un':bypk[v['pk']]['un'],'n':mut[v['pk']],'full':bypk[v['pk']]['full'][:24],'fb':int(MUT.get(str(v['pk']),0))} for v in G.values() if mut.get(v['pk'],0)>0],key=lambda x:-x['n'])[:20],
     'topconn':sorted([{'un':bypk[p]['un'],'n':c,'full':bypk[p]['full'][:24],'ver':bypk[p]['ver'],'fb':int(MUT.get(str(p),0))} for p,c in indeg.items() if p in bypk],key=lambda x:-x['n'])[:20]}
json.dump(out,open('data.json','w'))
print(json.dumps(out['stats'],indent=1))
for c in cinfo: print(c['c'],c['n'],'lead=@'+c['lead'],'ver',c['ver'],c['top'])
