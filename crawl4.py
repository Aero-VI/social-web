import json,os,subprocess,time
from concurrent.futures import ThreadPoolExecutor
K=os.environ['HIKERAPI_KEY']
MUT=json.load(open('mutuals_dyi.json'))
try: res=json.load(open('graph_mut.json'))
except Exception: res={}
prev=json.load(open('graph_raw.json'))
for un,v in prev.items():
    if v['pk'] not in res: res[v['pk']]={'un':un,'f':v['f']}
def get(url):
    for a in range(3):
        p=subprocess.run(['curl','-s','-m','50','-H',f'x-access-key: {K}',url],capture_output=True,text=True)
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
mp={m['pk'] for m in MUT}
todo=[m for m in MUT if m['pk'] not in res]
print("todo",len(todo),flush=True)
done=[0]
def work(m):
    L=follows(m['pk'])
    done[0]+=1
    print(f"{done[0]}/{len(todo)} {m['un']} n={len(L)} sm={len(set(L)&mp)}",flush=True)
    return m['pk'],{'un':m['un'],'f':L}
with ThreadPoolExecutor(max_workers=8) as ex:
    for pk,v in ex.map(work,todo):
        res[pk]=v
json.dump(res,open('graph_mut.json','w'))
print("DONE",len(res),flush=True)
