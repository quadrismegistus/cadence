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
#         for stanza_i,stanzadf in txt_or_txtdf.groupby('stanza_i'):
#             lines=stanzadf.groupby('line_i')
#             for line_,linedf in lines:
#                 yield linedf

def iter_combos(txtdf,num_proc=1):
    for dfline in iter_lines(txtdf,num_proc=num_proc):
        # ldf=resetindex(dfline)
        ldf=dfline.reset_index()
        linedf_nopunc = ldf[ldf.is_syll!=0]
        for dfi,dfcombo in enumerate(apply_combos(linedf_nopunc, 'word_i', 'word_ipa_i')):
            dfcombo['combo_i']=dfi
            dfcombo['combo_stress']=''.join(dfcombo.syll_stress)
            dfcombo['combo_syll_i']=list(index_by_truth(dfcombo.is_syll))
            dfcombo['combo_num_syll']=dfcombo['combo_syll_i'].max()+1
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
        only_unbounded=False,
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
        kwargs=kwargs
    )

def iter_parsed_lines(
        txt_or_txtdf,
        num_proc=DEFAULT_NUM_PROC,
        progress=False,
        by_line=False,
        only_best=False,
        only_unbounded=False,
        verbose=True,
        **kwargs
        ):
    # preproc
    preproc_gen = iter_lines(
        txt_or_txtdf,
        progress=progress if not verbose else False,
        desc='Metrically parsing lines',
        **kwargs.get('kwargs',{})
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
        verbose=verbose
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
    
    if cache:
        key=hashstr(str([
            x
            for x in pd.util.hash_pandas_object(
                linedf.reset_index(),
                index=False
            )
        ]))
        if not force:        
            with get_db('parses','r') as db:
                if key in db: return db[key]

#     odf=pd.DataFrame()
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
    
    if cache and len(odf):
        with get_db('parses','w') as db: db[key]=odf
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
        odf=parse_combo_cadence(linecombodf,**kwargs)
    return odf



def parse_prosodic_line(txt_or_txtdf, lang='en',
                   meter='default_english', use_espeak=True,
                   constraints=None,constraint_weights=None,**kwargs):
    p.config['resolve_optionality']=1
    p.config['print_to_screen']=False
    p.config['en_TTS_ENGINE']='espeak' if use_espeak else 'none'
    p.config['num_bounded_parses_to_store']=NUM_BOUNDED_TO_STORE
    
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
            word_objs.append(word_obj)
        wordtoken_obj = p.WordToken(word_objs, token)
        line_words.append(wordtoken_obj)
    l=p.Line()
    l.children = line_words
    l.parse(meter=meter_obj)
    odf=prosodic_line_to_data(l,txtdf,**kwargs)
    return setindex(odf,sort=True)
        

def prosodic_line_to_data(
        line,
        txtdf,
        viols_in_parse_str=True,
        total_col=TOTALCOL,
        only_unbounded=False,
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
        parse_str=parse_str.replace('|',' ')
        parse_mstr=' '.join(parse_mstr)
#         parse_str='|'.join(
#             x+'_' if not x.endswith('*') else x
#             for x in parse_str.split('|')
#         )
        bounded_by='' if is_unbounded else parse.boundedBy.str_meter()
        for pos_i,pos in enumerate(parse.positions):
            constraintd=dict(sorted(
                (constraint_names_from_prosodic.get(k.name,k.name),v)
                for k,v in pos.constraintScores.items()
            ))
            
            if total_col not in constraintd: constraintd[total_col]=sum(constraintd.values())
            constraintd['*clash']=np.nan
            constraintd['*lapse']=np.nan
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
        #if not len(o): yield pd.DataFrame()
        if not len(o): continue
        odf=pd.DataFrame(o)
        #print('1')
        #display(odf)
        
        odf=txtdf.reset_index().merge(
            odf,
            how='inner',
            on=['word_i','word_ipa_i','syll_i'],
            suffixes=['','_parse']
        )
        O+=[odf]

    ## add back combo data
    if not len(O): return pd.DataFrame()
    odf=pd.concat(O)
    #odf=setindex(pd.concat(O))
    #display(odf)
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






def postproc_dfline(
        dfline,
        by_line=False,
        verbose=True,
        only_best=False,
        only_unbounded=False):
    #display(dfline)
    o=[]
    if verbose: display(show_parse(dfline))
    
    for i,dfg in sorted(dfline.groupby('linepart_i')):
        odf=to_lines(dfg) if by_line else sort_by_total_and_syll(dfg)
        odf=bound_parses(odf,only_unbounded=only_unbounded)
        o+=[odf]
    odf=pd.concat(o) if len(o) else pd.DataFrame()
#     display(odf)
    #stop
    
    if only_best and 'parse_rank' in set(odf.index.names) or 'parse_rank' in set(odf.columns):
        odf=odf.query('parse_rank==1')
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
    odfg=odf=odforig.reset_index()
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
    if only_unbounded: odf=odf[odf.ds_bounded!=True]
    # re-rank
    #display(odf)
    odf.parse_rank=odf.parse_rank.rank(ascending=True,method='dense').apply(int)
    
    return setindex(odf)

def iter_combos_as_lines(parsed_line_iter,by_line=False,only_best=False):
    for dfline in parsed_line_iter:
        lineiter=to_lines(dfline) if by_line else sort_by_total_and_syll(dfline)
        for x in lineiter:
            if only_best:
                try:
                    yield x.query('parse_rank==1')
                except Exception:
                    yield x
            else:
                yield x
        

#     lineinow=None
#     combos=[]
#     for dfcombo in iter_combo:
#         if not 'line_i' in set(dfcombo.columns):continue
#         combo_linei=dfcombo.line_i.iloc[0]
#         if lineinow is not None and lineinow!=combo_linei and combos:
#             dfline=pd.concat(combos)
#             yield sort_by_total_and_syll(dfline) if not by_line else to_lines(dfline)
#             combos=[]
#         lineinow=combo_linei
#         combos.append(dfcombo)
#     if len(combos):
#         dfline=pd.concat(combos)
#         yield sort_by_total_and_syll(dfline) if not by_line else to_lines(dfline)
        



def sort_by_total_and_syll(dfline,key=LINEKEY,sortcol='sort_parse_viols',rankcol=PARSERANKCOL,totalcol='*total'):
    dfline=resetindex(dfline)
    gcols=[
        'stanza_i',
        'line_i',
        'combo_i',
        'parse_i',
    ]
    dflnsum = dfline.groupby(gcols).sum().sort_values(totalcol)
    ranks = dflnsum[totalcol].rank(method='dense').apply(int)
    indices = [
        tuple(int(row.get(gc)) for gc in gcols)
        for i,row in dflnsum.reset_index().iterrows()
    ]
    dfline[rankcol]=dfline.reset_index().apply(
        lambda row: ranks.iloc[
            indices.index(tuple(int(row.get(gc)) for gc in gcols))
        ],
        axis=1
    )
    #dfline[rankcol]=dfline[rankcol].rank(method='dense')
    # dfline[sortcol] = list(zip(dfline[rankcol], dfline.parse_syll_i))
    odf=setindex(dfline,sort=True)
    # odf=odf.sort_values(sortcol)
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

def to_lines(parses,totalcol=TOTALCOL,rankcol=PARSERANKCOL, agg=sum):
    # parses
    #parses=pd.DataFrame(parses)
    #rparses=resetindex(parses)
    rparses=parses.reset_index()
    rcols=set(rparses.columns)
    pkcols = [c for c in PARSELINEKEY if c in rcols]
    #print('pkcols',pkcols)
    # sum by actual data lines
    valcols = [c for c in parses.select_dtypes('number').columns
              if not c in pkcols
              if not c.endswith('_i')
              if not c.endswith('_ii')
              if not c in {'index','level_0'}
              ]
    #print('valcols',valcols)
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
    #print('linesums')
    #display(linesums)
        
    o=[]
    for i,g in linesums.groupby(lgby):
        g=g.sort_values([totalcol,'combo_i'])
        g[rankcol]=[i+1 for i in range(len(g))]
        g[rankcol+'_min']=g[totalcol].rank(method='min').apply(int)
        g[rankcol+'_dense']=g[totalcol].rank(method='dense').apply(int)
        o.append(g)
    linesums=pd.concat(o)
    linesums = setindex(linesums,key=PARSELINEKEY,sort=True)
    return linesums
    
def iter_parses(*x,by_line=True,**y):
    yield from iter_parsed_lines(*x,by_line=by_line,**y)
    
    
    
    
"""
PROSODIC FUNCTIONS
"""








"""
UTILS
"""







def is_ok_parse(parse,maxS=2,maxW=2):
    return ('s'*(maxS+1)) not in parse and ('w'*(maxW+1)) not in parse


def possible_parses(window_len,maxS=2,maxW=2):
    poss = list(product(*[('w','s') for n in range(window_len)]))
    poss = [''.join(x) for x in poss]
    poss = [x for x in poss if is_ok_parse(x)]
    poss = [x for x in poss if len(x)==window_len]
    return poss

def possible_parses_recursive(window_len,starter=[],maxS=2,maxW=2,allow_overshooting=False,as_you_go=False):
    wtypes = [tuple(['w']*n) for n in range(1,maxW+1)]
    stypes = [tuple(['s']*n) for n in range(1,maxS+1)]
    if as_you_go and starter: yield starter
    if not starter:
        for typ in wtypes + stypes:
            yield from possible_parses_recursive(window_len,starter=[typ])
    else:
        lenn=sum(len(x) for x in starter)
        if lenn>window_len:
            if allow_overshooting:  # does not match syll count but overshoots it
                yield starter 
        elif lenn==window_len:  # exact match
            yield starter #tuple([tuple(x) for x in starter])
        else:
            if starter[-1][-1]=='s':
                for wtype in wtypes:
                    yield from possible_parses_recursive(window_len,starter=starter+[wtype])
            else:
                for stype in stypes:
                    yield from possible_parses_recursive(window_len,starter=starter+[stype])

def possible_metrical_positions(window_len,**y):
    return possible_parses_recursive(window_len,**y)


### Data by foot
def possible_metrical_feet(num_sylls,maxS=2,maxW=2):
    """
    Creates a hierarchical index of possible metrical parses
    """

    l = list(possible_parses_recursive(num_sylls,maxS=maxS,maxW=maxW))
    # return as data
    ld=[]
    for parse_i,parse in enumerate(l):
        tlen=sum(len(x) for x in parse)
        parse_str = ''.join([''.join(pos) for pos in parse])
        d={
            'parse':parse_str,
#             'pos':''.join(pos),
            'num_pos':len(parse),
            'num_syll':tlen
        }
        
        for pos_i,pos in enumerate(parse):
            d[f'mpos_{pos_i}']=''.join(pos)
        ld.append(d)
    df=pd.DataFrame(ld).fillna('')
    indices = [c for c in df.columns if c.startswith('mpos_')]
    return df.set_index(indices)



### Data by syllable
def possible_metrical_feet_bysyll(num_sylls,maxS=2,maxW=2):
    l = possible_parses_recursive(num_sylls,maxS=maxS,maxW=maxW)
    ld=[]
    for parse_i,parse in enumerate(l):
        num_syll=sum(len(x) for x in parse)
        num_pos=len(parse)
        parse_str = ''.join([''.join(pos) for pos in parse])
        parse_sofar=''
        parse_sofar_bysyll=''

        si=0
        for pos_i,pos in enumerate(parse):
            pos_str=''.join(pos)
            parse_sofar+=pos_str
            for syll_i,syll in enumerate(pos):
                parse_sofar_bysyll+=syll
                d={
                    'parse_i':parse_i,
                    'parse':parse_str,
                    # 'parse_sofar_bypos':parse_sofar,
                    # 'parse_sofar_bysyll':parse_sofar_bysyll,
                    'parse_num_pos':num_pos,
                    'parse_num_syll':num_syll,
                    'parse_pos_i':pos_i,
                    'parse_pos':pos_str,
                    'parse_syll_i':si,
                    'parse_syll':syll
                }
                si+=1
                ld.append(d)
    df=pd.DataFrame(ld)
    return df
### Data by foot
def possible_metrical_feet_bypos(num_sylls,maxS=2,maxW=2):
    """
    Creates a hierarchical index of possible metrical parses
    """

    l = possible_parses_recursive(num_sylls,maxS=maxS,maxW=maxW)
    ld=[]
    for parse_i,parse in enumerate(l):
        tlen=sum(len(x) for x in parse)
        parse_str = ''.join([''.join(pos) for pos in parse])
        for pos_i,pos in enumerate(parse):
            d={
                'parse_i':parse_i,
                'parse':parse_str,
                'parse_num_pos':len(parse),
                'parse_num_syll':tlen,
                'parse_pos_i':parse_pos_i,
                'parse_pos':''.join(pos)
            }
            ld.append(d)
    df=pd.DataFrame(ld)
    return df


POSSD={}
def get_poss_df(nsyll):
    global POSSD
    if not nsyll in POSSD: POSSD[nsyll]=possible_metrical_feet_bysyll(nsyll)
    return POSSD[nsyll]






"""
Metrical positions
"""

def iter_unique_metrical_positions(linecombodf):
    lcdf=linecombodf.reset_index()
    numsyll=len(lcdf)
    poss=[]
    poss_parses=possible_metrical_positions(numsyll)
    for parse in poss_parses:
        posi=0
        for i,pos in enumerate(parse):
            o=( (posi,posi+len(pos)), pos, i)
            poss+=[o]
            posi+=len(pos)
    
    for unique_mpos in sorted(list(set(poss))):
        indices,pos,posi = unique_mpos
        posdf = lcdf.iloc[indices[0] : indices[1]]
        posdf = pd.DataFrame(posdf)
        posdf['parse_syll'] = pos
        posdf['parse_pos'] = ''.join(pos)
        posdf['parse_pos_i'] = posi
        yield posdf


def iter_parsed_metrical_positions(linecombodf):
    for posdf in iter_unique_metrical_positions(linedf):
        yield parse_group(posdf)


def get_parsed_metrical_positions(linecombodf):
    return setindex(pd.concat(iter_parsed_metrical_positions(linecombodf)))


"""
Positions -> Parses
"""

def parse_combo_cadence(linecombodf, **kwargs):
    lfpc=linecombodf.reset_index()
    # setup
    numsyll=len(lfpc)
    done=set()
    # parse just the positions
    dfpm = get_parsed_metrical_positions(lfpc)
    dfpmr=resetindex(dfpm)
    dfposs=get_poss_df(numsyll)

    # join with parsed positions
    dfjoin=setindex(dfpmr.merge(dfposs, left_on=['combo_syll_i','parse_pos_i','parse_syll','parse_pos'], right_on=['parse_syll_i','parse_pos_i','parse_syll','parse_pos']))
    
    # concat on way out
    o=[]
    for parse,parsedf in dfjoin.groupby(level=['combo_i','parse_i']):
        if not is_ok_parse(parse): continue
        pdf=resetindex(parsedf).drop_duplicates(['parse_syll_i','parse_syll','parse_pos_i','parse_pos'])
        if not is_valid_mpos_combo(pdf,numsyll): continue
        pdf['parse_str']='|'.join(
            '.'.join(wdf.apply(lambda row: row.syll_str.upper() if row.is_s else row.syll_str.lower(), axis=1))
            for wi,wdf in sorted(pdf.groupby('parse_pos_i'))
        )
        o+=[pdf]
    odf=setindex(pd.concat(o))
    return odf

def is_valid_mpos_combo(parsedf,numsyll):
    if len(set(parsedf.combo_syll_i))!=numsyll: return False
    return True

def get_num_lines(txt_or_txtdf,splitter='\n',groupby=['stanza_i','line_i']):
    if txt_or_txtdf is None:
        return np.nan
    if type(txt_or_txtdf)==str:
        return len([x for x in txt_or_txtdf.split(splitter) if x.strip()])
    elif type(txt_or_txtdf)==pd.DataFrame:
        return len(txt_or_txtdf.groupby(groupby))
    return np.nan

def get_num_stanzas(txt_or_txtdf):
    return get_num_lines(txt_or_txtdf,splitter='\n\n',groupby='stanza_i')



def parse_line(linedf):
    """
    Line DF -> Combos -> Parsed -> Concat
    """
    return setindex(pd.concat(parse_combo(combo) for combo in iter_combos(linedf)))




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
                
                if row.is_s:
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
                    #md=f'<span style="color:darkred">{md}</span>'
                    md=f'<i>{md}</i>'
                md=f'{wpref}{md}{wsuf}'
                mdword+=[md]
            mdrow.append(''.join(mdword))
        mdline.append(' '.join(mdrow))
    
    o=' '.join(mdline)#.replace('</u> <u>',' ')
    #print(o)
    #return f'<span style="color:darkblue">{o}</span>'
    return o

def show_parse(dfparse,only_best=True):
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
    
    



