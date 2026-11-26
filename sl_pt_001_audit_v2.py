#!/usr/bin/env python3
"""FD-6 independent auditor, Python 3.12 standard library.
Exposure: exactly these four supplied attachments:
SL-PT-001_R4.2i_Stage_A_Amendment_Candidate_Claude_2026-11-26(1).md
SL-PT-001_Stage_A_Freeze_Record_R4.2i_2026-11-26.txt
SL-PT-001_Interface_Contract_TER-1_v1(1).md
sl_pt_001_audit(1).py
No harness code, external tests, TER output, Claude conversations/packages,
credentials or orders seen. Stage A only; E-1/E-2 apply.
Verified attachment SHA-256: 4259551121fa3d271074fb13da51fb270ae859b0b516a953752731f20972a51a.
Usage: python sl_pt_001_audit_v2.py REPOSITORY --custody-commit COMMIT --scope ID
       [--evidence-root experiments/sl-pt-001]
Local committed evidence only; stdout plain text and JSON. No network or writes.
Remote push timing and seed secrecy remain externally unverified.
"""
import argparse
import calendar
import collections
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from fractions import Fraction as F
from urllib.parse import urlsplit, parse_qs

SPEC = '4259551121fa3d271074fb13da51fb270ae859b0b516a953752731f20972a51a'
SPEC_PATH = 'experiments/sl-pt-001/SL-PT-001_R4.2i_Stage_A_Amendment_Candidate_Claude_2026-11-26.md'
LIMITATION = 'Disconnection from trading is asserted at the HTTP-client level only. Alternate egress paths in the process or host (other libraries, raw sockets, proxies, inherited handles) were not excluded.'
NS = 10**9
STEP = 300*NS
V = ['V'+str(i) for i in range(1,12)] + ['V12a','V12b']
Q = ['Q'+str(i) for i in range(1,6)]
NUMS = ['S20_k','S50_k','S20_prev','S50_prev','D_prev','D_k']
CLOCK = ['t_send','t_recv','D','θ_low','θ_high']
ART = ['bars_sha256','bars_headers_sha256','quote_sha256','quote_headers_sha256']
ARRAYS = ['completed_bars','excluded_bars','bar_store_transitions','rule_results','used_bars']
BAR_FIELDS = ('o','h','l','c','v','vw','n')
ROUND = 'bid ask price_increment qty_increment min_order_size f_res shadow_cash shadow_reserved cash_available budget shadow_btc shadow_reserved_btc'.split()
PROPOSAL = 'instrument side order_type L q R rounding_inputs'.split()
TER = ('schema origin manifest_sha256 slot_index cycle_id invocation_instant T_d created bars_request quote_request signal mapping proposal terminal_state policy_sha256 displayed_sizes egress_scope lock_clock_at V12a_evidence injection'.split()+V+Q+NUMS+CLOCK+ART+ARRAYS)
MANIFEST = 'instrument T_d0 declared_slots opening_cash frozen_set_hashes harness_sha256 policy_sha256 task_xml_sha256 wrapper_sha256 prev_chain_head'.split()
BODIES = {'GENESIS':'experiment_id frozen_set_hashes','RUN_OPEN':'manifest_sha256','CYCLE_OVERRUN':'slot_index old_process_id','CONCURRENT_INVOCATION':'slot_index invocation_instant','OFF_RUN':'invocation_instant','INJECTION_ABORTED':'proposal result','RUN_STOPPED':'instant','RUN_CLOSE':'invocation_log_sha256 task_xml_sha256'}
REASONS = 'V12A_FAILED V12B_FAILED FETCH_FAILED DATA_INVALID NO_PROPOSAL INJECTED'.split()
NO_DECISION = 'FETCH_FAILED INCOMPLETE_RESPONSE MALFORMED_VALUE DATA_CONFLICT STALE_SERIES DATA_GAP INSUFFICIENT_HISTORY SOURCE_REVISION QUOTE_INVALID'.split()
TERMINALS = ['HOLD','NO_ACTION','REJECTED','SHADOW_EXPIRED','BOUNDARY_FAIL','CYCLE_OVERRUN']+['NO_DECISION ('+x+')' for x in NO_DECISION]
RULES = dict(zip('R1 R2 R3 R4 R5 R6 R7 R8 R9 R10 R11 R12 R13 R15 R16'.split(), 'BTC/USD LIMIT SCHEMA_VALID 15 0.01 CASH_AVAILABLE 150 300 BTC_AVAILABLE INCREMENTS_AND_MINIMUM ONE_OPEN 450 90 EXIT_LONG NO_OPEN_OR_UNRESOLVED'.split()))
POLICY = dict(f_res='0.0025',settle_s='60',W_s='90',freshness_s='15',rules=RULES)
for key,value in [('price_increment','1'),('qty_increment','0.0001'),('min_order_size','0.0001')]:
    POLICY[key] = dict(value=value,source='support_table_DOCUMENTED',status='UNVERIFIED')
