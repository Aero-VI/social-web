import json,os,subprocess,time,random
K=os.environ['HIKERAPI_KEY']
F=json.load(open('following.json')); bypk={x['pk']:x for x in F}
H=json.load(open('hubs.json'))
def get(url):
    for a in range(3):
        p=subprocess.run(['curl','-s','-m','45','-H',f'x-access-key: {K}',url],capture_output=True,text=True)
        try: return json.loads(p.stdout)
        except Exception: time.sleep(2)
    return None
def follows(pk,maxpages=2):
    out=[];cur=''
    for i in range(maxpages):
        d=get(f"https://api.hikerapi.com/v1/user/following/chunk?user_id={pk}"+(f"&max_id={cur}" if cur else ""))
        if not d or not isinstance(d,list): break
        us,cur=d[0],d[1]
        out+=[str(x['pk']) for x in us]
        if not cur: break
    return out
res={}
try: res=json.load(open('graph_raw.json'))
except Exception: pass
for h,v in H.items():
    if v['n']>0 and h not in res: res[h]={'pk':v['pk'],'f':v['f']}
done=set(v['pk'] for v in res.values())
core=set()
for h,v in H.items(): core |= (set(v['f']) & set(bypk))
prio=[p for p in core]
rest=[x['pk'] for x in F if x['pk'] not in core and not x['ver']]
random.seed(7); random.shuffle(rest)
targets=prio+rest[:max(0,180-len(prio))]
print("targets",len(targets),"already",len(done),flush=True)
for i,pk in enumerate(targets):
    if pk in done: continue
    un=bypk[pk]['un']; L=follows(pk); done.add(pk)
    if L: res[un]={'pk':pk,'f':L}
    print(f"{i+1}/{len(targets)} {un} n={len(L)} shared={len(set(L)&set(bypk))}",flush=True)
    if (i+1)%10==0: json.dump(res,open('graph_raw.json','w'))
json.dump(res,open('graph_raw.json','w'))
print("DONE",len(res),flush=True)
