from ..imports import *
from .txtparsing import *


#####
# PARSE LINE UNITS
#####


def divide_parse_units(dfsyll,nsyll=None,linebreaks=LINEBREAKS,phrasebreaks=PHRASEBREAKS,**kwargs):
    # reverse
    if linebreaks and not phrasebreaks:
        dfsyll['unit_i']=divide_by_line_only(dfsyll)
    elif phrasebreaks and not linebreaks:
        dfsyll['unit_i']=divide_by_phrase_only(dfsyll)
    elif phrasebreaks and linebreaks:
        dfsyll['unit_i']=divide_by_phrase_and_line(dfsyll)
    
    dfsyll['unit_i']=list(divide_overflow(dfsyll))
    dfsyll['unit_i']=dfsyll['unit_i'].rank(method='dense').apply(int)


def divide_by_line_only(dfwords): return divide_by(dfwords,by=['line_i'])
def divide_by_phrase_only(dfwords): return divide_by(dfwords,by=['sent_i','sentpart_i'])
def divide_by_phrase_and_line(dfwords): return divide_by(dfwords,by=['sent_i','sentpart_i','line_i'])
def divide_by(dfwords, by=['sent_i','sentpart_i','line_i']):
    o=[]
    keynow=None
    unit_i=0
    inp = (dfwords[k] for k in by)
    for rowkey in zip(*inp):
        if rowkey!=keynow: unit_i+=1
        o.append(unit_i)
        keynow=rowkey
    return o

        

def get_nsyll(df):
    return len(df[df.word_ipa_i==1])

def divide_overflow(dfsyll,max_nsyll=MAX_SYLL_IN_PARSE_UNIT):
    for ui,unitdf in dfsyll.groupby('unit_i'):
        nsyll=get_nsyll(unitdf)
        if nsyll<=max_nsyll:
            for n in range(len(unitdf)):
                yield ui
        else:
            newui=[]
            nsyllnow=0
            ui2=2
            gl=list(unitdf.groupby(['sent_i','word_i']))
            for wi,wdf in reversed(gl):
                nsyll_word=get_nsyll(wdf)
                for si in range(len(wdf)): newui+=[ui + (1/ui2)]
                nsyllnow+=nsyll_word
                if nsyllnow>=max_nsyll:
                    ui2+=1
                    nsyllnow=0
            yield from reversed(newui)


###
# Iterating over positions
###


def getlenparse(l): return sum(len(x) for x in l)

def iter_mpos(nsyll, starter=[], pos_types=None, maxS=METER_MAX_S, maxW=METER_MAX_W):
    if pos_types is None:
        wtypes = ['w'*n for n in range(1,maxW+1)]
        stypes = ['s'*n for n in range(1,maxS+1)]
        pos_types=[[x] for x in wtypes + stypes]
        
    news=[]
    for pos_type in pos_types:
        if starter and starter[-1][-1]==pos_type[0][0]: continue
        new = starter + pos_type
        # if starter: print(starter[-1][-1], pos_type[0][0], new)
        #if not is_ok_parse(new): continue
        if getlenparse(new)<=nsyll:
            news.append(new)
    
    # news = battle_parses(news)
    if news: yield from news
    # print('\n'.join('|'.join(x) for x in news))
    for new in news: yield from iter_mpos(nsyll, starter=new, pos_types=pos_types)

POSSPARSED={}
def get_poss_parses(n,maxS=METER_MAX_S,maxW=METER_MAX_W):
    global POSSPARSED

    key=(n,maxS,maxW)
    if not key in POSSPARSED:    
        dfpars = pd.DataFrame([
            dict(
                npos=len(x),
                nsyll=getlenparse(x),
                meter='|'.join(x) + '|',
            )
            for x in iter_mpos(n)
            if getlenparse(x)<=n
        ])
        POSSPARSED[key]=dfpars
    return POSSPARSED[key]

def parse_combo(dfcombo,min_nsyll=4):
    bounded={}
    dfpars=get_poss_parses(len(dfcombo))
    scored={}
    for nsyll,nsylldf in sorted(dfpars.groupby('nsyll')):
        if nsyll<min_nsyll: continue
        scored={}
        for meter in nsylldf.meter:
            exclude=False
            for bmeter in bounded:
                if meter.startswith(bmeter):
                    exclude=True
                    break
            if exclude: continue
            scored[meter] = apply_constraints(dfcombo, meter)
        for mtr1 in scored:
            for mtr2 in scored:
                if mtr1>=mtr2: continue
                s1=scored[mtr1].sum()
                s2=scored[mtr2].sum()
                s1_ever_better_than_s2 = any(s1<s2)
                s2_ever_better_than_s1 = any(s2<s1)
                if s1_ever_better_than_s2 and not s2_ever_better_than_s1:
                    # s1 bounds s2
                    bounded[mtr2]=mtr1
                elif s2_ever_better_than_s1 and not s1_ever_better_than_s2:
                    # s2 bounds s1
                    bounded[mtr1]=mtr2
    
    odf=concatt([
        mdf.assign(
            parse=format_parse_str(mtr),
            slot_meter=list(mtr.replace('|',''))
        )
        for mtr,mdf in scored.items()
    ])
    return odf