DEC = re.compile(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\Z')
INT = re.compile(r'-?(?:0|[1-9][0-9]*)\Z')
HASH = re.compile(r'[0-9a-f]{64}\Z')

def sha(b): return hashlib.sha256(b).hexdigest()
def require(ok, reason):
    if not ok: raise ValueError(reason)
def keys(o, names):
    require(type(o) is dict and set(o)==set(names), 'closed keys: expected '+','.join(sorted(names)))
def string(x):
    require(type(x) is str, 'expected string'); x.encode('utf-8'); return x
def hx(x):
    require(type(x) is str and HASH.fullmatch(x), 'invalid SHA-256'); return x
def integer(x):
    require(type(x) is str and INT.fullmatch(x), 'expected integer string'); return int(x)
def dec(x):
    require(isinstance(x,str) and DEC.fullmatch(x), 'expected exact decimal token'); return F(x)
def arr(x): require(type(x) is list,'expected array'); return x
def safeint(x):
    require(type(x) is int and 0<=x<=9007199254740991,'expected nonnegative safe JSON integer'); return x
def nullable(fn,x): return None if x is None else fn(x)
def check(b, reason=None): return {'result': 'NOT_EVALUATED' if b is None else ('PASS' if b else 'FAIL'), 'reason':reason if b is None else None}
def no_dec(reason): return 'NO_DECISION ('+reason+')'
def jcs(x):
    if x is None: return 'null'
    if type(x) is str: return json.dumps(string(x),ensure_ascii=False,separators=(',',':'))
    if type(x) is int: return str(safeint(x))
    if type(x) is list: return '['+','.join(jcs(y) for y in x)+']'
    if type(x) is dict: return '{'+','.join(jcs(k)+':'+jcs(x[k]) for k in sorted(x,key=lambda s:s.encode('utf-16-be')))+'}'
    raise ValueError('unsupported JCS primitive')

# Exact JSON lexer/parser. Raw mode retains original number spelling and object
# byte-equivalent text spans for V4. Strict mode admits safe integers only.
class Token(str): pass
class RawObject(dict):
    def __init__(self, value, raw): super().__init__(value); self.raw=raw
class Parser:
    def __init__(self,b,raw=False): self.s=b.decode('utf-8'); self.i=0; self.raw=raw
    def ws(self):
        while self.i<len(self.s) and self.s[self.i] in ' \t\r\n': self.i+=1
    def take(self,c):
        self.ws(); require(self.s[self.i:self.i+1]==c,'expected '+c); self.i+=1
    def quoted(self):
        require(self.s[self.i:self.i+1]=='"','expected JSON string')
        s,self.i=json.decoder.scanstring(self.s,self.i+1,True); return string(s)
    def value(self):
        self.ws(); start=self.i; c=self.s[self.i:self.i+1]
        if c=='"': return self.quoted()
        if c=='{':
            self.i+=1; self.ws(); o={}
            if self.s[self.i:self.i+1]!='}':
                while True:
                    self.ws(); k=self.quoted(); require(k not in o,'duplicate JSON key'); self.take(':'); o[k]=self.value(); self.ws()
                    if self.s[self.i:self.i+1]!=',': break
                    self.i+=1
            self.take('}'); return RawObject(o,self.s[start:self.i]) if self.raw else o
        if c=='[':
            self.i+=1; self.ws(); a=[]
            if self.s[self.i:self.i+1]!=']':
                while True:
                    a.append(self.value()); self.ws()
                    if self.s[self.i:self.i+1]!=',': break
                    self.i+=1
            self.take(']'); return a
        for lit,val in [('null',None),('true',True),('false',False)]:
            if self.s.startswith(lit,self.i): self.i+=len(lit); return val
        m=re.match(r'-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?',self.s[self.i:]); require(m,'malformed JSON token')
        tok=m.group(); self.i+=len(tok)
        if self.raw: return Token(tok)
        require(INT.fullmatch(tok),'noninteger JSON number forbidden'); return safeint(int(tok))
    def parse(self):
        result=self.value(); self.ws(); require(self.i==len(self.s),'trailing JSON content'); return result

def load(b, raw=False): return Parser(b,raw).parse()
def ter_scalars(o):
    if type(o) is dict:
        for k,v in o.items(): string(k); ter_scalars(v)
    elif type(o) is list:
        for v in o: ter_scalars(v)
    else: require(o is None or type(o) is str,'TER scalar is not string/null')
def hash_map(o):
    require(type(o) is dict and o.get(SPEC_PATH)==SPEC,'frozen-set map missing pinned spec')
    for k,v in o.items(): string(k); hx(v)
def proposal_schema(p):
    keys(p,PROPOSAL); keys(p['rounding_inputs'],ROUND)
    for k in ('instrument','side','order_type'): string(p[k])
    for k in ('L','q','R'): dec(p[k])
    for x in p['rounding_inputs'].values(): dec(x)
def ter_schema(t):
    keys(t,TER); ter_scalars(t)
    require(t['schema']=='TER-1' and t['origin'] in ('SCHEDULED','INJECTED'),'TER identity')
    require(t['egress_scope']=='CLIENT_ALLOWLIST_ONLY' and t['terminal_state'] in TERMINALS,'TER enum')
    hx(t['manifest_sha256']); hx(t['policy_sha256'])
    for k in ART: nullable(hx,t[k])
    for k in CLOCK+['slot_index','invocation_instant','T_d','created']: nullable(integer,t[k])
    for k in NUMS: nullable(dec,t[k])
    integer(t['lock_clock_at']); v12a_schema(t['V12a_evidence'])
    if t['V12a_evidence']['config_sha256'] is None: require(t['V12a']['result']=='FAIL','unreadable config must fail V12a')
    if t['origin']=='SCHEDULED': require(t['injection'] is None,'scheduled injection fields')
    else: injection_schema(t['injection'])
    if t['cycle_id'] is not None:
        require(type(t['cycle_id']) is list and len(t['cycle_id'])==2 and t['cycle_id'][0]=='BTC/USD','cycle_id'); integer(t['cycle_id'][1])
    if t['origin']=='SCHEDULED': require(all(t[k] is not None for k in ['slot_index','cycle_id','T_d','invocation_instant']),'scheduled identity missing')
    else: require(t['slot_index'] is None and t['cycle_id'] is None,'injected occupies slot')
    require(t['signal'] in (None,'BUY','EXIT','HOLD') and t['mapping'] in (None,'PROPOSAL','HOLD','NO_ACTION','NO_ACTION (BLOCKED_OPEN_ORDER)'),'signal/mapping enum')
    for k in V+Q:
        c=t[k]; keys(c,['result','reason']); require((c['result'] in ('PASS','FAIL') and c['reason'] is None) or (c['result']=='NOT_EVALUATED' and c['reason'] in REASONS),'check '+k)
    for prefix in ('bars','quote'):
        r=t[prefix+'_request']; hashes=[t[prefix+'_sha256'],t[prefix+'_headers_sha256']]
        if r is None:
            require(hashes==[None,None] or (t['origin']=='INJECTED' and prefix=='quote' and hashes[1] is None),'unissued has artifact'); continue
        keys(r,['url','sent_at','received_at','outcome']); string(r['url']); integer(r['sent_at'])
        if r['outcome']=='RESPONSE': integer(r['received_at']); require(all(hashes),'response missing artifact')
        elif r['outcome']=='NO_RESPONSE': require(r['received_at'] is None and hashes==[None,None],'NO_RESPONSE presence')
        else: raise ValueError('request outcome')
    for k in ARRAYS: arr(t[k])
    for b in t['completed_bars']+t['excluded_bars']:
        keys(b,['t',*BAR_FIELDS,'zero_volume']); nullable(integer,b['t']); require(b['zero_volume'] in (None,'TRUE','FALSE'),'zero_volume');
        for k in BAR_FIELDS: nullable(dec,b[k])
    for b in t['used_bars']:
        keys(b,['t','state','observation_count']); integer(b['t']); require(integer(b['observation_count'])>0 and b['state'] in ('BASELINED','PENDING','CONFIRMED'),'used bar state/count')
    for b in t['bar_store_transitions']:
        keys(b,['t','event','old','new','state','observation_count']); integer(b['t']); nullable(integer,b['observation_count']); require(b['event'] in ('BASELINED','OBSERVED','SOURCE_REVISION','CONFIRMED','DISAPPEARED','DUPLICATE_COLLAPSED'),'transition event'); require(b['state'] in (None,'BASELINED','PENDING','CONFIRMED'),'transition state')
        for k in ('old','new'):
            if b[k] is not None:
                keys(b[k],BAR_FIELDS)
                for x in b[k].values(): dec(x)
    if t['displayed_sizes'] is not None:
        keys(t['displayed_sizes'],['bs','as']); [nullable(dec,x) for x in t['displayed_sizes'].values()]
    if t['proposal'] is not None: proposal_schema(t['proposal'])
    if t['origin']=='INJECTED': injected_presence(t)
    else:
        qr=t['quote_request']; require((t['displayed_sizes'] is not None)==(qr is not None and qr['outcome']=='RESPONSE'),'displayed sizes presence')
    # Presence rules are schema checks, not evidence of the reported outcomes.
    if t['origin']=='SCHEDULED':
        br,qr=t['bars_request'],t['quote_request']; v12a=t['V12a']['result']; v12b=t['V12b']['result']
        def all_ne(names,reason): return all(t[k]==check(None,reason) for k in names)
        def empty_decisions(): return all(t[k] is None for k in NUMS+['signal','mapping','proposal','created']) and not t['rule_results'] and not t['used_bars']
        if v12a=='FAIL':
            require(br is None and qr is None and all(t[k] is None for k in ART+CLOCK) and all(not t[k] for k in ARRAYS) and empty_decisions() and t['displayed_sizes'] is None and all_ne(V[:-2]+['V12b']+Q,'V12A_FAILED') and t['terminal_state']=='BOUNDARY_FAIL','V12a failure presence')
        else:
            require(v12a=='PASS' and br is not None,'V12a/request presence'); require(t['t_send']==br['sent_at'] and t['t_recv']==br['received_at'],'bars clock/request mismatch')
            if br['outcome']=='NO_RESPONSE':
                require(qr is None and all(t[k] is None for k in ART+CLOCK[1:]) and all(not t[k] for k in ARRAYS) and empty_decisions() and t['displayed_sizes'] is None and all_ne(V[:-2]+['V12b']+Q,'FETCH_FAILED') and t['terminal_state']==no_dec('FETCH_FAILED'),'bars NO_RESPONSE presence')
            elif v12b=='FAIL':
                require(qr is None and all(not t[k] for k in ARRAYS) and empty_decisions() and t['displayed_sizes'] is None and all_ne(V[:-2]+Q,'V12B_FAILED') and t['terminal_state']=='BOUNDARY_FAIL','V12b failure presence')
            else:
                require(v12b=='PASS' and qr is not None,'V12b/quote request presence')
                require(all(t[k]['result'] in ('PASS','FAIL') for k in V[:2]),'V1/V2 must evaluate')
                dep=any(t[k]['result']=='FAIL' for k in V[:2]); require(all_ne(V[2:11],'DATA_INVALID') if dep else all(t[k]['result'] in ('PASS','FAIL') for k in V[2:11]),'V1/V2 dependency presence')
                vf=any(t[k]['result']=='FAIL' for k in V[:11]); term=t['terminal_state']
                if vf: require(empty_decisions() and all_ne(Q,'DATA_INVALID') and term.startswith('NO_DECISION ('),'V failure presence')
                else:
                    require(all(t[k] is not None for k in NUMS+['signal','mapping']) and len(t['used_bars'])==51,'valid data computed fields')
                    if term in ('HOLD','NO_ACTION'): require(t['proposal'] is None and t['created'] is None and not t['rule_results'] and all_ne(Q,'NO_PROPOSAL'),'no proposal presence')
                    elif term==no_dec('QUOTE_INVALID'): require(t['proposal'] is None and t['created'] is None and not t['rule_results'] and all(t[k]['result'] in ('PASS','FAIL') for k in Q) and any(t[k]['result']=='FAIL' for k in Q),'quote invalid presence')
                    elif term in ('REJECTED','SHADOW_EXPIRED'): require(t['proposal'] is not None and t['created'] is not None and t['rule_results'] and all(t[k]['result']=='PASS' for k in Q),'proposal presence')
                    else: raise ValueError('unexpected terminal for valid data')
    seen=set()
    for r in t['rule_results']:
        keys(r,['rule','result']); require(r['rule'] in RULES and r['rule'] not in seen and r['result'] in ('PASS','FAIL'),'rule result'); seen.add(r['rule'])

def v12a_schema(e):
    keys(e,['env_credential_names','config_sha256','client_allowlist'])
    nullable(hx,e['config_sha256'])
    for k in ('env_credential_names','client_allowlist'):
        for x in arr(e[k]): string(x)
    require(all(x.upper().startswith(('APCA_','ALPACA_')) for x in e['env_credential_names']),'nonmatching credential name')

def injection_schema(e):
    keys(e,['plan_sha256','fixture_sha256','intended_rule']); hx(e['plan_sha256']); hx(e['fixture_sha256']); require(e['intended_rule'] in RULES,'intended rule')

def injected_presence(t):
    require(all(t[k] is None for k in CLOCK+NUMS+['slot_index','cycle_id','bars_request','quote_request','bars_sha256','bars_headers_sha256','quote_headers_sha256','signal','mapping']), 'injected null fields')
    require(all(not t[k] for k in ARRAYS if k!='rule_results'),'injected bar collections')
    integer(t['T_d']); integer(t['invocation_instant'])
    v=t['V12a']['result']; require(v in ('PASS','FAIL'),'injected V12a')
    require(all(t[k]==check(None,'V12A_FAILED' if v=='FAIL' else 'INJECTED') for k in V[:-2]+['V12b']),'injected V presence')
    if v=='FAIL':
        require(t['terminal_state']=='BOUNDARY_FAIL' and all(t[k] is None for k in ('quote_sha256','displayed_sizes','created','proposal')) and not t['rule_results'] and all(t[k]==check(None,'V12A_FAILED') for k in Q),'injected boundary path')
    else:
        hx(t['quote_sha256']); require(t['displayed_sizes'] is not None,'injected sizes'); require(all(t[k]['result'] in ('PASS','FAIL') for k in Q),'injected Q')
        if any(t[k]['result']=='FAIL' for k in Q): require(t['terminal_state']==no_dec('QUOTE_INVALID') and t['created'] is None and t['proposal'] is None and not t['rule_results'],'injected invalid quote')
        else: require(t['terminal_state'] in ('REJECTED','SHADOW_EXPIRED') and t['created'] is not None and t['proposal'] is not None and t['rule_results'],'injected proposal path')

def record_schema(r):
    keys(r,['seq','prev_hash','type','body','hash']); safeint(r['seq']); nullable(hx,r['prev_hash']); hx(r['hash']); typ=r['type']; b=r['body']
    if typ in ('CYCLE','INJECTION'):
        ter_schema(b); require(b['origin']==('SCHEDULED' if typ=='CYCLE' else 'INJECTED'),'record/origin mismatch'); return
    require(typ in BODIES,'unknown record type'); keys(b,BODIES[typ].split())
    for k,x in b.items():
        if k.endswith('sha256'): hx(x)
        elif k in ('slot_index','old_process_id','invocation_instant','instant'): integer(x)
    if typ=='GENESIS': require(b['experiment_id']=='SL-PT-001','experiment id'); hash_map(b['frozen_set_hashes'])
    if typ=='INJECTION_ABORTED': require(b['result']=='INJECTION_ABORTED','abort result'); nullable(proposal_schema,b['proposal'])

def manifest_schema(m):
    keys(m,MANIFEST); hash_map(m['frozen_set_hashes']); require(m['instrument']=='BTC/USD','instrument'); require((integer(m['T_d0'])-60*NS)%STEP==0,'manifest off grid'); require(safeint(m['declared_slots'])>=30,'declared_slots <30'); require(dec(m['opening_cash'])==500,'opening cash');
    for k in MANIFEST:
        if k.endswith('sha256') or k=='prev_chain_head': hx(m[k])

class Git:
    def __init__(self,path,commit,root):
        self.path=path; self.root=root.strip('/'); self.env={k:v for k,v in os.environ.items() if not k.startswith('GIT_')}; self.env.update(GIT_OPTIONAL_LOCKS='0',GIT_NO_LAZY_FETCH='1',GIT_ALLOW_PROTOCOL='',GIT_TERMINAL_PROMPT='0',GIT_NO_REPLACE_OBJECTS='1',GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull)
        require(not self.root.startswith('-') and '..' not in self.root.split('/'),'invalid evidence root')
        self.commit=self.git('rev-parse','--verify','--end-of-options',commit+'^{commit}').decode().strip(); self.files={}
        for entry in self.git('ls-tree','-r','-z',self.commit).split(b'\0'):
            if not entry: continue
            meta,name=entry.split(b'\t',1); mode,typ,oid=meta.decode().split(); name=name.decode('utf-8')
            if typ=='blob' and mode in ('100644','100755'): self.files[name]=oid
    def git(self,*args):
        p=subprocess.run(['git','--no-optional-locks','-c','core.fsmonitor=false','-C',self.path,*args],env=self.env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
        require(p.returncode==0,'local git error: '+p.stderr.decode(errors='replace').strip()); return p.stdout
    def full(self,p): return self.root+'/'+p if self.root else p
    def read(self,p,absolute=False):
        name=p if absolute else self.full(p); require(name in self.files,'missing committed file '+name); return self.git('cat-file','blob',self.files[name])
    def list(self,p):
        prefix=self.full(p).rstrip('/')+'/'; offset=len(self.root)+1 if self.root else 0
        return sorted(x[offset:] for x in self.files if x.startswith(prefix))

def stamp(s):
    require(type(s) is str,'timestamp type'); m=re.fullmatch(r'(\d{4}-\d\d-\d\d)T(\d\d):(\d\d):(\d\d)(?:\.(\d{1,9}))?(Z|[+-]\d\d:\d\d)',s); require(m,'timestamp syntax'); d,h,mi,se,frac,z=m.groups(); hh,mm,ss=map(int,(h,mi,se)); base=dt.datetime.fromisoformat(d).replace(hour=hh,minute=mm,second=ss); off=0
    if z!='Z':
        zh,zm=map(int,z[1:].split(':')); require(zh<24 and zm<60,'timestamp offset'); off=(zh*3600+zm*60)*(1 if z[0]=='+' else -1)
    return (calendar.timegm(base.timetuple())-off)*NS+int((frac or '').ljust(9,'0'))
def headers(b):
    lines=b.decode('iso-8859-1').split('\r\n'); require(lines[-2:]==['',''],'header block terminator'); m=re.fullmatch(r'HTTP/\d(?:\.\d)? (\d{3})(?: .*)?',lines[0]); require(m,'missing HTTP status line'); dates=[]; encodings=[]
    for line in lines[1:-2]:
        require(':' in line,'malformed header'); k,v=line.split(':',1)
        if k.lower()=='date': dates.append(v.strip())
        if k.lower()=='content-encoding': encodings.append(v.strip().lower())
    d=None
    if len(dates)==1:
        try:
            match=re.fullmatch(r'(Mon|Tue|Wed|Thu|Fri|Sat|Sun), (\d{2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4}) (\d{2}):(\d{2}):(\d{2}) GMT',dates[0]); require(match,'invalid IMF-fixdate'); weekday,day,month,year,hour,minute,second=match.groups(); months='Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(); t=dt.datetime(int(year),months.index(month)+1,int(day),int(hour),int(minute),int(second)); require('Mon Tue Wed Thu Fri Sat Sun'.split()[t.weekday()]==weekday,'incorrect date weekday'); d=calendar.timegm(t.timetuple())*NS
        except ValueError: pass
    return int(m.group(1)),d,all(x=='identity' for x in encodings)

def attempt(fn, default=None):
    try: return fn()
    except (ValueError,KeyError,TypeError,IndexError,ArithmeticError,AttributeError): return default

def token(x): require(type(x) is Token,'not original JSON numeric token'); return str(x)
def raw_num(x): return dec(token(x))
def nsstr(x): return None if x is None else str(x)
def bar_view(b,t):
    out={'t':nsstr(t)}; out.update({k:attempt(lambda:token(b[k])) for k in BAR_FIELDS}); v=attempt(lambda:raw_num(b['v'])); out['zero_volume']=None if v is None else ('TRUE' if v==0 else 'FALSE'); return out

def compare(actual,expected,path,diffs,numeric=False):
    if isinstance(expected,F):
        same=attempt(lambda:dec(actual)==expected,False)
    elif isinstance(expected,dict):
        if type(actual) is not dict: diffs.append({'field':path,'recorded':actual,'expected':expected}); return
        for k in sorted(set(actual)-set(expected)): diffs.append({'field':path+'.'+k,'recorded':actual[k],'error':'unexpected field'})
        for k,v in expected.items():
            if k not in actual: diffs.append({'field':path+'.'+k,'expected':v,'error':'missing field'})
            else: compare(actual[k],v,path+'.'+k,diffs)
        return
    elif isinstance(expected,list):
        if type(actual) is not list: diffs.append({'field':path,'recorded':actual,'expected':expected}); return
        if len(actual)!=len(expected): diffs.append({'field':path,'recorded_length':len(actual),'expected_length':len(expected)})
        for i,v in enumerate(expected[:len(actual)]): compare(actual[i],v,path+'['+str(i)+']',diffs)
        return
    else: same=actual==expected
    if not same: diffs.append({'field':path,'recorded':actual,'expected':expected})

def request_url(r,prefix,T):
    u=urlsplit(r['url']); require(u.scheme=='https' and u.netloc=='data.alpaca.markets' and not u.fragment,'request outside pinned host'); q=parse_qs(u.query,keep_blank_values=True,strict_parsing=True)
    if prefix=='bars':
        require(u.path=='/v1beta3/crypto/us/bars' and set(q)=={'symbols','timeframe','start','end','limit'} and all(len(x)==1 for x in q.values()),'bars URL shape'); require(q['symbols']==['BTC/USD'] and q['timeframe']==['5Min'] and q['limit']==['1000'],'bars request params'); require(stamp(q['start'][0])==T-360*NS-59*STEP and stamp(q['end'][0])==T,'bars request range'); require('.' not in q['start'][0] and '.' not in q['end'][0] and q['start'][0].endswith('Z') and q['end'][0].endswith('Z'),'bars request UTC seconds')
    else: require(u.path=='/v1beta3/crypto/us/latest/quotes' and q=={'symbols':['BTC/USD']},'quote URL params')

def reconstruct(t,m,artifact,store):
    """No TER check outcomes used as inputs. Recorded instants and request
    facts are necessary observations, not independent evidence of clock/egress.
    Returns expected fields, gaps and differences. Updates raw-derived store."""
    e={k:None for k in NUMS+CLOCK+['signal','mapping','proposal','created','displayed_sizes']}; e.update({k:[] for k in ARRAYS}); gaps=[]; diffs=[]
    T=integer(t['T_d']); invocation=integer(t['invocation_instant']); exp=T-360*NS
    def setchecks(names,b,reason=None):
        for k in names:e[k]=check(b,reason)
    def finish(terminal):
        e['terminal_state']=terminal
        lock=integer(t['lock_clock_at'])
        if not lock<T+STEP or (terminal=='SHADOW_EXPIRED' and lock<T+180*NS): diffs.append({'field':'lock_clock_at','recorded':str(lock),'expected':'append begins before next slot; expiry at or after ceiling'})
        for k,v in e.items(): compare(t[k],v,k,diffs)
        return e,gaps,diffs
    br=t['bars_request']; qr=t['quote_request']
    boundary=boundary_check(t,artifact,gaps)
    e['V12a']=check(boundary)
    if not boundary:
        setchecks(V[:-2]+['V12b']+Q,None,'V12A_FAILED')
        return finish('BOUNDARY_FAIL')
    require(br is not None,'bars omitted after V12a pass')
    for prefix,r in [('bars',br),('quote',qr)]:
        if r is not None:
            try: request_url(r,prefix,T); require(integer(r['sent_at'])>=invocation,'request before invocation');
            except ValueError as exc: diffs.append({'field':prefix+'_request','error':str(exc)})
    e['t_send']=br['sent_at']; e['t_recv']=br['received_at']
    if br['outcome']=='NO_RESPONSE':
        if qr is not None: diffs.append({'field':'quote_request','expected':None,'recorded':qr})
        setchecks(V[:-2]+['V12b']+Q,None,'FETCH_FAILED'); return finish(no_dec('FETCH_FAILED'))
    bs,D,benc=headers(artifact(t['bars_headers_sha256'])); send,recv=map(integer,(br['sent_at'],br['received_at'])); e['D']=nsstr(D)
    lo=None if D is None else D-recv; hi=None if D is None else D+NS-send; e['θ_low']=nsstr(lo); e['θ_high']=nsstr(hi)
    clock=D is not None and 0<=recv-send<3*NS and lo>=-2*NS and hi<=2*NS; e['V12b']=check(clock)
    if not clock:
        if qr is not None: diffs.append({'field':'quote_request','expected':None,'recorded':qr})
        setchecks(V[:-2]+Q,None,'V12B_FAILED'); return finish('BOUNDARY_FAIL')
    require(qr is not None,'quote request omitted after V12b pass')
    require(integer(qr['sent_at'])>=recv,'quote issued before bars headers')
    raw=attempt(lambda:load(artifact(t['bars_sha256']),True)); qraw=None; qs=None; quote=None; qenc=True
    if qr['outcome']=='RESPONSE':
        qs,_,qenc=headers(artifact(t['quote_headers_sha256'])); qraw=attempt(lambda:load(artifact(t['quote_sha256']),True)); quote=attempt(lambda:qraw['quotes']['BTC/USD'])
        require(integer(qr['received_at'])>=integer(qr['sent_at']),'quote receipt before send')
    qsymbols=attempt(lambda:qraw['quotes']); wrong_quote=isinstance(qsymbols,dict) and set(qsymbols)!={'BTC/USD'}
    if qr['outcome']=='RESPONSE': e['displayed_sizes']=sizes_for(quote)
    bars=attempt(lambda:raw['bars']['BTC/USD']); shape=isinstance(raw,dict) and isinstance(raw.get('bars'),dict) and set(raw['bars'])=={'BTC/USD'} and type(bars) is list
    required=shape and 'next_page_token' in raw and all(isinstance(b,dict) and set(('t',*BAR_FIELDS))<=set(b) for b in bars)
    v1=bs==200 and benc and qenc and shape and required and not wrong_quote; v2= isinstance(raw,dict) and 'next_page_token' in raw and raw['next_page_token'] is None
    e['V1']=check(v1); e['V2']=check(v2)
    if not(v1 and v2):
        setchecks(V[2:11]+Q,None,'DATA_INVALID'); return finish(no_dec(('INCOMPLETE_RESPONSE' if shape and not required and bs==200 and benc and qenc and not wrong_quote else 'FETCH_FAILED') if not v1 else 'INCOMPLETE_RESPONSE'))
    unique={}; times=[]; v3=True; v4=True; v9=True; duplicate_notes=[]
    for b in bars:
        tt=attempt(lambda:stamp(b['t'])); v3 &= tt is not None and tt%STEP==0
        vals=attempt(lambda:{k:raw_num(b[k]) for k in BAR_FIELDS}); valid=vals is not None and all(vals[k]>0 for k in ('o','h','l','c','vw')) and vals['v']>=0 and vals['n']>=0 and vals['n'].denominator==1; v9 &= valid
        if tt is None: continue
        if tt in unique:
            if b.raw==unique[tt].raw: duplicate_notes.append(dict(t=str(tt),event='DUPLICATE_COLLAPSED',old=None,new=None,state=None,observation_count=None)); continue
            v4=False; continue
        unique[tt]=b; times.append(tt)
    complete={tt:unique[tt] for tt in times if tt+360*NS<=T}; excluded=[tt for tt in times if tt not in complete]
    e['completed_bars']=[bar_view(complete[tt],tt) for tt in times if tt in complete]; e['excluded_bars']=[bar_view(unique[tt],tt) for tt in excluded]; e['bar_store_transitions']=duplicate_notes
    window=list(range(exp-50*STEP,exp+1,STEP)); v7=bool(complete) and max(complete)==exp; v8=all(tt in complete for tt in window); v10=len(complete)>=51
    if v3 and v4 and v9:
        for tt,b in sorted(complete.items()):
            new={k:token(b[k]) for k in BAR_FIELDS}; old_entry=store.get(tt); old=old_entry['accepted'] if old_entry else None
            if old_entry is None: entry=dict(accepted=new,pending=None,state='BASELINED',count=1); event='BASELINED'
            elif old_entry['state']=='PENDING':
                if new==old_entry['pending']: entry=dict(accepted=new,pending=None,state='CONFIRMED',count=2); event='CONFIRMED'
                else: entry=dict(old_entry,pending=new); event='SOURCE_REVISION'; old=old_entry['pending']
            elif new==old: entry=dict(old_entry,count=old_entry['count']+1); event='OBSERVED'
            else: entry=dict(old_entry,pending=new,state='PENDING'); event='SOURCE_REVISION'
            store[tt]=entry; e['bar_store_transitions'].append(dict(t=str(tt),event=event,old=old,new=new,state=entry['state'],observation_count=str(entry['count'])))
        for tt,entry in sorted(store.items()):
            if exp-59*STEP<=tt<=exp and tt not in complete and entry['state']!='PENDING': e['bar_store_transitions'].append(dict(t=str(tt),event='DISAPPEARED',old=entry['accepted'],new=None,state=entry['state'],observation_count=str(entry['count'])))
    else: e['bar_store_transitions']=[]  # D-6: no observation from invalid set
    v11=not any(store.get(tt,{}).get('state')=='PENDING' for tt in window)
    for k,b in zip(V[2:11],[v3,v4,True,True,v7,v8,v9,v10,v11]): e[k]=check(b)
    fail=next((k for k in V[:11] if e[k]['result']=='FAIL'),None)
    if fail:
        setchecks(Q,None,'DATA_INVALID'); return finish(no_dec(dict(V3='MALFORMED_VALUE',V4='DATA_CONFLICT',V7='STALE_SERIES',V8='DATA_GAP',V9='MALFORMED_VALUE',V10='INSUFFICIENT_HISTORY',V11='SOURCE_REVISION')[fail]))
    closes=[raw_num(complete[tt]['c']) for tt in window]; a,b,c,d=sum(closes[-20:]),sum(closes[-50:]),sum(closes[-21:-1]),sum(closes[:-1]); dk=5*a-2*b; dp=5*c-2*d
    e.update(dict(zip(NUMS,[a,b,c,d,dp,dk]))); e['used_bars']=[dict(t=str(tt),state=store[tt]['state'],observation_count=str(store[tt]['count'])) for tt in window]
    signal='BUY' if dp<=0<dk else ('EXIT' if dp>=0>dk else 'HOLD'); mapping={'BUY':'PROPOSAL','EXIT':'NO_ACTION','HOLD':'HOLD'}[signal]; e.update(signal=signal,mapping=mapping)
    if mapping!='PROPOSAL': setchecks(Q,None,'NO_PROPOSAL'); return finish(mapping)
    qp,values=quote_checks(quote,qs==200 and qenc)
    for k,v in zip(Q,qp): e[k]=check(v)
    if not all(qp): return finish(no_dec('QUOTE_INVALID'))
    created=integer(t['created']); e['created']=str(created); require(created>=integer(qr['received_at']) and created>=T,'checkpoint before data or slot')
    terminal,proposal,rules=buy(values,T,created,m['instrument'],dec(m['opening_cash']),F(0),F(0),F(0),[])
    e['proposal']=proposal; e['rule_results']=rules
    return finish(terminal)


def boundary_check(t,artifact,gaps):
    e=t['V12a_evidence']; h=e['config_sha256']; allow=e['client_allowlist']
    if h is None or e['env_credential_names'] or allow!=['data.alpaca.markets']: return False
    # On a recorded failure config bytes are deliberately not retained. The
    # hash alone cannot distinguish valid config from forbidden keys.
    if t['V12a']['result']=='FAIL':
        gaps.append('V12a failure config contents withheld; independently indeterminate')
        return False
    cfg=attempt(lambda:load(artifact(h))); return type(cfg) is dict and set(cfg)=={'client_allowlist'} and cfg['client_allowlist']==allow


def sizes_for(quote): return {k:attempt(lambda:token(quote[k])) for k in ('bs','as')}

def quote_checks(quote,available=True):
    bid=attempt(lambda:raw_num(quote['bp'])); ask=attempt(lambda:raw_num(quote['ap'])); bs=attempt(lambda:raw_num(quote['bs'])); az=attempt(lambda:raw_num(quote['as'])); qt=attempt(lambda:stamp(quote['t']))
    return [available and bid is not None and bid>0,available and ask is not None and ask>0,available and bid is not None and ask is not None and ask>=bid,available and bs is not None and az is not None and min(bs,az)>=0,available and qt is not None],(bid,ask,qt)


def buy(values,T,created,instrument,cash,btc,reserved,reserved_btc,opened):
    bid,ask,qt=values; pi,qi,minimum,fee=F(1),F('0.0001'),F('0.0001'),F('0.0025')
    available=cash-reserved; budget=min(F(150),available); L=(ask//pi)*pi; require(L>0,'rounded L=0: sizing undefined')
    quantity=(budget/(L*(1+fee))//qi)*qi; cost=quantity*L*(1+fee); R=F(-(-cost*100//1),100)
    rounding=dict(zip(ROUND,[bid,ask,pi,qi,minimum,fee,cash,reserved,available,budget,btc,reserved_btc])); proposal=dict(instrument=instrument,side='BUY',order_type='LIMIT',L=L,q=quantity,R=R,rounding_inputs=rounding)
    mid=(bid+ask)/2; results={'R1':instrument=='BTC/USD','R2':True,'R3':True,'R4':0<=created-qt<=15*NS,'R5':abs(L-mid)<=F('0.01')*mid,'R6':R<=available,'R7':R<=150,'R8':btc*bid+R<=300,'R10':quantity>=minimum and quantity%qi==0 and L%pi==0,'R11':not opened,'R12':cash+btc*bid>=450,'R13':T<=created<=T+30*NS,'R16':not opened}
    return 'SHADOW_EXPIRED' if all(results.values()) else 'REJECTED',proposal,[dict(rule=k,result='PASS' if v else 'FAIL') for k,v in results.items()]


def fixture_schema(f):
    keys(f,'instrument quote_body_hex T_d created shadow_cash shadow_btc shadow_reserved shadow_reserved_btc open_authorizations policy_sha256'.split()); string(f['instrument']); hx(f['policy_sha256']); T=integer(f['T_d']); created=integer(f['created']); require(created>=T,'fixture created before T_d'); require(re.fullmatch(r'(?:[0-9a-f]{2})*',string(f['quote_body_hex'])) is not None,'fixture quote hex')
    cash,btc,reserved,rb=(dec(f[k]) for k in ('shadow_cash','shadow_btc','shadow_reserved','shadow_reserved_btc')); require(cash>=0 and 0<=reserved<=cash and 0<=rb<=btc and cash*100%1==0 and reserved*100%1==0,'fixture ledger')
    for x in arr(f['open_authorizations']): string(x)
    return bytes.fromhex(f['quote_body_hex'])


def injection_replay(t,f,artifact):
    body=fixture_schema(f); gaps=[]; diffs=[]; e={k:None for k in ['created','proposal','displayed_sizes','quote_sha256']}; e['rule_results']=[]
    e['T_d']=f['T_d']; e['policy_sha256']=f['policy_sha256']; boundary=boundary_check(t,artifact,gaps); e['V12a']=check(boundary)
    for k in V[:-2]+['V12b']: e[k]=check(None,'INJECTED' if boundary else 'V12A_FAILED')
    if not boundary:
        e['terminal_state']='BOUNDARY_FAIL'
        for k in Q: e[k]=check(None,'V12A_FAILED')
    else:
        e['quote_sha256']=sha(body); require(artifact(e['quote_sha256'])==body,'fixture quote artifact mismatch')
        raw=attempt(lambda:load(body,True)); quote=attempt(lambda:raw['quotes'][f['instrument']]); e['displayed_sizes']=sizes_for(quote); qp,vals=quote_checks(quote)
        for k,v in zip(Q,qp): e[k]=check(v)
        if not all(qp): e['terminal_state']=no_dec('QUOTE_INVALID')
        else:
            e['created']=f['created']; cash,btc,reserved,rb=(dec(f[k]) for k in ('shadow_cash','shadow_btc','shadow_reserved','shadow_reserved_btc')); require(btc<F('0.0001') and not f['open_authorizations'],'fixture not eligible constructed flat BUY')
            e['terminal_state'],e['proposal'],e['rule_results']=buy(vals,integer(f['T_d']),integer(f['created']),f['instrument'],cash,btc,reserved,rb,f['open_authorizations'])
    for k,v in e.items(): compare(t[k],v,k,diffs)
    return e,gaps,diffs

def audit(g,seed,custody):
    findings=[]; report={'commit':g.commit,'chain_head':None,'findings':findings,'manifests':[],'sample':[],'orphaned_artifacts':[],'attestation':{'V12a':'HARNESS-ATTESTED','lock_clock_at':'HARNESS-ATTESTED'},'off_grid':[],'invocation_mismatches':[],'limitations':[LIMITATION,'V12a and lock_clock_at: HARNESS-ATTESTED, conditional on observations; append completion/fsync not timestamped','Failed V12a configuration bytes withheld; some failures cannot be independently recomputed','Local commit does not establish remote push timing or no rewrites','Clock assumptions A-CLK/A-CLK2 and data-host UTC accuracy unverified','Venue increments and fee unverified; sizing conditional','FD-6 common-mode risk; founder hand cross-check required']}
    def finding(code,**kw): findings.append(dict(code=code,**kw))
    report['seed_sha256']=sha(seed.encode('utf-8'))
    try: require(sha(g.read(SPEC_PATH,absolute=True))==SPEC,'spec hash mismatch in audited commit')
    except ValueError as exc: finding('SPEC',detail=str(exc))
    manifests={}; invalid_manifests=set(); paths={}
    for p in g.list('runs'):
        if not p.endswith('.json'): continue
        b=g.read(p); h=sha(b); paths.setdefault(h,[]).append(p)
        try:
            m=load(b); manifests[h]=m if isinstance(m,dict) else {}; manifest_schema(m)
        except (ValueError,KeyError,TypeError,ArithmeticError) as exc:
            invalid_manifests.add(h); finding('MANIFEST_SCHEMA',manifest=h,path=p,detail=str(exc)); manifests.setdefault(h,{})
    for h,ps in paths.items():
        if len(ps)>1: finding('DUPLICATE_MANIFEST_FILE',manifest=h,paths=ps)
    policy=None; ph=None
    try:
        pb=g.read('policy/P-0.2.json'); ph=sha(pb); policy=load(pb); require(policy==POLICY,'policy differs from contract/frozen values')
    except (ValueError,KeyError,TypeError) as exc: finding('POLICY',detail=str(exc)); policy=None
    refs=set(); cached={}; bad_art=set()
    def artifact(h):
        hx(h)
        if h not in cached:
            b=g.read('artifacts/'+h); require(sha(b)==h,'artifact SHA-256 mismatch '+h); cached[h]=b
        return cached[h]
    records=[]; chain_good=True; prev=None; genesis=None; active=None; closed=False; opens=collections.defaultdict(list); closes=collections.defaultdict(list); groups=collections.defaultdict(list); samples=[]; injection_records=[]
    try: data=g.read('chain/events.jsonl')
    except ValueError as exc: data=b''; finding('CHAIN_MISSING',detail=str(exc)); chain_good=False
    lines=data.splitlines(keepends=True)
    if not lines: finding('CHAIN_EMPTY'); chain_good=False
    for idx,line in enumerate(lines):
        r=None; valid=chain_good
        try:
            require(line.endswith(b'\n') and not line.endswith(b'\r\n'),'chain line not LF-terminated'); r=load(line[:-1]);
            for test in (lambda:record_schema(r),lambda:require(r['seq']==idx,'seq not contiguous'),lambda:require(r['prev_hash']==prev,'prev_hash mismatch'),lambda:require((idx==0)==(r['type']=='GENESIS'),'GENESIS position'),lambda:require(sha(jcs({k:v for k,v in r.items() if k!='hash'}).encode('utf-8'))==r['hash'],'record hash mismatch')):
                try: test()
                except (ValueError,KeyError,TypeError,ArithmeticError,AttributeError,IndexError) as exc:
                    valid=False; chain_good=False; finding('CHAIN_INTEGRITY',line=idx+1,detail=str(exc))
        except (ValueError,KeyError,TypeError,ArithmeticError,AttributeError) as exc:
            valid=False; chain_good=False; finding('CHAIN_INTEGRITY',line=idx+1,detail=str(exc))
            if r is None: r=attempt(lambda:load(line.rstrip(b'\r\n')))
        if not isinstance(r,dict): prev=None; continue
        prev=r.get('hash'); typ=r.get('type'); typ=typ if isinstance(typ,str) else '<invalid>'; b=r.get('body'); b=b if isinstance(b,dict) else {}; row={'record':r,'body':b,'line':idx+1,'valid':valid,'type':typ,'seq':r.get('seq',idx),'manifest':None}; records.append(row)
        if typ=='GENESIS': genesis=b.get('frozen_set_hashes')
        elif typ=='RUN_OPEN':
            h=b.get('manifest_sha256'); h=h if isinstance(h,str) else '<invalid>'; opens[h].append(row)
            if active is not None and not closed: finding('RUN_OPEN_WHILE_OPEN',manifest=h,previous=active); invalid_manifests.update((h,active))
            active=h; closed=False; row['manifest']=h
            if h in manifests and h not in invalid_manifests:
                m=manifests[h]
                if m['prev_chain_head']!=r.get('prev_hash'): finding('MANIFEST_PREV_HEAD',manifest=h); invalid_manifests.add(h)
                if m['frozen_set_hashes']!=genesis: finding('FROZEN_SET_MISMATCH',manifest=h); invalid_manifests.add(h)
        else:
            row['manifest']=b.get('manifest_sha256') if typ in ('CYCLE','INJECTION') else active
            h=row['manifest']; h=h if isinstance(h,str) else None; row['manifest']=h
            if typ in ('CYCLE','INJECTION') and (active is None or h!=active): finding('RUN_ATTRIBUTION',seq=row['seq'],manifest=h,active=active); row['valid']=False
            if typ in ('CYCLE','CYCLE_OVERRUN','CONCURRENT_INVOCATION','INJECTION','INJECTION_ABORTED') and closed: finding('RECORD_AFTER_RUN_CLOSE',seq=row['seq'],manifest=h); row['valid']=False
            if typ=='RUN_CLOSE':
                if h is None or closed: finding('RUN_CLOSE_WITHOUT_OPEN',seq=row['seq']); row['valid']=False
                closes[h].append(row); closed=True
            if typ=='CYCLE' and b.get('origin')=='SCHEDULED': samples.append(row)
            if typ in ('CYCLE','INJECTION','INJECTION_ABORTED','CYCLE_OVERRUN','CONCURRENT_INVOCATION','RUN_STOPPED') and active is None: row['valid']=False; finding('NO_OPEN_RUN',seq=row['seq'],type=typ)
            if typ=='INJECTION': injection_records.append(row)
            if typ in ('CYCLE','CYCLE_OVERRUN','CONCURRENT_INVOCATION','OFF_RUN'): groups[h].append(row)
            if typ in ('CYCLE','INJECTION'):
                for k in ART+['V12a_config']:
                    x=attempt(lambda:b['V12a_evidence']['config_sha256'] if b['V12a']['result']=='PASS' else None) if k=='V12a_config' else b.get(k)
                    if isinstance(x,str) and HASH.fullmatch(x):
                        refs.add(x)
                        try: artifact(x)
                        except ValueError as exc: bad_art.add(x); finding('ARTIFACT_INTEGRITY',seq=row['seq'],field=k,detail=str(exc)); row['artifact_bad']=True
    # Verify order against all later-slot records, including anomalies.
    for h,rr in groups.items():
        highest=-1
        for row in rr:
            if row['type']=='OFF_RUN': continue
            i=attempt(lambda:integer(row['body']['slot_index']))
            if i is None: continue
            if row['type']=='CYCLE' and i<highest:
                row['order_bad']=True; finding('LATE_CHAIN_ORDER',manifest=h,seq=row['seq'],slot=i)
            highest=max(highest,i)
    report['chain_head']=prev; report['chain_integrity']=chain_good
    for h in sorted(set(opens)-set(manifests)): finding('RUN_OPEN_WITHOUT_MANIFEST',manifest=h)
    for h in sorted(set(manifests)-set(opens)): finding('MANIFEST_WITHOUT_RUN_OPEN',manifest=h)
    for h,rr in opens.items():
        if len(rr)!=1: finding('RUN_OPEN_COUNT',manifest=h,count=len(rr)); invalid_manifests.add(h)
    for h,rr in closes.items():
        if len(rr)!=1: finding('RUN_CLOSE_COUNT',manifest=h,count=len(rr)); invalid_manifests.add(h)
    for h in set(opens)-set(closes): finding('RUN_NOT_CLOSED',manifest=h); invalid_manifests.add(h)
    for p in g.list('artifacts'):
        name=p.split('/')[-1]
        if p!='artifacts/'+name or name not in refs: report['orphaned_artifacts'].append(p)
    for p in report['orphaned_artifacts']: finding('ORPHANED_ARTIFACT',path=p)
    # Every CYCLE is replayed in chain order, including non-sampled cycles.
    # An unresolved observation makes subsequent revision claims conditional.
    store={}; store_uncertain=False; cycle_ids=collections.defaultdict(set); replays={}
    for row in records:
        if row['type']!='CYCLE': continue
        b=row['body']; h=row['manifest']; seq=row['seq']; replay={'seq':seq,'manifest':h,'differences':[],'gaps':[],'recomputed_terminal':None}; replays[row['line']]=replay
        cid=b.get('cycle_id')
        if isinstance(cid,list) and len(cid)==2 and all(isinstance(x,str) for x in cid): cycle_ids[tuple(cid)].add(h)
        if not row['valid'] or h not in manifests or h in invalid_manifests or row.get('artifact_bad') or policy is None:
            replay['gaps'].append('invalid schema/chain/manifest/artifact or policy; no trusted replay'); store_uncertain=True; continue
        m=manifests[h]
        if m['policy_sha256']!=ph or b['policy_sha256']!=ph:
            replay['differences'].append({'field':'policy_sha256','expected':ph,'manifest':m['policy_sha256'],'recorded':b['policy_sha256']}); finding('RECONSTRUCTION_DIFFERENCE',seq=seq,differences=replay['differences']); store_uncertain=True; continue
        try:
            i=integer(b['slot_index']); T0=integer(m['T_d0']); T=T0+i*STEP; require(0<=i<m['declared_slots'] and integer(b['T_d'])==T and b['cycle_id']==['BTC/USD',str(T-360*NS)] and T<=integer(b['invocation_instant'])<T+STEP,'OFF_GRID');
            expected,gaps,diffs=reconstruct(b,m,artifact,store); replay.update(recomputed_terminal=expected['terminal_state'],differences=diffs,gaps=gaps,recomputed_signal=expected['signal'],recomputed_fields=expected)
            if row.get('order_bad'): diffs.append({'field':'chain_order','error':'CYCLE follows a later-slot record'})
            if store_uncertain: replay['gaps'].append('prior revision history unresolved')
            if any('fold semantics' in x or 'pagination' in x for x in gaps): store_uncertain=True
            if diffs: finding('RECONSTRUCTION_DIFFERENCE',seq=seq,differences=diffs)
            if replay['gaps']: finding('RECONSTRUCTION_GAP',seq=seq,gaps=replay['gaps'])
        except (ValueError,KeyError,TypeError,ArithmeticError,AttributeError,IndexError) as exc:
            replay['gaps'].append(str(exc)); finding('RECONSTRUCTION_UNRESOLVED',seq=seq,detail=str(exc)); store_uncertain=True
    duplicates={cid for cid,hs in cycle_ids.items() if len(hs)>1}
    for cid in sorted(duplicates): finding('CYCLE_ID_ACROSS_MANIFESTS',cycle_id=list(cid),manifests=sorted(str(x) for x in cycle_ids[cid]))
    total=0; strict_best=0; conditional_best=0; strict_no_action=collections.Counter(); conditional_no_action=collections.Counter()
    for h in sorted(set(manifests)|set(opens)):
        m=manifests.get(h,{}); out={'manifest_sha256':h,'paths':paths.get(h,[]),'slots':[],'run_length':0,'conditional_run_length':0,'declared_slots':m.get('declared_slots'),'invocation_mismatches':[]}; report['manifests'].append(out)
        if h not in manifests or not isinstance(m,dict) or type(m.get('declared_slots')) is not int or not isinstance(m.get('T_d0'),str):
            out['status']='INVALID_OR_MISSING_MANIFEST'; continue
        N=m['declared_slots']; T0=attempt(lambda:integer(m['T_d0']));
        if N<0 or T0 is None: out['status']='INVALID_MANIFEST'; continue
        total+=N; end=T0+N*STEP;
        if time.time_ns()<end: invalid_manifests.add(h); finding('RUN_NOT_ELAPSED',manifest=h)
        byslot=collections.defaultdict(list); off=[]; lines_by_slot=collections.defaultdict(list); remaining=[]; inv_bad=False
        def mismatch(**kw):
            obj=dict(manifest=h,**kw); out['invocation_mismatches'].append(obj); report['invocation_mismatches'].append(obj); finding('INVOCATION_MISMATCH',**obj)
        def owner(x): return (x-T0)//STEP if T0<=x<end else None
        for row in groups[h]:
            b=row['body']; typ=row['type']
            if typ=='OFF_RUN':
                off.append(row); x=attempt(lambda:integer(b['invocation_instant']));
                if x is None or owner(x) is not None: finding('OFF_RUN_IN_GRID',manifest=h,seq=row['seq']); row['valid']=False
                continue
            i=attempt(lambda:integer(b['slot_index'])); td=attempt(lambda:integer(b['T_d'])); iv=attempt(lambda:integer(b['invocation_instant'])); correct=i is not None and 0<=i<N
            if typ=='CONCURRENT_INVOCATION': correct=correct and iv is not None and owner(iv)==i
            if typ=='CYCLE':
                correct=correct and td==T0+i*STEP and b.get('cycle_id')==['BTC/USD',str(T0+i*STEP-360*NS)] and iv is not None and owner(iv)==i
            if not correct:
                obj=dict(manifest=h,seq=row['seq'],slot=b.get('slot_index'),type=typ); report['off_grid'].append(obj); finding('OFF_GRID',**obj)
                # An invalid record with identifiable slot still poisons that slot.
                if i is not None and 0<=i<N: row['valid']=False; byslot[i].append(row)
                continue
            byslot[i].append(row)
        try:
            log=g.read('chain/invocations/'+h+'.log')
            if closes[h]: require(sha(log)==closes[h][0]['body'].get('invocation_log_sha256'),'RUN_CLOSE invocation log hash mismatch')
            else: finding('RUN_NOT_CLOSED',manifest=h)
            for idx,line in enumerate(log.splitlines(keepends=True)):
                try:
                    require(line.endswith(b'\n') and not line.endswith(b'\r\n'),'invocation line not LF-terminated'); x,pid,wh=line[:-1].decode('utf-8').split('\t'); x=integer(x); require(integer(pid)>0,'pid'); hx(wh); require(wh==m.get('wrapper_sha256'),'wrapper hash mismatch'); item={'line':idx+1,'instant':x,'pid':pid,'used':False}; remaining.append(item); lines_by_slot[owner(x)].append(item)
                except (ValueError,TypeError) as exc: inv_bad=True; mismatch(line=idx+1,detail=str(exc))
        except (ValueError,KeyError,TypeError) as exc: inv_bad=True; finding('INVOCATION_LOG',manifest=h,detail=str(exc))
        try:
            require(hx(m['task_xml_sha256']),'task XML hash missing'); xml=g.read('chain/tasks/'+m['task_xml_sha256']+'.xml'); require(sha(xml)==m['task_xml_sha256'],'task XML hash mismatch');
            if closes[h]: require(closes[h][0]['body'].get('task_xml_sha256')==m['task_xml_sha256'],'RUN_CLOSE XML mismatch')
        except (ValueError,KeyError,TypeError) as exc: finding('TASK_XML',manifest=h,detail=str(exc)); invalid_manifests.add(h)
        # Exact invocation matching where instant exists; overrun only by slot.
        mismatched_slots=set()
        for row in off+[r for rr in byslot.values() for r in rr if r['type']!='CYCLE_OVERRUN']:
            b=row['body']; x=attempt(lambda:integer(b['invocation_instant'])); i=owner(x) if x is not None else None
            matches=[item for item in lines_by_slot[i] if not item['used'] and item['instant']==x]
            if matches: matches[0]['used']=True
            else: mismatch(seq=row['seq'],slot=i,detail='chain record without matching invocation'); mismatched_slots.add(i)
        for i,rr in byslot.items():
            for row in rr:
                if row['type']=='CYCLE_OVERRUN':
                    match=next((x for x in lines_by_slot[i] if not x['used']),None)
                    if match: match['used']=True
                    else: mismatch(seq=row['seq'],slot=i,detail='overrun without unmatched invocation'); mismatched_slots.add(i)
        for item in remaining:
            if item['used']: continue
            i=owner(item['instant']); rr=byslot[i] if i is not None else []; incomplete=i is not None and not any(r['type'] in ('CYCLE','CYCLE_OVERRUN') for r in rr) and not any(not r['valid'] for r in rr)
            if not incomplete: mismatch(line=item['line'],slot=i,detail='invocation without matching chain record'); mismatched_slots.add(i)
        streak=0; cstreak=0
        for i in range(N):
            rr=byslot[i]; cycles=[r for r in rr if r['type']=='CYCLE']; over=[r for r in rr if r['type']=='CYCLE_OVERRUN']; conc=[r for r in rr if r['type']=='CONCURRENT_INVOCATION']; T=T0+i*STEP; cid=['BTC/USD',str(T-360*NS)]; why=[]; c='NON-QUALIFYING'; conditional=c
            if any(not r['valid'] for r in rr): why.append('row 1 schema/hash/identity failure')
            elif over and cycles: c='CONFLICT'; why.append('row 2'); finding('SLOT_CONFLICT',manifest=h,slot=i)
            elif over: c='OVERRUN'; why.append('row 3')
            elif not cycles: c='INCOMPLETE' if lines_by_slot[i] else 'MISSING'; why.append('row 4' if c=='INCOMPLETE' else 'row 5'); finding(c,manifest=h,slot=i)
            elif len(cycles)>1: c='DUPLICATE'; why.append('row 6'); finding(c,manifest=h,slot=i)
            elif conc: why.append('row 7 concurrent invocation'); finding('CONCURRENT_INVOCATION',manifest=h,slot=i)
            else:
                row=cycles[0]; rp=replays.get(row['line'],{}); terminal=rp.get('recomputed_terminal'); gaps=rp.get('gaps',[]); diff=rp.get('differences',[])
                if diff or terminal not in ('HOLD','NO_ACTION','REJECTED','SHADOW_EXPIRED') or tuple(cid) in duplicates or inv_bad or i in mismatched_slots or h in invalid_manifests or h not in opens or not chain_good:
                    why.append('row 8 failed, unresolved or nonqualifying reconstruction/integrity')
                elif gaps: why.append('row 8 additional unresolved evidence')
                else:
                    c=conditional='QUALIFYING'; why.append('row 9; V12a and lock_clock_at HARNESS-ATTESTED');
                    if terminal=='NO_ACTION': strict_no_action[rp['recomputed_signal']]+=1; conditional_no_action[rp['recomputed_signal']]+=1
            if conditional!='QUALIFYING': conditional=c
            streak=streak+1 if c=='QUALIFYING' else 0; cstreak=cstreak+1 if conditional=='QUALIFYING' else 0; out['run_length']=max(out['run_length'],streak); out['conditional_run_length']=max(out['conditional_run_length'],cstreak)
            out['slots'].append(dict(slot_index=i,T_d=str(T),cycle_id=cid,classification=c,conditional_classification=conditional,reason=why,cycle_seq=[r['seq'] for r in cycles]))
        strict_best=max(strict_best,out['run_length']); conditional_best=max(conditional_best,out['conditional_run_length']); out['status']='AUDITED' if h not in invalid_manifests else 'INVALID_MANIFEST'
    for h,rr in groups.items():
        if h not in manifests:
            for row in rr: finding('UNATTRIBUTED_RECORD',manifest=h,seq=row['seq'])
    report['reconstructions']=[replays[k] for k in sorted(replays)]
    report['injections']=audit_injections(g,injection_records,records,manifests,artifact,ph,finding)
    local_count=report['injections']['locally_verified_intended_rule_rejections']
    report.update(denominator=total,run_length=strict_best,conditional_run_length=conditional_best,qualifying_no_action=dict(strict_no_action),M1_1_local_threshold_met=(strict_best>=30 and local_count>=5),M1_1='CONDITIONAL_ON_PUSH_PROVENANCE' if strict_best>=30 and local_count>=5 else 'NOT_MET',M1_1_met=None if strict_best>=30 and local_count>=5 else False)
    # Evidence population is all scheduled CYCLE records in the fixed manifests.
    scope=custody['scope']; eligible=[r for r in samples if r['manifest'] in scope['manifests']]
    seqs=[r['seq'] for r in eligible]; pop={'count':len(seqs),'first_seq':seqs[0] if seqs else None,'last_seq':seqs[-1] if seqs else None}
    custody_ok=scope['chain_head']==prev and scope['population']==pop and set(scope['manifests'])==set(manifests)==set(opens) and set(closes)==set(opens) and chain_good
    if not custody_ok: finding('SEED_SCOPE_MISMATCH',recorded=scope,computed_population=pop)
    report['custody']={**custody,'population_recomputed':pop,'local_scope_matches':custody_ok,'push_timing':'UNVERIFIED','seed_secrecy_entropy':'UNVERIFIED'}
    def rank(r): return (sha(b'SL-PT-001/FD-6/v2\0'+seed.encode('ascii')+b'\0'+str(r['seq']).encode('ascii')),r['seq'],r['line'])
    selected=sorted(eligible,key=rank)[:5] if custody_ok else []
    for row in selected:
        rp=replays.get(row['line'],{'gaps':['reconstruction unavailable'],'differences':[]}); report['sample'].append(dict(rank_sha256=rank(row)[0],line=row['line'],**rp))
    if len(selected)<5: finding('SAMPLE_SHORTFALL',available=len(selected),required=5)
    report['M1_6']='CONDITIONAL_ON_PUSH_PROVENANCE' if custody_ok and len(selected)==5 and not any(r['differences'] or r['gaps'] for r in report['sample']) else 'NOT_MET'
    report['M1_6_local_reconstruction_met']=(report['M1_6']=='CONDITIONAL_ON_PUSH_PROVENANCE')
    report['status']='FINDINGS' if findings else 'CONDITIONAL_ON_PUSH_PROVENANCE'
    return report

def history(g):
    # First-parent ordering gives a definite evidence lineage. Competing
    # commitment paths are also checked across all reachable ancestors.
    commits=g.git('rev-list','--first-parent','--reverse',g.commit).decode().splitlines()
    require(commits,'empty history')
    return commits


def snapshot(g,commit): return Git(g.path,commit,g.root)


def scope_schema(obj):
    keys(obj,['evidence_commit','chain_head','manifests','population']); require(re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}',string(obj['evidence_commit'])),'full evidence commit'); hx(obj['chain_head']); ms=arr(obj['manifests']); require(ms and len(ms)==len(set(ms)),'scope manifests'); [hx(x) for x in ms]
    pop=obj['population']; keys(pop,['count','first_seq','last_seq']); safeint(pop['count']); nullable(safeint,pop['first_seq']); nullable(safeint,pop['last_seq']); require((pop['first_seq'] is None)==(pop['last_seq'] is None)==(pop['count']==0),'population bounds'); return obj


def chain_bytes(g):
    p='chain/events.jsonl'
    return g.read(p) if g.full(p) in g.files else b''


def load_custody(path,commit,root,scope_id):
    tip=Git(path,commit,root); require(re.fullmatch(r'[A-Za-z0-9_-]+',scope_id),'invalid scope id'); base='audit-scopes/'+scope_id+'/'
    cp,sp,rp=(base+x for x in ('seed.sha256','scope.json','seed.txt'))
    commits=history(tip); seen={}; prior_chain=b''; scope=None; evidence=None; commitment=None; seed=None
    # Single fixed run-set audit, covering all manifests at evidence fixing.
    # Every additional commitment path in any reachable history is competing.
    commitment_versions=set()
    for c in tip.git('rev-list',tip.commit).decode().splitlines():
        snap=snapshot(tip,c)
        if snap.full(cp) in snap.files: commitment_versions.add(snap.files[snap.full(cp)])
        for p in snap.list('audit-scopes'):
            if p.endswith('/seed.sha256') and p!=cp:
                raise ValueError('competing seed commitment: '+p)
    require(len(commitment_versions)==1,'missing or multiple commitment versions in reachable history')
    for idx,c in enumerate(commits):
        g=snapshot(tip,c); current=chain_bytes(g)
        require(current.startswith(prior_chain),'chain history is not append-only on first-parent lineage'); prior_chain=current
        for p in (cp,sp,rp):
            oid=g.files.get(g.full(p))
            if p in seen: require(oid==seen[p][1],'custody file modified or deleted: '+p)
            elif oid is not None:
                seen[p]=(idx,oid,c)
                if p==cp:
                    commitment=g.read(cp).decode('ascii'); hx(commitment)
                elif p==sp:
                    require(cp in seen and seen[cp][0]<idx,'scope must follow commitment'); scope=scope_schema(load(g.read(sp))); require(scope['evidence_commit'] in commits[:idx],'evidence commit must precede scope'); require(commits.index(scope['evidence_commit'])>seen[cp][0],'evidence must follow seed commitment'); evidence=snapshot(tip,scope['evidence_commit']); require(chain_bytes(evidence)==current,'scope commit changes evidence chain')
                else:
                    require(sp in seen and seen[sp][0]<idx,'reveal must follow scope'); seed=g.read(rp).decode('ascii'); require(HASH.fullmatch(seed) and sha(seed.encode('ascii'))==commitment,'seed commitment mismatch')
        if scope is not None:
            def evidence_tree(x):
                return {p:x.files[x.full(p)] for d in ('chain','runs','artifacts','policy','injections') for p in x.list(d)}
            require(evidence_tree(g)==evidence_tree(evidence),'evidence substituted after fixing')
    require(len(seen)==3 and evidence is not None and seed is not None,'missing commitment, fixed scope or reveal')
    # Superseded seed is never read into output; only compare historical bytes.
    old=snapshot(tip,'07f43e0'); old_paths=[p for p in old.files if p.endswith('/SL-PT-001_FD6_Seed.txt') or p=='SL-PT-001_FD6_Seed.txt']; require(len(old_paths)==1,'superseded seed file unavailable or ambiguous'); old_bytes=old.read(old_paths[0],absolute=True); require(old_bytes.strip()!=seed.encode('ascii'),'superseded seed reused')
    require(tip.files.get(old_paths[0])==old.files[old_paths[0]],'superseded seed artifact not preserved unchanged')
    first=snapshot(tip,seen[cp][2]); require(first.read(base+'auditor.sha256').decode('ascii')==sha(open(__file__,'rb').read()),'auditor hash not committed by seed commitment')
    require(tip.files.get(tip.full(base+'auditor.sha256'))==first.files.get(first.full(base+'auditor.sha256')),'auditor hash record changed')
    for line in chain_bytes(first).splitlines():
        r=load(line); require(r.get('type') not in ('CYCLE','INJECTION'),'auditor hash commitment not pre-TER'); require(not(r.get('type')=='RUN_OPEN' and r.get('body',{}).get('manifest_sha256') in scope['manifests']),'seed commitment not before audited RUN_OPEN')
    # Manifest introduction must precede its RUN_OPEN locally. Wall-clock push
    # chronology is not inferred from local commit metadata.
    opened=set(); preceding=None
    for c in commits[:commits.index(evidence.commit)+1]:
        snap=snapshot(tip,c)
        for line in chain_bytes(snap).splitlines():
            rec=attempt(lambda:load(line))
            if not isinstance(rec,dict) or rec.get('type')!='RUN_OPEN': continue
            h=attempt(lambda:rec['body']['manifest_sha256'])
            if h not in scope['manifests'] or h in opened: continue
            require(preceding is not None and any(sha(preceding.read(p))==h for p in preceding.list('runs') if p.endswith('.json')),'manifest not committed strictly before RUN_OPEN'); opened.add(h)
        preceding=snap
    return evidence,seed,{'scope':scope,'seed_sha256':commitment,'commitment_commit':seen[cp][2],'scope_commit':seen[sp][2],'reveal_commit':seen[rp][2],'custody_commit':tip.commit,'local_order_verified':True}

def audit_injections(g,rows,records,manifests,artifact,policy_hash,finding):
    plans={}; fixtures={}; counted=set(); normalized=set(); details=[]
    for p in g.list('injections'):
        if not p.endswith('.json'): continue
        data=g.read(p); h=sha(data)
        if p.startswith('injections/fixtures/'):
            if p!='injections/fixtures/'+h+'.json': finding('FIXTURE_FILENAME_HASH',path=p); continue
            fixtures[h]=(p,data)
        else:
            if '/' in p[len('injections/'):]: finding('PLAN_PATH',path=p); continue
            plans[h]=(p,data)
    commits=history(g); snapshots=[snapshot(g,c) for c in commits] if rows else []
    for row in rows:
        t=row['body']; d={'seq':row['seq'],'counted_locally':False,'differences':[],'gaps':[]}; details.append(d)
        try:
            require(row['valid'] and not row.get('artifact_bad'),'invalid injection record'); i=t['injection']; ph,fh,target=i['plan_sha256'],i['fixture_sha256'],i['intended_rule']; d['intended_rule']=target
            p,pb=plans[ph]; fp,fb=fixtures[fh]; plan=load(pb); keys(plan,['injections']); entries=arr(plan['injections']);
            for entry in entries:
                keys(entry,['fixture_sha256','intended_rule']); hx(entry['fixture_sha256']); require(entry['intended_rule'] in RULES,'plan rule')
            require(sum(entry=={'fixture_sha256':fh,'intended_rule':target} for entry in entries)==1,'plan does not uniquely name fixture and rule')
            f=load(fb); fixture_schema(f); m=manifests[row['manifest']]; require(f['policy_sha256']==policy_hash==m['policy_sha256']==t['policy_sha256'],'injection policy mismatch')
            # Commit containing exact record line must have a strictly earlier
            # ancestor with both exact founder files, retained until the record.
            seq=row['seq']; record_commit=None
            for idx,snap in enumerate(snapshots):
                lines=chain_bytes(snap).splitlines()
                if len(lines)>seq:
                    require(load(lines[seq])==row['record'],'injection record changed in history'); record_commit=idx; break
            require(record_commit is not None and record_commit>0,'injection history missing')
            before=snapshots[record_commit-1]; require(before.read(p)==pb and before.read(fp)==fb,'plan/fixture not present before injection record'); d['plan_fixture_prior_commit']=before.commit; d['injection_first_commit']=snapshots[record_commit].commit
            inv=integer(t['invocation_instant']); lock=integer(t['lock_clock_at']); T0=integer(m['T_d0']); end=T0+m['declared_slots']*STEP; require(inv<=lock and T0<=inv<end,'injection command/lock outside open run'); next_td=T0+((inv-T0)//STEP+1)*STEP; require(next_td-inv>=30*NS and lock<next_td,'injection overlaps next slot or starts within 30s');
            for other in records:
                if other['manifest']!=row['manifest'] or other['type'] not in ('CYCLE','CONCURRENT_INVOCATION'): continue
                x=attempt(lambda:integer(other['body']['invocation_instant']))
                require(x is None or not inv<=x<=lock,'injection not aborted on slot invocation')
            expected,gaps,diffs=injection_replay(t,f,artifact); d.update(differences=diffs,gaps=gaps,recomputed_terminal=expected['terminal_state'],recomputed_rules=expected['rule_results']);
            require(not diffs and not gaps,'injection recomputation mismatch or gap')
            recorded={x['rule'] for x in t['rule_results'] if x['result']=='FAIL'}; recomputed={x['rule'] for x in expected['rule_results'] if x['result']=='FAIL'}
            require(t['terminal_state']==expected['terminal_state']=='REJECTED' and recorded==recomputed=={target},'not rejected solely by intended rule')
            # Distinct bytes AND distinct decoded input objects: whitespace-only
            # substitutions are not distinct fixtures (conservative CC).
            norm=sha(jcs(f).encode('utf-8')); require(fh not in counted and norm not in normalized,'duplicate counted fixture'); counted.add(fh); normalized.add(norm); d['counted_locally']=True
        except (ValueError,KeyError,TypeError,ArithmeticError,AttributeError,IndexError) as exc:
            d['gaps'].append(str(exc)); finding('INJECTION_NOT_COUNTED',**d)
    return {'records':len(rows),'locally_verified_intended_rule_rejections':len(counted),'verified_intended_rule_rejections':0,'push_provenance':'UNVERIFIED','details':details}


def plain(r):
    print('SL-PT-001 FD-6 | STRICT AUDIT | '+r.get('status','ERROR'))
    print('Audited commit:',r.get('commit')); print('Chain head:',r.get('chain_head')); print('Chain integrity:',r.get('chain_integrity'))
    print(LIMITATION); print('Denominator:',r.get('denominator'),'run_length:',r.get('run_length'),'conditional run_length:',r.get('conditional_run_length'),'M1-1:',r.get('M1_1'))
    for m in r.get('manifests',[]):
        print('\nMANIFEST',m['manifest_sha256'],'N=',m['declared_slots'],'run_length=',m['run_length'],'conditional=',m['conditional_run_length'])
        for s in m['slots']: print(' ',s['slot_index'],s['cycle_id'],s['classification'],'conditional='+s['conditional_classification'], '; '.join(s['reason']))
    print('\nSEEDED SAMPLE')
    for s in r.get('sample',[]): print(json.dumps(s,ensure_ascii=False,default=str,sort_keys=True))
    print('M1-6:',r.get('M1_6'),'M1-1 local threshold:',r.get('M1_1_local_threshold_met')); print('\nINJECTIONS',json.dumps(r.get('injections'),default=str)); print('NO_ACTION by signal:',r.get('qualifying_no_action'),'conditional:',r.get('conditional_no_action'))
    print('\nFINDINGS')
    for f in r.get('findings',[]): print(json.dumps(f,ensure_ascii=False,default=str,sort_keys=True))
    print('\nLIMITATIONS')
    for x in r.get('limitations',[]): print('-',x)
    print('\n--- JSON SUMMARY ---'); print(json.dumps(r,ensure_ascii=False,default=str,sort_keys=True,indent=2))

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('repository'); p.add_argument('--custody-commit',required=True); p.add_argument('--scope',required=True); p.add_argument('--evidence-root',default='experiments/sl-pt-001'); args=p.parse_args()
    try: g,seed,custody=load_custody(args.repository,args.custody_commit,args.evidence_root,args.scope); r=audit(g,seed,custody); plain(r); return 1
    except (ValueError,OSError,KeyError,TypeError,ArithmeticError,AttributeError,IndexError) as exc:
        plain({'status':'FATAL_INPUT_ERROR','M1_6':'NOT_MET','M1_1':'NOT_ESTABLISHED','commit':getattr(locals().get('g'),'commit',None),'findings':[{'code':'FATAL_INPUT','detail':str(exc)}],'limitations':[LIMITATION]}); return 2
if __name__=='__main__': sys.exit(main())
