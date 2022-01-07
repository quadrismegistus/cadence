from ..imports import *
from .txtparsing import *


"""
ITER LINES
"""

def iter_lines(txt_or_txtdf,num_proc=1,**kwargs):
    #yield from scan_iter(txt_or_txtdf,num_proc=num_proc,**kwargs)
    if type(txt_or_txtdf) == str:
        yield from scan_iter(txt_or_txtdf,num_proc=num_proc,**kwargs)
    else:
        for i,g in txt_or_txtdf.groupby(['stanza_i','line_i']):#,'linepart_i']):
            yield g

def iter_lines(txt_or_txtdf,num_proc=1,**kwargs):
    #yield from scan_iter(txt_or_txtdf,num_proc=num_proc,**kwargs)
    if type(txt_or_txtdf) == str:
        yield from scan_iter(txt_or_txtdf,num_proc=num_proc,**kwargs)
    else:
        for i,g in txt_or_txtdf.groupby(['stanza_i','line_i']):#,'linepart_i']):
            yield g


def iter_combos(txtdf,num_proc=1):
    for dfline in iter_lines(txtdf,num_proc=num_proc):
        # ldf=resetindex(dfline)
        ldf=dfline.reset_index()
        # linedf_nopunc = ldf[ldf.is_syll!=0]
        linedf_nopunc=ldf
        for dfi,dfcombo in enumerate(apply_combos(linedf_nopunc, 'word_i', 'word_ipa_i')):
            dfcombo['combo_i']=dfi
            dfcombo['combo_stress']=''.join(dfcombo.syll_stress)
            # dfcombo['combo_syll_i']=pd.Series(list(index_by_truth(dfcombo.is_syll)))+1
            dfcombo['combo_syll_i']=list(range(len(dfcombo)))
            dfcombo['combo_syll_i']+=1
            dfcombo['combo_num_syll']=dfcombo['combo_syll_i'].max()
            dfcombo['combo_ipa']=' '.join(
                '.'.join(wdf.syll_ipa)
                for wi,wdf in sorted(dfcombo.groupby('word_i'))
            )
            yield dfcombo
            #yield setindex(dfcombo)

def get_all_combos(txtdf):
    return resetindex(pd.concat(iter_combos(txtdf)))


"""
ITER PARSES
"""


# def get_scansion_key(scansion_df_or_str,**kwargs):
#     sdf=get_scansion(scansion_df_or_str,**kwargs)
    
#     # sdf
#     o=[]
#     for word_i,wdf in sdf.groupby('word_i'):
#         x=[]
#         for word_ipa_i,widf in wdf.groupby('word_ipa_i'):
#             x+=[widf.word_ipa.iloc[0]]
#         o+=['/'.join(x)]
#     ostr='_'.join(o)
#     return ostr

def get_parse_cache(linepart_str,path=None,**kwargs):
    #lpdf=get_scansion(linepart_str,**kwargs)
    lpdf_key=linepart_str#get_scansion_key(lpdf)
    cs="|".join(sorted(list(kwargs.get("constraints",DEFAULT_CONSTRAINTS))))
    dbk=f'{lpdf_key}{DBSEP}parse{DBSEP}{cs}'
    with get_db(path=path) as db:
        if not dbk in db:
            db[dbk]=get_parse_nocache(linepart_str,**kwargs)
        # else: print('from cache:',[dbk])
        return db[dbk]

def get_parse_nocache(linepart_str,path=None,**kwargs):
    # print('no cache:',[linepart_str])
    lpdf=get_scansion(linepart_str,**kwargs)
    if len(lpdf):
        pdf=parse_linepartdf(lpdf,**kwargs)
        # strcols={'word_str', 'syll_str', 'linepart_str'}
        if len(pdf):
            # pdf=pdf[[col for col in pdf.columns if col not in strcols]]
            return pdf
    return pd.DataFrame()

def get_parse(linepart_str_or_df,path=None,cache=True,force=False,**kwargs):
    linepart_str = get_linepart_str(linepart_str_or_df)
    linepart_df = get_linepart_df(linepart_str_or_df)
        
    if cache and not force:
        pdf=get_parse_cache(linepart_str,path=path,**kwargs)
    else:
        pdf=get_parse_nocache(linepart_str,path=path,**kwargs)
            
    cols1=set(linepart_df.columns)
    cols2=set(pdf.columns)
    row=linepart_df.iloc[0]
    joiner=['word_i','word_ipa_i','syll_i']
    odf=pdf.merge(linepart_df[(cols1-cols2) | set(joiner)],on=joiner,how='left')
    if len(odf): odf['linepart_str']=linepart_str
    return setindex(odf)

    
