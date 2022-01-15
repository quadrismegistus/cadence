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

# def parse_combo(dfcombo_orig,min_nsyll=4,**kwargs):
#     dfcombo=dfcombo_orig[dfcombo_orig.word_ipa!=""]
#     bounded={}
#     dfpars=get_poss_parses(len(dfcombo))
#     scored={}
#     for nsyll,nsylldf in sorted(dfpars.groupby('nsyll')):
#         if nsyll<min_nsyll: continue
#         scored={}
#         for meter in nsylldf.meter:
#             exclude=False
#             for bmeter in bounded:
#                 if meter.startswith(bmeter):
#                     exclude=True
#                     break
#             if exclude: continue
#             scored[meter] = apply_constraints(dfcombo, meter, **kwargs)
#         for mtr1 in scored:
#             for mtr2 in scored:
#                 if mtr1>=mtr2: continue
#                 s1=scored[mtr1].sum()
#                 s2=scored[mtr2].sum()
#                 s1_ever_better_than_s2 = any(s1<s2)
#                 s2_ever_better_than_s1 = any(s2<s1)
#                 if s1_ever_better_than_s2 and not s2_ever_better_than_s1:
#                     # s1 bounds s2
#                     bounded[mtr2]=mtr1
#                 elif s2_ever_better_than_s1 and not s1_ever_better_than_s2:
#                     # s2 bounds s1
#                     bounded[mtr1]=mtr2
    
#     o=[]
#     for mtr,mdf in scored.items():
#         mdf['slot_meter']=list(mtr.replace('|',''))
#         odf=mdf.join(dfcombo_orig[[]],how='outer')
#         odf['parse']=format_parse_str(mtr)
#         o.append(odf)
#     return concatt(o)

def parse_combo(dfcombo_orig,min_nsyll=None,**kwargs):
    dfcombo=dfcombo_orig[dfcombo_orig.word_ipa!=""]
    bounded={}
    dfpars=get_poss_parses(len(dfcombo))
    scored={}
    for nsyll,nsylldf in sorted(dfpars.groupby('nsyll')):
        if min_nsyll and nsyll<min_nsyll: continue
        scored={}
        for meter in nsylldf.meter:
            exclude=False
            for bmeter in bounded:
                if meter.startswith(bmeter):
                    exclude=True
                    break
            if exclude: continue
            scored[meter] = apply_constraints(dfcombo, meter, **kwargs)
        for mtr1 in scored:
            for mtr2 in scored:
                if mtr1>=mtr2: continue
                if mtr1[-2:]!=mtr2[-2:]: continue
                s1=scored[mtr1].sum()
                s2=scored[mtr2].sum()
                s1_ever_better_than_s2 = any(s1<s2)
                s2_ever_better_than_s1 = any(s2<s1)
                if s1_ever_better_than_s2 and not s2_ever_better_than_s1:
                    # s1 bounds s2
                    # eprint(mtr1,'bounds',mtr2)
                    bounded[mtr2]=mtr1
                elif s2_ever_better_than_s1 and not s1_ever_better_than_s2:
                    # s2 bounds s1
                    # eprint(mtr2,'bounds',mtr1)
                    bounded[mtr1]=mtr2
    
    o=[]
    for mtr,mdf in scored.items():
        mdf['slot_meter']=list(mtr.replace('|',''))
        odf=mdf.join(dfcombo_orig[[]],how='outer')
        odf['parse']=format_parse_str(mtr)
        o.append(odf)
    return concatt(o)

def format_parse_str(pstr):
    return pstr.replace('|','').replace('s','S')
    # if not pstr: return ''
    # # if not pstr.startswith('|'): pstr='|'+pstr
    # # if not pstr.endswith('|'): pstr=pstr+'|'
    # if pstr.endswith('|'): pstr=pstr[:-1]
    
    # return ' '.join(
    #     f'{x:^2}' for x in pstr.replace('s','S').split('|')
    # )

def get_constraints(constraints=DEFAULT_CONSTRAINTS):
    return [
        CONSTRAINTD.get(cname) if type(cname)==str else cname
        for cname in constraints
        if type(cname)!=str or cname in CONSTRAINTD
    ]


