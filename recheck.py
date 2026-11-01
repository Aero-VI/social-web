import json,subprocess,os
K=os.environ['HIKERAPI_KEY']
g=json.load(open('graph_raw.json'))
no=[(k,v['pk'],len(v['f'])) for k,v in g.items() if '222397560' not in v['f']]
fixed=[]
for un,pk,n in no:
    url=f"https://api.hikerapi.com/v1/user/search/following?user_id={pk}&query=nnickkh"
    p=subprocess.run(['curl','-s','-m','25','-H',f'x-access-key: {K}',url],capture_output=True,text=True)
    try: d=json.loads(p.stdout)
    except Exception: d=None
    if isinstance(d,list) and any(str(x.get('pk'))=='222397560' for x in d):
        fixed.append(un); print('FN',un,n,flush=True)
json.dump(fixed,open('false_negatives.json','w'))
print('TOTAL_FN',len(fixed),'CORRECTED',43+len(fixed),'OF',len(g),flush=True)
