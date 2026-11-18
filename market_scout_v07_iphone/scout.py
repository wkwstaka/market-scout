#!/usr/bin/env python3
"""Public RSS evidence collector; no LLM, no revenue claims."""
import datetime as dt, email.utils, hashlib, json, pathlib, re, urllib.request, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parent
FEEDS={
 'Google News / AI automation':'https://news.google.com/rss/search?q=AI+%E6%A5%AD%E5%8B%99%E8%87%AA%E5%8B%95%E5%8C%96&hl=ja&gl=JP&ceid=JP:ja',
 'Google News / digital products':'https://news.google.com/rss/search?q=%E3%83%87%E3%82%B8%E3%82%BF%E3%83%AB%E5%95%86%E5%93%81+%E8%B2%A9%E5%A3%B2&hl=ja&gl=JP&ceid=JP:ja',
 'Google News / small business':'https://news.google.com/rss/search?q=%E4%B8%AD%E5%B0%8F%E4%BC%81%E6%A5%AD+DX+%E9%9C%80%E8%A6%81&hl=ja&gl=JP&ceid=JP:ja',
 'Google News / creator economy':'https://news.google.com/rss/search?q=%E3%82%AF%E3%83%AA%E3%82%A8%E3%82%A4%E3%82%BF%E3%83%BC+%E5%8F%8E%E7%9B%8A%E5%8C%96&hl=ja&gl=JP&ceid=JP:ja',
}
def clean(s): return re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',s or '')).strip()[:320]
def main():
 now=dt.datetime.now(dt.timezone.utc); path=ROOT/'data'/'research.json'
 try: old=json.loads(path.read_text(encoding='utf8')).get('items',[])
 except (ValueError,OSError): old=[]
 items={x['id']:x for x in old if isinstance(x,dict) and 'id' in x}
 statuses=[]
 for topic,url in FEEDS.items():
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'MarketScoutResearch/0.7 (RSS reader)'})
   with urllib.request.urlopen(req,timeout=18) as response: raw=response.read(1_000_000)
   root=ET.fromstring(raw); found=0
   for item in root.findall('.//item')[:12]:
    title=clean(item.findtext('title')); link=(item.findtext('link') or '').strip()
    if not title or not link.startswith('https://'): continue
    key=hashlib.sha256((topic+'|'+link).encode()).hexdigest()[:16]
    pub=clean(item.findtext('pubDate'))
    try: published=email.utils.parsedate_to_datetime(pub).isoformat()
    except (TypeError,ValueError): published=''
    items[key]={'id':key,'topic':topic,'title':title,'url':link,'published':published,'summary':clean(item.findtext('description')),'source_type':'news_aggregation','verification':'unverified','first_seen':items.get(key,{}).get('first_seen',now.isoformat())}
    found+=1
   statuses.append({'feed':topic,'status':'ok','count':found})
  except Exception as exc: statuses.append({'feed':topic,'status':'error','message':type(exc).__name__})
 # Retain up to 120; failed feeds must not erase previous findings
 rows=sorted(items.values(),key=lambda x:x.get('first_seen',''),reverse=True)[:120]
 output={'schema_version':'0.7','generated_at':now.isoformat(),'disclaimer':'News headlines are discovery leads, not validated customer demand or verified primary sources. No AI analysis or revenue automation has run.','feed_status':statuses,'items':rows}
 path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print('Stored',len(rows),'items;',statuses)
if __name__=='__main__':main()