def parse_linepartdf(linepartdf,linepart_str=None,**kwargs):
    odf=resetindex(linepartdf)
    odf=parse_prosodic_line(odf,**kwargs)
    odf=postproc_dfline(odf,**kwargs)
    if 'index' in odf.columns: odf=odf.drop('index',1)
    return odf


def do_parse_iter(obj):
    metad,attrs = obj
    lpstr=metad.get('linepart_str')
    odf=get_parse(lpstr,**attrs)
    for k,v in metad.items(): odf[k]=v
    return setindex(odf)


def parse_iter(
        txt_or_txtdf,
        num_proc=DEFAULT_NUM_PROC,
        progress=True,
        lim=None,
        shuffle=False,
        lineparts_ld=None,
        **kwargs
    ):
    try:
        if not lineparts_ld: lineparts_ld=lineparts(txt_or_txtdf, **kwargs)
        objs = [(d,kwargs) for d in lineparts_ld]
        if shuffle: random.shuffle(objs)
        if lim: objs=objs[:lim]
        proc_gen=pmap_iter(do_parse_iter, objs, num_proc=num_proc, progress=progress)
        yield from proc_gen
    except AssertionError:
    # except (KeyError,AttributeError) as e:
        # print('!!',e)
        yield pd.DataFrame()

def parse(txt_or_txtdf,*x,verbose=False,**y):
    """
    Return parses
    """
    o=list(parse_iter(txt_or_txtdf,*x, verbose=verbose, **y))
    odf=pd.concat(o) if len(o) else pd.DataFrame()
    return odf


def parse_iter_lines(txt_or_txtdf,**kwargs):
    o=[]
    last=None
    joiner=['stanza_i','line_i']
    iterr=parse_iter(txt_or_txtdf,**kwargs)
    for pdf in iterr:
        if not len(pdf): continue
        pdf=resetindex(pdf)
        row=pdf.iloc[0]
        pdfkey=tuple([row[k] for k in joiner])
        if (last is not None) and (last!=pdfkey) and len(o):
            yield setindex(pd.concat(o))
            o=[]
        o+=[pdf]
        last=pdfkey
    if len(o): yield setindex(pd.concat(o))


def iter_parsed_combos(
        txtdf,
        num_proc=DEFAULT_NUM_PROC,
        progress=False,
        **kwargs):

    iter1=tqdm(
        iter_lines(txtdf,**kwargs),
        total=get_num_lines(txtdf),
        disable=(not progress)
    )

    for linedf in iter1:
        try:
            gdf=get_all_combos(linedf)
            yield from pmap_iter_groups(
                parse_combo,
                gdf.groupby(['stanza_i','line_i','combo_i']),
                num_proc=1,
                #progress=progress,
                kwargs=kwargs,
                progress=False,
                desc='Metrically parsing lines (+word IPA combinations)'
            )
        except ValueError:
            yield linedf







def parse_combo(linecombodf,engine=ENGINE,**kwargs):
    if engine==ENGINE_PROSODIC:
        odf=parse_prosodic_combo(linecombodf,**kwargs)
    else:
        raise Exception('Only prosodic implemented right now')
        # odf=parse_combo_cadence(linecombodf,**kwargs)
    return odf



