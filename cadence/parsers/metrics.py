from ..imports import *
from .txtparsing import *


"""
ITER LINES
"""

def iter_lines(txt_or_txtdf,num_proc=1,**kwargs):
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

def parse(txt_or_txtdf,*x,**y):
    """
    Return parses
    """
    o=list(parse_iter(txt_or_txtdf,*x, **y))
    odf=pd.concat(o) if len(o) else pd.DataFrame()
    return odf.sort_index()


def parse_iter(
        txt_or_txtdf,
        by_line=True,
        by_syll=False,
        only_best=False,
        only_unbounded=True,
        num_proc=DEFAULT_NUM_PROC,
        progress=True,
        force=False,
        verbose=True,
        **kwargs):
    """
    Return parses as iter
    """
    if by_syll: by_line=False
    elif by_line: by_syll=False
#     if by_line: by_syll=False
#     if not by_syll: by_line=True
    yield from iter_parsed_lines(
        txt_or_txtdf,
        num_proc=num_proc,
        progress=progress,
        by_line=by_line,
        only_best=only_best,
        only_unbounded=only_unbounded,
        force=force,
        verbose=verbose,
        **kwargs
    )

def iter_parsed_lines(
        txt_or_txtdf,
        num_proc=DEFAULT_NUM_PROC,
        progress=False,
        by_line=False,
        only_best=False,
        only_unbounded=True,
        verbose=True,
        posthoc_constraints=True,
        rebound_parses=False,
        **kwargs
        ):
    # preproc
    preproc_gen = iter_lines(
        txt_or_txtdf,
        progress=progress if not verbose else False,
        desc='Metrically parsing lines',
        **kwargs#.get('kwargs',{})
    )
    
    # proc
    kwargs['only_unbounded']=only_unbounded
    kwargs['engine']=ENGINE
    proc_gen = parmap(
        do_iter_parsed_lines,
        preproc_gen,
        N=num_proc,
        kwargs=kwargs
    )
    
    # postproc
    postproc_func = partial(
        postproc_dfline,
        by_line=by_line,
        only_best=only_best,
        only_unbounded=only_unbounded,
        verbose=verbose,
        posthoc_constraints=posthoc_constraints,
        rebound_parses=rebound_parses
    )
    postproc_gen = map(postproc_func, proc_gen)
    
    # yield from total queue
    yield from postproc_gen

def do_iter_parsed_lines(
        linedf,
        num_proc=DEFAULT_NUM_PROC,
        force=True,
        cache=False,
        verbose=True,
        **kwargs):
    o=[]
    for linepart_i,linepartdf in sorted(linedf.groupby('linepart_i')):
        if kwargs.get('engine')==ENGINE_PROSODIC:
            odf=parse_prosodic_line(
                linepartdf,
                **kwargs
            )
        else:
            o=list(iter_parsed_combos(
                linepartdf,
                num_proc=1,
                progress=False,
                **kwargs
            ))  
            odf=pd.concat(o) if len(o) else pd.DataFrame()
        o+=[odf]
    odf=pd.concat(o) if len(o) else pd.DataFrame()    
    return odf
    


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



def parse_prosodic_line(txt_or_txtdf, lang='en',
                   meter='default_english', use_espeak=True,
                   constraints=None,constraint_weights=None,set_index=True,**kwargs):
    p.config['resolve_optionality']=1
    p.config['print_to_screen']=False
    p.config['en_TTS_ENGINE']='espeak' if use_espeak else 'none'
    p.config['num_bounded_parses_to_store']=NUM_BOUNDED_TO_STORE

    # print(constraints)
    # print(kwargs)
    
    meter_obj=p.config['meters'][meter]
    config=default_config=meter_obj.config
    if constraints is not None:
        constraints_pros=[
            f'{constraint_names_in_prosodic[c]}/{constraint_weights[i] if constraint_weights is not None else 1}'
            for c in constraints
        ]
        config['constraints']=constraints_pros
        meter_obj=p.Meter(config)
    
    txtdf = scan(txt_or_txtdf) if type(txt_or_txtdf)==str else txt_or_txtdf
    txtdf = txtdf.sort_index()
    
    line_words=[]
    plang=p.dict[lang]
    plang.getprep_syllabify_orth=None
    for wi0,wdf0 in txtdf.reset_index().groupby('word_i'):
        word_objs=[]
        for wi,wdf in wdf0.groupby('word_ipa_i'):
            ipa_str='.'.join(wdf.syll_ipa)
            sylls_text=list(wdf.syll_str)
            token = wdf.iloc[0].word_str
            #print(wi0,wi,token,ipa_str)
            word_obj = plang.make((ipa_str,sylls_text), token)
            word_obj.word_i=wi0
            word_obj.word_ipa_i=wi
            if wdf.is_funcword.iloc[0]==1: word_obj.feats['functionword']=True
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
        posthoc_constraints=True,
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
        parse_mstr=' '.join(parse_mstr)
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
                    parse_num_syll=len(parse_mstr),
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
            combo_stress=' '.join(g.syll_stress),
            combo_ipa=' '.join(
                '.'.join(wdf.syll_ipa)
                for wi,wdf in sorted(g.groupby('word_i'))
            )
        )
        for i,g in odf.groupby('parse_i')
    )
    #print('3')
    #display(odf)

    return odf