def apply_constraints(df, mtr, constraints=DEFAULT_CONSTRAINTS, allow_partial=False, **kwargs):
    if type(mtr)==str:
        mtr=mtr.replace('|','').lower()
        is_s=np.array([float(x=='s') for x in mtr])
    else:
        is_s=mtr

    df=df.iloc[:len(is_s)]
    odf=pd.DataFrame(index=df.index)
    
    for cnstr in get_constraints(constraints):
        o=cnstr(df, is_s)
        if not allow_partial: o=[1.0 if x>0 else 0.0 for x in o]
        odf['*' + cnstr.__name__] = o

    return odf



###
# PARSING UNITS
###

def parse_unit_combos(
        dfunit,
        index=False,
        **kwargs):
    o=[]
    for ci,dfcombo in enumerate(iter_combos(dfunit)):
        # print(ci,'...')
        try:
            ok_parses = parse_combo(dfcombo,**kwargs)
            dfcombo_join = dfcombo[[col for col in dfcombo.columns if col in set(LINEKEY)]]
            ok_parses2 = ok_parses.join(dfcombo_join)
            o.append(ok_parses2)
        except KeyError as e:
            pass
    odf=pd.concat(o) if len(o) else pd.DataFrame()
    if len(odf):
        odf=final_bounding(odf)
        unit_i=dfunit.unit_i.iloc[0]
        odf['unit_i']=unit_i
        parse_il=list(set(list(zip(odf.parse, odf.combo_i))))
        parse_id=dict((x,i+1) for i,x in enumerate(parse_il))
        odf['parse_i']=[parse_id[tup] for tup in zip(odf.parse, odf.combo_i)]
        odf=rank_parses(odf)
        odf['syll_str_parse']=[x.upper() if y=='s' else x.lower() for x,y in zip(odf.syll_str, odf.slot_meter)]
        odf['syll_str_parse']=['*'+x if y else x for x,y in zip(odf.syll_str_parse, odf['*total'])]
        
        parse_str_d={}
        for i,pdf in odf.groupby('parse_rank'):    
            parse_str=' '.join(
                '.'.join(wdf.syll_str_parse)
                for wi,wdf in pdf.groupby('word_i')
            )
            parse_str_d[i]=parse_str
        
        odf['parse_str']=odf.parse_rank.apply(lambda x: parse_str_d.get(x,''))
        # odf=odf.drop('syll_str',1)
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
    odf['is_troch']=odf['parse'].apply(lambda x: int(x and x[0].lower()=='s'))
    newrankdf=odf[['parse_i',TOTALCOL,'is_troch']].groupby(['parse_i','is_troch']).sum().reset_index().sort_values([TOTALCOL,'is_troch'])
    newrankdf['ranks_int']=list(range(len(newrankdf)))
    # newrankdf['ranks_int']+=1
    newrank=dict(zip(newrankdf.parse_i, newrankdf.ranks_int))
    # display(newrankdf)
    odf['parse_rank']=odf.parse_i.apply(lambda x: int(newrank.get(x,0))+1)
    odf['num_parses']=odf['parse_rank'].max()
    # odf=odf.drop('parse_i',1)
    # odf=odf.drop('is_troch',1)
    # display(odf)
    return odf


def to_lines(dfparses,totalcol=TOTALCOL,rankcol=PARSERANKCOL, agg=sum, only_best=False, **kwargs):
    # parses
    rparses=resetindex(dfparses)
    if only_best: rparses=rparses[rparses.parse_rank==1]
    rcols=set(rparses.columns)
    pkcols = [c for c in PARSELINEKEY if c in rcols]
    # sum by actual data lines
    valcols = [
        c for c in rparses.select_dtypes('number').columns
        if not c in set(pkcols)
        if not c.endswith('_i')
        if not c.endswith('_ii')
        if not c in {'index','level_0'}
    ]
    aggfunc = dict((vc,sum) for vc in valcols)
    medians = [col for col in rcols if 'num_' in col or col=='num_parses']
    for mx in medians:
        if mx in rcols:
            aggfunc[mx]=np.median
    # lgby=['para_i','unit_i','sent_i','sentpart_i','line_i']
    lgby=['para_i','unit_i']
    lgby+=['parse_rank','parse','parse_str']
    # if not only_best:
    #     lgby+=['parse_rank','parse','parse_str']
    # else:
    #     aggfunc['parse_str']='first'
    #     aggfunc['parse']='first'
    #     aggfunc['parse_str']='first'
        # aggfunc['parse']='first'
    lgby=[col for col in lgby if col in set(rparses.columns)]
    try:
        linesums = rparses.groupby(lgby).agg(aggfunc)
    except Exception as e:
        print('!!',e)
        return pd.DataFrame()
    
    linesums=linesums[sorted(linesums.columns)]
    if TOTALCOL in set(linesums.columns):
        linesums=linesums[[TOTALCOL] + [col for col in linesums.columns if col!=TOTALCOL]]
    return linesums
    