def format_parse_str(pstr):
    return pstr.replace('|','').replace('s','S')
    # if not pstr: return ''
    # # if not pstr.startswith('|'): pstr='|'+pstr
    # # if not pstr.endswith('|'): pstr=pstr+'|'
    # if pstr.endswith('|'): pstr=pstr[:-1]
    
    # return ' '.join(
    #     f'{x:^2}' for x in pstr.replace('s','S').split('|')
    # )

def get_constraints(constraint_names=DEFAULT_CONSTRAINTS):
    return [
        CONSTRAINTD.get(cname)
        for cname in sorted(constraint_names)
        if cname in CONSTRAINTD
    ]


def apply_constraints(df, mtr, constraint_names=DEFAULT_CONSTRAINTS):
    if type(mtr)==str:
        mtr=mtr.replace('|','')
        is_s=np.array([float(x=='s') for x in mtr])
    else:
        is_s=mtr

    df=df.iloc[:len(is_s)]
    odf=pd.DataFrame(index=df.index)
    
    for cnstr in get_constraints(constraint_names):
        odf['*' + cnstr.__name__] = cnstr(df, is_s)

    return odf



###
# PARSING UNITS
###

def parse_unit_combos(
        dfunit,
        index=False,
        **kwargs):
    o=[]
    for dfcombo in iter_combos(dfunit):
        ok_parses = parse_combo(dfcombo,**kwargs)
        dfcombo_join = dfcombo[['sent_i','word_i','word_ipa_i','syll_i','combo_i']]
        ok_parses2 = ok_parses.join(dfcombo_join)
        o.append(ok_parses2)
    odf=pd.concat(o) if len(o) else pd.DataFrame()
    if len(odf):
        odf=final_bounding(odf)
        unit_i=dfunit.unit_i.iloc[0]
        odf['unit_i']=unit_i
        parse_il=list(set(list(zip(odf.parse, odf.combo_i))))
        parse_id=dict((x,i+1) for i,x in enumerate(parse_il))
        odf['parse_i']=[parse_id[tup] for tup in zip(odf.parse, odf.combo_i)]
        odf=rank_parses(odf)
        odf=setindex(odf) if index else resetindex(odf)
    return odf

def final_bounding(parses):
    groups = [g for i,g in parses.groupby(['combo_i','parse'])]
    for g in groups: g.bounded=False
    for i,g in enumerate(groups):
        for ii,gg in enumerate(groups):
            if i>=ii: continue
            bounds = df_bounds_df(g,gg)
            if bounds is True:
                gg.bounded=True
            elif bounds is False:
                g.bounded=True
    return pd.concat(g for g in groups if not g.bounded)

def df_bounds_df(df1,df2):
    cdf1=df1[[c for c in df1.columns if c.startswith('*')]]
    cdf2=df2[[c for c in df2.columns if c.startswith('*')]]
    s1=cdf1.sum()
    s2=cdf2.sum()
    s1_ever_better_than_s2 = any(s1<s2)
    s2_ever_better_than_s1 = any(s2<s1)
    if s1_ever_better_than_s2 and not s2_ever_better_than_s1:
        return True
    elif s2_ever_better_than_s1 and not s1_ever_better_than_s2:
        return False
    return None
    

def rank_parses(odf,**kwargs):
    odf[TOTALCOL]=odf[[col for col in odf.columns if col.startswith('*') and col!=TOTALCOL]].sum(axis=1)
    odf['is_troch']=odf['parse'].apply(lambda x: int(x and x[0]=='s'))
    newrankdf=odf[['parse_i',TOTALCOL]].groupby('parse_i').sum().sort_values(TOTALCOL).reset_index()
    newrankdf['ranks_int']=pd.Series(list(range(len(newrankdf))))+1
    newrank=dict(zip(newrankdf.parse_i, newrankdf.ranks_int))
    odf['parse_rank']=odf.parse_i.apply(lambda x: int(newrank.get(x,0)))
    odf['num_parses']=odf['parse_rank'].max()
    return odf