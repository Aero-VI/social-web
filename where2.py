#!/usr/bin/env python3
import json,datetime,collections
T=json.load(open('/tmp/trips.json'))
def d(s):
    if not s: return None
    try: return datetime.date.fromisoformat(s[:10])
    except Exception: return None
day={}
def put(dt,label,cc,kind,prio,trip):
    cur=day.get(dt)
    if cur is None or prio>cur[4]: day[dt]=(label,cc,kind,trip,prio)
for t in T:
    tn=t.get('TripName'); 
    for s in t.get('Segments',[]):
        k=s.get('SegmentType')
        if k in ('Accommodation','Hotel'):
            ci=d(s.get('CheckInDate') or s.get('CheckIn')); co=d(s.get('CheckOutDate') or s.get('CheckOut'))
            city=s.get('City') or s.get('DisplayName') or s.get('HotelName'); cc=s.get('CountryCode')
            if ci and co:
                for i in range(max((co-ci).days,1)): put(ci+datetime.timedelta(days=i),city,cc,'stay',3,tn)
        elif k=='Cruise':
            dep=s.get('DeparturePort',{}); arr=s.get('ArrivalPort',{})
            a=d(dep.get('Time')); b=d(arr.get('Time')); ship=s.get('Ship') or 'Cruise'
            if a and b:
                for i in range((b-a).days+1): put(a+datetime.timedelta(days=i),ship,None,'sea',2,tn)
            for p in s.get('PortsOfCall') or []:
                pd=d(p.get('Date'))
                if pd: put(pd,p.get('City') or p.get('PortName'),p.get('CountryCode'),'port',4,tn)
            if a: put(a,dep.get('City'),dep.get('CountryCode'),'port',4,tn)
            if b: put(b,arr.get('City'),arr.get('CountryCode'),'port',4,tn)
        elif k in ('Flight','Train','Bus'):
            arr=s.get('Arrival',{}); t2=d(arr.get('Time'))
            if t2: put(t2,arr.get('City'),arr.get('CountryCode'),'arrive',1,tn)
M=json.load(open('mutuals_dyi.json'))
hit=0
for m in M:
    ts=m.get('followed_back_ts')
    if not ts: continue
    dt=datetime.datetime.fromtimestamp(ts,datetime.timezone.utc).date()
    m['d']=str(dt)
    loc=day.get(dt); off=0
    if not loc:
        for o in range(1,4):
            loc=day.get(dt-datetime.timedelta(days=o)) or day.get(dt+datetime.timedelta(days=o))
            if loc: off=o; break
    if loc:
        hit+=1; m['loc'],m['cc'],m['kind'],m['trip']=loc[0],loc[1],loc[2],loc[3]
json.dump(M,open('mutuals_located.json','w'))
print('matched',hit,'/',len(M))
tr=collections.Counter(m.get('trip') for m in M if m.get('trip'))
for k,v in tr.most_common(12): print(v,k)