accentd={
    'a':'á',
    'e':'é',
    'i':'í',
    'o':'ó',
    'u':'ú',
    'y':'ý',
}
for k,v in list(accentd.items()): accentd[k.upper()]=v.upper()
        
def parse_markdown(dfparse,accent_stresses=False):
    dfp=resetindex(dfparse)
    dfp=dfp[dfp.parse_rank==1]
    mdline=[]
    for l,dflp in sorted(dfp.groupby('unit_i')):
        mdrow=[]
        for w,dfword in sorted(dflp.groupby('word_i')):
            mdword=[]
            for s,dfsyll in sorted(dfword.groupby('syll_i')):
                row=dfsyll.iloc[0]
                #wpref,w,wsuf = split_punct(row.syll_str)
                md=w=row.syll_str
                
                if row.syll_stress in {"P","S"}:
                    if accent_stresses:
                        w2=[]
                        accented=False
                        numvowels=len([y for y in w if y in accentd])
                        for x in w:
                            if not accented and x in accentd:
                                if numvowels<2 or x!='y':
                                    x=accentd[x]
                                    accented=True
                            w2+=[x]
                        md=w=''.join(w2)
                    else:
                        md=f'<b>{md}</b>'
                    
                if row.slot_meter=='s': md=f'<u>{md}</u>'
                if row['*total']>0:
                    md=f'<font style="color:darkred">{md}</font>'
                #md=f'{wpref}{md}{wsuf}'
                is_punc=not any(x.isalpha() for x in row.syll_str)
                mdword+=[md]
            mdrow.append('.'.join(mdword))
            if not is_punc: mdrow[-1]=' '+mdrow[-1]
        mdline.append(''.join(mdrow))
    
    # spltr='\n * '
    # o=spltr + spltr.join(mdline)#.replace('</u> <u>',' ')
    o=' | '.join(mdline)#.replace('</u> <u>',' ')
    return o



# accentd={
#     'a':'á',
#     'e':'é',
#     'i':'í',
#     'o':'ó',
#     'u':'ú',
#     'y':'ý',
# }
# for k,v in list(accentd.items()): accentd[k.upper()]=v.upper()

# def show_parses(parses_bysyll):
#     try:
#         from IPython.display import HTML
#         return HTML(show_parses_md(parses_bysyll))
#     except ImportError:
#         return show_parses_txt(parses_bysyll)
    
# def show_parse_md(dfparse):
# #     print(dfparse.reset_index().line_i.nunique())
# #     print(dfparse.reset_index().linepart_i.nunique())
#     dfp=dfparse.reset_index()
#     mdline=[]
#     for l,dflp in sorted(dfp.groupby('linepart_i')):
#         mdrow=[]
#         #display(dflp)
        
#         for w,dfword in sorted(dflp.groupby('word_i')):
#             mdword=[]
#             for s,dfsyll in sorted(dfword.groupby('syll_i')):
#                 row=dfsyll.iloc[0]
#                 wpref,w,wsuf = split_punct(row.syll_str)
                
#                 if row.is_stressed:
#                     w2=[]
#                     accented=False
#                     numvowels=len([y for y in w if y in accentd])
#                     for x in w:
#                         if not accented and x in accentd:
#                             if numvowels<2 or x!='y':
#                                 x=accentd[x]
#                                 accented=True
#                         w2+=[x]
#                     w=''.join(w2)
                    
#                 md=w#f'{row.syll_str}'
#                 if row.is_s: md=f'<b>{md}</b>'
#                 #if row.is_s: md=f'<u>{md}</u>'
#                 #if row.is_w: md=f'<i>{md}</i>'
#                 #if row.is_stressed: md=f'<i>{md}</i>'
#                 if row['*total']>0:
#                     # md=f'<span style="color:darkred">{md}</span>'
#                     md=f'<font style="color:darkred">{md}</font>'
#                     # md=f'<i>{md}</i>'
#                 md=f'{wpref}{md}{wsuf}'
#                 mdword+=[md]
#             mdrow.append(''.join(mdword))
#         mdline.append(''.join(mdrow))
    