def parse_prosodic_line(
        txt_or_txtdf,
        lang='en',
        meter=DEFAULT_METER,
        use_espeak=True,
        constraints=DEFAULT_CONSTRAINTS,
        constraint_weights=None,
        parse_maxsec=DEFAULT_PARSE_MAXSEC,
        set_index=True,
        **kwargs):
    p.config['resolve_optionality']=1
    p.config['print_to_screen']=False
    p.config['en_TTS_ENGINE']='espeak' if use_espeak else 'none'
    p.config['num_bounded_parses_to_store']=NUM_BOUNDED_TO_STORE

    # print(constraints)
    # print(kwargs)
    
    meter_obj=p.config['meters'][meter]
    config=default_config=meter_obj.config
    config['parse_maxsec']=parse_maxsec
    config['print_to_screen']=False


    if constraints is not None:
        constraints_pros=[
            f'{constraint_names_in_prosodic[c]}/{constraint_weights[i] if constraint_weights is not None else 1}'
            for c in constraints
        ]
        config['constraints']=constraints_pros
        meter_obj=p.Meter(config)
    
    txtdf = scan(txt_or_txtdf,**kwargs) if type(txt_or_txtdf)==str else txt_or_txtdf
    txtdf = txtdf.sort_index()
    
    line_words=[]
    plang=p.dict[lang]
    plang.getprep_syllabify_orth=None
    for wi0,wdf0 in txtdf.reset_index().groupby('word_i'):
        word_objs=[]
        for wi,wdf in wdf0.groupby('word_ipa_i'):
            ipa_str='.'.join(wdf.syll_ipa)
            sylls_text=list(wdf.syll_str)
            sylls_text_zp = [zero_punc(sx) for sx in sylls_text]
            token = wdf.iloc[0].word_str
            #print(wi0,wi,token,ipa_str)
            word_obj = plang.make((ipa_str,sylls_text_zp), token)
            word_obj.word_i=wi0
            word_obj.word_ipa_i=wi
            try:
                if wdf.is_funcword.iloc[0]==1: word_obj.feats['functionword']=True
            except AttributeError:
                display(wdf)
                stop
            # print(word_obj, word_obj.feats)
            word_objs.append(word_obj)
        wordtoken_obj = p.WordToken(word_objs, token)
        line_words.append(wordtoken_obj)
    l=p.Line()
    l.children = line_words
    l.parse(meter=meter_obj)
    odf=prosodic_line_to_data(l,txtdf,**kwargs)
    if 'parse_pos_i' in set(odf.columns): odf['parse_pos_i']+=1
    if 'parse_i' in set(odf.columns): odf['parse_i']+=1
    if 'combo_i' in set(odf.columns): odf['combo_i']+=1
    # if set_index: odf=setindex(odf,sort=True)
    return odf
        

def prosodic_line_to_data(
        line,
        txtdf,
        viols_in_parse_str=True,
        total_col=TOTALCOL,
        only_unbounded=True,
        posthoc_constraints=APPLY_POSTHOC_CONSTRAINTS,
        **kwargs):
    
    if line is None: return pd.DataFrame()
    if line.allParses() is None: return pd.DataFrame()
    all_parses = [(parse,True) for parse in line.allParses()]
    if not only_unbounded:
        all_parses+=[(parse,False) for parse in line.boundParses()][:NUM_BOUNDED_TO_STORE]
    needed_len=None
    O=[]
    for parse_i,(parse,is_unbounded) in enumerate(all_parses):
        o=[]
        parse_mstr=parse.str_meter()
        if needed_len is None:
            needed_len=len(parse_mstr)
        else:
            if len(parse_mstr)!=needed_len:
                break
        parse_str=parse.posString(viols=viols_in_parse_str)
        # parse_str=parse_str.replace('|',' ')
        # parse_mstr=' '.join(parse_mstr)
        bounded_by='' if is_unbounded else parse.boundedBy.str_meter()
        for pos_i,pos in enumerate(parse.positions):
            constraintd=dict(sorted(
                (constraint_names_from_prosodic.get(k.name,k.name),v)
                for k,v in pos.constraintScores.items()
            ))
            
            if total_col not in constraintd: constraintd[total_col]=sum(constraintd.values())
            mval=pos.meterVal
            mval2=''.join(mval for n in range(len(pos.slots)))
            
            nsyll=0
            for slot_i,slot in enumerate(pos.slots):
                nsyll+=1
                odx=dict(
                    word_i=slot.word.word_i,
                    word_ipa_i=slot.word.word_ipa_i,
                    syll_i=slot.wordpos[0],
                    parse_i=parse_i,
                    parse=parse_mstr,
                    parse_str=parse_str,
                    parse_pos_i=pos_i,
                    parse_pos=mval2,
                    parse_syll_i=nsyll,
                    parse_syll=mval,
                    **constraintd,
                    is_w=int(mval=='w'),
                    is_s=int(mval=='s'),
                    parse_num_pos=len(parse.positions),
                    parse_num_syll=len(parse_mstr.replace(' ','')),
                    parse_is_bounded=not is_unbounded,
                    parse_bounded_by=bounded_by
                )
                o.append(odx)
        if not len(o): continue
        odf=pd.DataFrame(o)
        
        
        odf=txtdf.reset_index().merge(
            odf,
            how='inner',
            on=['word_i','word_ipa_i','syll_i'],
            suffixes=['','_parse']
        )

        if posthoc_constraints:
            apply_posthoc_constraints(odf)
        
        


        O+=[odf]

    ## add back combo data
    if not len(O): return pd.DataFrame()
    odf=pd.concat(O)
    combos_sofar={}
    def tocombo(xdf):
        #display(xdf)
        key=tuple(xdf.reset_index().syll_ipa)
        if not key in combos_sofar: combos_sofar[key]=len(combos_sofar)
        return combos_sofar[key]
    odf=pd.concat(
        g.assign(
            combo_i=tocombo(g),
            combo_stress=' '.join(''.join(wdf.syll_stress) for wi,wdf in sorted(g.groupby('word_i'))),
            combo_ipa=' '.join('.'.join(wdf.syll_ipa) for wi,wdf in sorted(g.groupby('word_i')))
        )
        for i,g in odf.groupby('parse_i')
    )
    #print('3')
    #display(odf)

    return odf