def rank_parses(dfparses):
    odf=dfparses
    odf[TOTALCOL]=odf[[col for col in odf.columns if col.startswith('*') and col!=TOTALCOL]].sum(axis=1)
    newrankdf=odf[['parse_i',TOTALCOL]].groupby('parse_i').sum().sort_values(TOTALCOL)
    newrankdf['ranks']=newrankdf[TOTALCOL].rank(method='dense')
    newrank=dict(zip(newrankdf.index, newrankdf.ranks))
    odf['parse_rank']=odf.parse_i.apply(lambda x: int(newrank.get(x,0)))
    return odf

def postproc_dfline(
        dfline,
        by_line=False,
        verbose=True,
        only_best=False,
        only_unbounded=False,
        posthoc_constraints=True,
        rebound_parses=False):
    #display(dfline)
    o=[]
    
    for i,dfg in sorted(dfline.groupby('linepart_i')):
        dfg=rank_parses(dfg)
        if rebound_parses: dfg=bound_parses(dfg,only_unbounded=only_unbounded)
        #odf=to_lines(dfg) if by_line else dfg#sort_by_total_and_syll(dfg)
        o+=[dfg]
    if verbose:
        odf=pd.concat(o) if len(o) else pd.DataFrame()
        display(show_parse(odf))
    if by_line:
        o=[to_lines(dfg) for dfg in o]
        odf=pd.concat(o) if len(o) else pd.DataFrame()
    
    if only_best and ('parse_rank' in set(odf.index.names) or 'parse_rank' in set(odf.columns)):
        # odf=odf[odf.parse_rank==1]
        odf=odf.query('parse_rank==1')
    return setindex(odf)

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
            ' '.join(x) if type(x)==str and x else ''
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




def parse_group(df,constraints=DEFAULT_CONSTRAINTS):
    """
    Actual parsing, interface to constraints
    """

    dfcols=set(df.columns)
    if not 'is_w' in dfcols: df['is_w']=[np.int(x=='w') for x in df.parse_syll]
    if not 'is_s' in dfcols: df['is_s']=[np.int(x=='s') for x in df.parse_syll]
    dfpc=apply_constraints(df)
    lkeys=[c for c in df.columns if c not in set(dfpc.columns)]
    return df[lkeys].join(dfpc)



"""
Summarizing by line
"""

def to_lines(rparses,totalcol=TOTALCOL,rankcol=PARSERANKCOL, agg=sum):
    # parses
    rcols=set(rparses.columns)
    pkcols = [c for c in PARSELINEKEY if c in rcols]
    # sum by actual data lines
    valcols = [c for c in parses.select_dtypes('number').columns
              if not c in pkcols
              if not c.endswith('_i')
              if not c.endswith('_ii')
              if not c in {'index','level_0'}
              ]
    aggfunc = dict((vc,sum) for vc in valcols)
    medians=['combo_num_syll','parse_num_syll','line_num_syll','parse_num_pos']
    for mx in medians:
        if mx in rcols:
            aggfunc[mx]=np.median
    lgby=['stanza_i','line_i','linepart_i']
    try:
        linesums = rparses.groupby(pkcols).agg(aggfunc)
    except Exception as e:
        print('!!',e)
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
        from IPython.display import Markdown
        return Markdown(show_parses_md(parses_bysyll))
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
                    md=f'<span style="color:darkred">{md}</span>'
                    # md=f'<i>{md}</i>'
                md=f'{wpref}{md}{wsuf}'
                mdword+=[md]
            mdrow.append(''.join(mdword))
        mdline.append(' '.join(mdrow))
    
    o=' '.join(mdline)#.replace('</u> <u>',' ')
    #print(o)
    #return f'<span style="color:darkblue">{o}</span>'
    return o

def show_parse(dfparse,only_best=True):
    #dfparse=resetindex(dfparse)
    if only_best:# dfparse=dfparse.query('parse_rank==1')
        best_idf=dfparse.groupby('parse_i')['*total'].mean().sort_values()
        best_i=list(best_idf.index)[0]
        dfparse=dfparse.query(f'parse_i=={best_i}')
    try:
        from IPython.display import Markdown
        return Markdown(show_parse_md(dfparse))
    except ImportError:
        return show_parse_txt(dfparse)
    

def show_parses_md(parses_bysyll):
    
    grps=sorted(parses_bysyll.reset_index().groupby(
        ['stanza_i','line_i']#,'linepart_i','parse_rank']    
    ))
    mdl=[show_parse_md(dfparse) for i,dfparse in grps]
    omd='\n<br/>'.join(mdl)
    return omd
    
    