#     # spltr='\n * '
#     # o=spltr + spltr.join(mdline)#.replace('</u> <u>',' ')
#     o=' | '.join(mdline)#.replace('</u> <u>',' ')
#     return o

# def get_best_parse(dfparse):
#     for i,g in dfparse.groupby(['parse_rank','is_troch','parse_i']): break
#     return g

# def get_best_parses(dfparses):
#     o=[get_best_parse(g) for i,g in dfparses.groupby(['stanza_i','line_i','linepart_i'])]
#     return pd.concat(o) if len(o) else pd.DataFrame()

# def show_parse(dfparse,only_best=True):
#     dfparse=get_best_parses(dfparse)

#     try:
#         from IPython.display import HTML
#         return HTML(show_parse_md(dfparse))
#     except ImportError:
#         return show_parse_txt(dfparse)
    

# def show_parses_md(parses_bysyll):
    
#     grps=sorted(parses_bysyll.reset_index().groupby(
#         ['stanza_i','line_i']#,'linepart_i','parse_rank']    
#     ))
#     mdl=[show_parse_md(dfparse) for i,dfparse in grps]
#     omd='\n<br/>'.join(mdl)
#     return omd
    
 
# def info_parses(dfparses_or_path,lcols=['stanza_i','line_i','linepart_i'],min_num_syll=4):
#     infod={}

#     try:
#         if type(dfparses_or_path)==str:
#             if os.path.exists(dfparses_or_path):
#                 dfparses=read_df(dfparses_or_path)
#             else:
#                 return {}
#         else:
#             dfparses=dfparses_or_path    
        
#         # byline
#         allcols=set(dfparses.columns)|set(dfparses.index.names)
#         if 'syll_i' in allcols: dfparses=to_lines(dfparses)
#         allcols=set(dfparses.columns)|set(dfparses.index.names)
#         if 'parse_num_syll' not in allcols: return infod
#         dfparses=dfparses.query(f'parse_num_syll>={min_num_syll}')


#         infod['num_lines_total']=dfparses.groupby(['stanza_i','line_i','linepart_i']).size().shape[0]
        
#         # avg num sylls
#         num_sylls = dfparses.groupby(lcols).parse_num_syll.mean()
#         num_monosylls = dfparses.groupby(lcols).linepart_num_monosyll.mean()
#         infod['num_sylls_avg'] = num_sylls.mean()

#         infod['num_monosylls_avg'] = num_monosylls.mean()
#         num_monosylls_per_10syll = num_monosylls / num_sylls * 10
#         infod['num_monosylls_per_10syll_avg'] = num_monosylls_per_10syll.mean()
        

#         # avg num parses per line?
#         num_parses = dfparses.groupby(lcols).size()# / dfparses.groupby(lcols).parse_num_syll.mean()
#         infod['num_parses_avg'] = num_parses.mean()
#         num_parses_per_10syll = num_parses / num_sylls * 10
#         infod['num_parses_per_10syll_avg'] = num_parses_per_10syll.mean()
        
        
#         # avg viols?
#         vkeys=[col for col in dfparses.columns if col.startswith('*')]
#         for vk in vkeys:
#             vk2='' if vk=='*total' else f'__{vk}'
#             num_viols = dfparses.groupby(lcols)[vk].mean()
#             infod[f'num_viols_avg{vk2}'] = num_viols.mean()
#             num_viols_per_10syll = num_viols /num_sylls * 10
#             infod[f'num_viols_per_10syll_avg{vk2}'] = num_viols_per_10syll.mean()

#         return infod
#     except KeyError:
#         return infod
    
# def show_info_parses(infod):
#     return f'''
# * Metrical friction: **{infod["num_viols_per_10syll_avg"]:.02f}** viols per 10 sylls (**{infod["num_viols_avg"]:.02f}** per parse)
# * Metrical ambiguity: **{infod["num_parses_per_10syll_avg"]:.02f}** parses per 10 sylls (**{infod["num_parses_avg"]:.02f}** per parse)
# '''