def rank_parses(dfparses,**kwargs):
    odf=dfparses
    try:
        odf[TOTALCOL]=odf[[col for col in odf.columns if col.startswith('*') and col!=TOTALCOL]].sum(axis=1)
        odf['is_troch']=odf['parse'].apply(lambda x: int(x and x[0]=='s'))
        newrankdf=odf[['parse_i',TOTALCOL]].groupby('parse_i').sum().sort_values(TOTALCOL).reset_index()
        newrankdf['ranks_int']=pd.Series(list(range(len(newrankdf))))+1
        newrank=dict(zip(newrankdf.parse_i, newrankdf.ranks_int))
        odf['parse_rank']=odf.parse_i.apply(lambda x: int(newrank.get(x,0)))
        odf['num_parses']=odf['parse_rank'].max()
    except (KeyError,AttributeError) as e:
        pass
    return odf


def postproc_dfline(
        dfline,
        by_line=False,
        verbose=False,
        verbose_bylinepart=True,
        only_best=False,
        only_unbounded=False,
        rebound=False,
        rank=True,
        verse=None,
        prose=None,
        **kwargs):
    odf=dfline
    if rebound: odf=bound_parses(odf,only_unbounded=only_unbounded)
    if rank: odf=rank_parses(odf,**kwargs)
    if only_best: odf=odf[odf.parse_rank==1]
    if by_line: odf=to_lines(odf)
    return odf

def is_bounded(pdf1,pdf2,totalcol=TOTALCOL,cprefix='*'):
    cdf1=pdf1[[c for c in pdf1.columns if c.startswith(cprefix) and c!=totalcol]]
    cdf2=pdf2[[c for c in pdf2.columns if c.startswith(cprefix) and c!=totalcol]]
    o=[]
    
    c1orig=cdf1.sum()
    c2orig=cdf2.sum()

    for c1,c2 in [(c1orig,c2orig), (c2orig,c1orig)]:
        greater=c2>=c1
        equal=c1==c2
        bounds=set(greater)=={True} and set(equal)!={True}
        #print(c1,c2,bounds,set(greater),set(equal))
        o+=[bounds]
    #stop
    return tuple(o)

