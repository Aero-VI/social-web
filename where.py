#!/usr/bin/env python3
"""where.py - day-by-day location timeline from travel.aeroverra.com trips.json,
then match each mutual's followed_back date to where Nicholas actually was."""
import json,datetime,collections
T=json.load(open('/tmp/trips.json'))
def d(s):
    if not s: return None
    return datetime.date.fromisoformat(s[:10])
day={}   # date -> (label, cc, kind)
def put(dt,label,cc,kind,prio):
    cur=day.get(dt)
    if cur is None or prio>cur[3]: day[dt]=(label,cc,kind,prio)
for t in T:
    for s in t.get('Segments',[]):
        k=s.get('SegmentType')
        if k in ('Accommodation','Hotel'):
            ci=d(s.get('CheckInDate') or s.get('CheckIn')); co=d(s.get('CheckOutDate') or s.get('CheckOut'))
            city=s.get('City') or s.get('DisplayName') or s.get('HotelName'); cc=s.get('CountryCode')
            if ci and co:
                n=(co-ci).days
                for i in range(max(n,1)):
                    put(ci+datetime.timedelta(days=i),city,cc,'stay',3)
        elif k=='Cruise':
            dep=s.get('DeparturePort',{}); arr=s.get('ArrivalPort',{})
            a=d(dep.get('Time')); b=d(arr.get('Time'))
            ship=s.get('Ship') or s.get('CruiseLine') or 'Cruise'
            if a and b:
                for i in range((b-a).days+1):
                    put(a+datetime.timedelta(days=i),ship,None,'sea',2)
            for p in s.get('PortsOfCall') or []:
                pd=d(p.get('Date'))
                if pd: put(pd,p.get('City') or p.get('PortName'),p.get('CountryCode'),'port',4)
            if a: put(a,dep.get('City'),dep.get('CountryCode'),'port',4)
            if b: put(b,arr.get('City'),arr.get('CountryCode'),'port',4)
        elif k in ('Flight','Train','Bus'):
            arr=s.get('Arrival',{}); t2=d(arr.get('Time'))
            if t2: put(t2,arr.get('City'),arr.get('CountryCode'),'arrive',1)
json.dump({str(k):v[:3] for k,v in sorted(day.items())},open('timeline.json','w'))
print('days mapped',len(day),'range',min(day),max(day))
M=json.load(open('mutuals_dyi.json'))
hit=0;miss=0;by=collections.Counter()
for m in M:
    ts=m.get('followed_back_ts')
    if not ts: continue
    dt=datetime.datetime.utcfromtimestamp(ts).date()
    # exact day, else nearest within 3 days
    loc=day.get(dt)
    if not loc:
        for off in range(1,4):
            loc=day.get(dt-datetime.timedelta(days=off)) or day.get(dt+datetime.timedelta(days=off))
            if loc: break
    if loc:
        hit+=1; m['loc']=loc[0]; m['cc']=loc[1]; m['kind']=loc[2]; by[(loc[1],loc[0])]+=1
    else: miss+=1
print('matched',hit,'unmatched',miss)
for k,v in by.most_common(25): print(v,k)
json.dump(M,open('mutuals_located.json','w'))
