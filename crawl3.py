import json,os,subprocess,time
K=os.environ['HIKERAPI_KEY']
MUT=json.load(open('mutuals_dyi.json'))
try: res=json.load(open('graph_mut.json'))
except Exception: res={}
def get(url):
    for a in range(3):
        p=subprocess.run(['curl','-s','-m','45','-H',f'x-access-key: {K}',url],capture_output=True,text=True)
        try: return json.loads(p.stdout)
        except Exception: time.sleep(2)
    return None
def follows(pk,maxpages=10):
    out=[];cur=''
    for i in range(maxpages):
        d=get(f"https://api.hikerapi.com/v1/user/following/chunk?user_id={pk}"+(f"&max_id={cur}" if cur else ""))
        if not d or not isinstance(d,list) or len(d)<2: break
        us,cur=d[0],d[1]
        out+=[str(x['pk']) for x in us]
        if not cur: break
    return out
# seed from prior crawl
prev=json.load(open('graph_raw.json'))
for un,v in prev.items():
    if v['pk'] not in res: res[v['pk']]={'un':un,'f':v['f']}
mp={m['pk'] for m in MUT}
todo=[m for m in MUT if m['pk'] not in res]
print("todo",len(todo),flush=True)
for i,m in enumerate(todo):
    L=follows(m['pk'])
    res[m['pk']]={'un':m['un'],'f':L}
    print(f"{i+1}/{len(todo)} {m['un']} n={len(L)} sharedmut={len(set(L)&mp)}",flush=True)
    if (i+1)%10==0: json.dump(res,open('graph_mut.json','w'))
json.dump(res,open('graph_mut.json','w'))
print("DONE",len(res),flush=True)