def bound_parses(odforig,only_unbounded=False):
    odfg=odf=odforig#.reset_index()
    prank2meter=dict(zip(odf.parse_rank, odf.parse))
    if 'parse_is_bounded' in set(odf.columns):
        odf.parse_bounded_by=[
            ''.join(x) if type(x)==str and x else ''
            for x in odf.parse_bounded_by
        ]
        odfg=odf[odf.parse_is_bounded==False]
    else:
        odfg=odf.assign(parse_is_bounded=False)
    
    grps=sorted(list(odfg.groupby('parse_rank')),reverse=True)
    not_ok_ranks=set()
    bounded_by_d={}
    for parse_rank1,parsedf1 in grps:
        for parse_rank2,parsedf2 in grps:
            if parse_rank1>=parse_rank2: continue
            if parse_rank1 in not_ok_ranks or parse_rank2 in not_ok_ranks: continue
            x_bounds_y, y_bounds_x = is_bounded(parsedf1,parsedf2)
            if y_bounds_x: 
                not_ok_ranks|={parse_rank1}
                if parse_rank1 not in bounded_by_d:
                    bounded_by_d[parse_rank1]=prank2meter.get(parse_rank2)
            if x_bounds_y:
                not_ok_ranks|={parse_rank2}
                if parse_rank2 not in bounded_by_d:
                    bounded_by_d[parse_rank2]=prank2meter.get(parse_rank1)
    
    #odf=odf[~odf.index.get_level_values('parse_rank').isin(not_ok_ranks)]
    def isbound(isb,prank):
        if isb: return True
        if prank in not_ok_ranks: return True
        return False
    def isboundedby(bby,prank):
        if bby: return bby
        return bounded_by_d.get(prank,'')
        
    odf['parse_is_bounded']=[isbound(isb,prank) for isb,prank in zip(odf.parse_is_bounded, odf.parse_rank)]
    odf['parse_bounded_by']=[isboundedby(isb,prank) for isb,prank in zip(odf.parse_bounded_by.fillna(''), odf.parse_rank)]
    if only_unbounded: odf=odf[odf.parse_is_bounded==False]
    # odf.parse_rank=odf.parse_rank.rank(ascending=True,method='dense').apply(int)
    
    return odf






"""
Summarizing by line
"""


def to_lines(parses,totalcol=TOTALCOL,rankcol=PARSERANKCOL, agg=sum):
    # parses
    rparses=resetindex(parses)
    rcols=set(rparses.columns)
    pkcols = [c for c in PARSELINEKEY if c in rcols]
    # sum by actual data lines
    valcols = [c for c in rparses.select_dtypes('number').columns
              if not c in pkcols
              if not c.endswith('_i')
              if not c.endswith('_ii')
              if not c in {'index','level_0'}
              ]
    aggfunc = dict((vc,sum) for vc in valcols)
    # medians=['combo_num_syll','parse_num_syll','line_num_syll','parse_num_pos']
    medians = [col for col in rcols if '_num_' in col or col=='num_parses']
    for mx in medians:
        if mx in rcols:
            aggfunc[mx]=np.median
    lgby=['stanza_i','line_i','linepart_i','linepart_str']
    try:
        linesums = rparses.groupby(pkcols).agg(aggfunc)
    except Exception as e:
        # print('!!',e)
        return pd.DataFrame()
    return linesums
    
def iter_parses(*x,by_line=True,**y):
    yield from iter_parsed_lines(*x,by_line=by_line,**y)
    
    
    
  

###### SHOWING


accentd={
    'a':'á',
    'e':'é',
    'i':'í',
    'o':'ó',
    'u':'ú',
    'y':'ý',
}
for k,v in list(accentd.items()): accentd[k.upper()]=v.upper()

def show_parses(parses_bysyll):
    try:
        from IPython.display import HTML
        return HTML(show_parses_md(parses_bysyll))
    except ImportError:
        return show_parses_txt(parses_bysyll)
    
def show_parse_md(dfparse):
#     print(dfparse.reset_index().line_i.nunique())
#     print(dfparse.reset_index().linepart_i.nunique())
    dfp=dfparse.reset_index()
    mdline=[]
    for l,dflp in sorted(dfp.groupby('linepart_i')):
        mdrow=[]
        #display(dflp)
        
        for w,dfword in sorted(dflp.groupby('word_i')):
            mdword=[]
            for s,dfsyll in sorted(dfword.groupby('syll_i')):
                row=dfsyll.iloc[0]
                wpref,w,wsuf = split_punct(row.syll_str)
                
                if row.is_stressed:
                    w2=[]
                    accented=False
                    numvowels=len([y for y in w if y in accentd])
                    for x in w:
                        if not accented and x in accentd:
                            if numvowels<2 or x!='y':
                                x=accentd[x]
                                accented=True
                        w2+=[x]
                    w=''.join(w2)
                    
                md=w#f'{row.syll_str}'
                if row.is_s: md=f'<b>{md}</b>'
                #if row.is_s: md=f'<u>{md}</u>'
                #if row.is_w: md=f'<i>{md}</i>'
                #if row.is_stressed: md=f'<i>{md}</i>'
                if row['*total']>0:
                    # md=f'<span style="color:darkred">{md}</span>'
                    md=f'<font style="color:darkred">{md}</font>'
                    # md=f'<i>{md}</i>'
                md=f'{wpref}{md}{wsuf}'
                mdword+=[md]
            mdrow.append(''.join(mdword))
        mdline.append(''.join(mdrow))
    
    # spltr='\n * '
    # o=spltr + spltr.join(mdline)#.replace('</u> <u>',' ')
    o=' | '.join(mdline)#.replace('</u> <u>',' ')
    return o

