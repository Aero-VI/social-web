# Finding: follows-back must come from /v1/user/search/following (exact, 1 call, no pagination).
# /v1/user/following/chunk truncates and produces false negatives (adrianah.lee, 2026-11-01).
import json,subprocess,os,time
K=os.environ['HIKERAPI_KEY']; ME='222397560'
F=json.load(open('following.json'))
try: R=json.load(open('mutuals.json'))
except Exception: R={}
# seed from what we already proved
try:
    g=json.load(open('graph_raw.json'))
    fn=set(json.load(open('false_negatives.json')))
    for un,v in g.items():
        if ME in v['f'] or un in fn: R[str(v['pk'])]=1
except Exception: pass
json.dump(R,open('mutuals.json','w'))
todo=[x for x in F if str(x['pk']) not in R]
print('seeded',len(R),'todo',len(todo),flush=True)
for i,u in enumerate(todo):
    pk=str(u['pk'])
    url=f"https://api.hikerapi.com/v1/user/search/following?user_id={pk}&query=nnickkh"
    ok=0
    for a in range(2):
        p=subprocess.run(['curl','-s','-m','30','-H',f'x-access-key: {K}',url],capture_output=True,text=True)
        try: d=json.loads(p.stdout)
        except Exception: d=None
        if isinstance(d,list):
            ok=1 if any(str(x.get('pk'))==ME for x in d) else 0
            break
        time.sleep(2)
    else:
        continue
    R[pk]=ok
    if (i+1)%25==0:
        json.dump(R,open('mutuals.json','w'))
        print(f"{i+1}/{len(todo)} mutuals={sum(R.values())}",flush=True)
json.dump(R,open('mutuals.json','w'))
print('DONE checked',len(R),'mutuals',sum(R.values()),flush=True)