def get_best_parse(dfparse):
    for i,g in dfparse.groupby(['parse_rank','is_troch','parse_i']): break
    return g

def get_best_parses(dfparses):
    o=[get_best_parse(g) for i,g in dfparses.groupby(['stanza_i','line_i','linepart_i'])]
    return pd.concat(o) if len(o) else pd.DataFrame()

def show_parse(dfparse,only_best=True):
    dfparse=get_best_parses(dfparse)

    try:
        from IPython.display import HTML
        return HTML(show_parse_md(dfparse))
    except ImportError:
        return show_parse_txt(dfparse)
    

def show_parses_md(parses_bysyll):
    
    grps=sorted(parses_bysyll.reset_index().groupby(
        ['stanza_i','line_i']#,'linepart_i','parse_rank']    
    ))
    mdl=[show_parse_md(dfparse) for i,dfparse in grps]
    omd='\n<br/>'.join(mdl)
    return omd
    
 
def info_parses(dfparses_or_path,lcols=['stanza_i','line_i','linepart_i'],min_num_syll=4):
    infod={}

    try:
        if type(dfparses_or_path)==str:
            if os.path.exists(dfparses_or_path):
                dfparses=read_df(dfparses_or_path)
            else:
                return {}
        else:
            dfparses=dfparses_or_path    
        
        # byline
        allcols=set(dfparses.columns)|set(dfparses.index.names)
        if 'syll_i' in allcols: dfparses=to_lines(dfparses)
        allcols=set(dfparses.columns)|set(dfparses.index.names)
        if 'parse_num_syll' not in allcols: return infod
        dfparses=dfparses.query(f'parse_num_syll>={min_num_syll}')


        infod['num_lines_total']=dfparses.groupby(['stanza_i','line_i','linepart_i']).size().shape[0]
        
        # avg num sylls
        num_sylls = dfparses.groupby(lcols).parse_num_syll.mean()
        num_monosylls = dfparses.groupby(lcols).linepart_num_monosyll.mean()
        infod['num_sylls_avg'] = num_sylls.mean()

        infod['num_monosylls_avg'] = num_monosylls.mean()
        num_monosylls_per_10syll = num_monosylls / num_sylls * 10
        infod['num_monosylls_per_10syll_avg'] = num_monosylls_per_10syll.mean()
        

        # avg num parses per line?
        num_parses = dfparses.groupby(lcols).size()# / dfparses.groupby(lcols).parse_num_syll.mean()
        infod['num_parses_avg'] = num_parses.mean()
        num_parses_per_10syll = num_parses / num_sylls * 10
        infod['num_parses_per_10syll_avg'] = num_parses_per_10syll.mean()
        
        
        # avg viols?
        vkeys=[col for col in dfparses.columns if col.startswith('*')]
        for vk in vkeys:
            vk2='' if vk=='*total' else f'__{vk}'
            num_viols = dfparses.groupby(lcols)[vk].mean()
            infod[f'num_viols_avg{vk2}'] = num_viols.mean()
            num_viols_per_10syll = num_viols /num_sylls * 10
            infod[f'num_viols_per_10syll_avg{vk2}'] = num_viols_per_10syll.mean()

        return infod
    except KeyError:
        return infod
    
def show_info_parses(infod):
    return f'''
* Metrical friction: **{infod["num_viols_per_10syll_avg"]:.02f}** viols per 10 sylls (**{infod["num_viols_avg"]:.02f}** per parse)
* Metrical ambiguity: **{infod["num_parses_per_10syll_avg"]:.02f}** parses per 10 sylls (**{infod["num_parses_avg"]:.02f}** per parse)
'''