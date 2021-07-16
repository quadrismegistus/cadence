from ..imports import *
from .txtparsing import *


"""
ITER LINES
"""

def iter_lines(txt_or_txtdf,num_proc=1,**kwargs):
    if type(txt_or_txtdf) == str:
        yield from scan_iter(txt_or_txtdf,num_proc=num_proc,**kwargs)
    else:
        for i,g in txt_or_txtdf.groupby(['stanza_i','line_i','linepart_i']):
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

def parse_combo(linecombodf,engine=ENGINE):
    if engine==ENGINE_PROSODIC:
        odf=parse_prosodic(linecombodf)
    else:
        odf=parse_combo_cadence(linecombodf)
    return odf
    
def parse_combo_cadence(linecombodf):
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

def get_num_lines(txt_or_txtdf):
    if type(txt_or_txtdf)==str:
        return len([x for x in txt_or_txtdf.split('\n') if x.strip()])
    return len(txt_or_txtdf)



def iter_parsed_combos(txtdf,num_proc=DEFAULT_NUM_PROC,progress=False,**kwargs):    
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
                num_proc=num_proc,
                #progress=progress,
                progress=True,
                desc='Metrically parsing lines (+word IPA combinations)'
            )
        except ValueError:
            yield linedf


def parse_line(linedf):
    """
    Line DF -> Combos -> Parsed -> Concat
    """
    return setindex(pd.concat(parse_combo(combo) for combo in iter_combos(linedf)))

def do_iter_parsed_lines(
        linedf,
        num_proc=DEFAULT_NUM_PROC,
        force=False,
        **kwargs):
    
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
            
    print(num_proc)
    o=list(iter_parsed_combos(
        linedf,
        num_proc=num_proc,
        progress=False,
        **kwargs
    ))  
    if len(o):
        odf=pd.concat(o)
        with get_db('parses','w') as db:
            db[key]=odf
        return odf
    return pd.DataFrame()
    

def iter_parsed_lines(
        txt_or_txtdf,
        num_proc=DEFAULT_NUM_PROC,
        progress=False,
        by_line=False,
        only_best=False,
        **kwargs
        ):
    
    def iterr():
        for linedf in tqdm(
                iter_lines(txt_or_txtdf),
                disable = True, #not progress,
                total = get_num_lines(txt_or_txtdf)
            ):
            yield do_iter_parsed_lines(
                linedf,
                num_proc=num_proc,
                **kwargs
            )
    iterr2 = iter_combos_as_lines(
        iterr(),
        by_line=by_line
    )
    for x in iterr2:
        if only_best:
            try:
                x2=x.reset_index()
                yield x.query('parse_rank==1')
            except Exception:
                yield x
        else:
            yield x
            
        



#     yield from iter_combos_as_lines(
#         iter_parsed_combos(
#             txtdf,
#             num_proc=num_proc,
#             progress=progress,
#             **kwargs
#         ),
#         by_line=by_line
#     )        


def iter_combos_as_lines(parsed_line_iter,by_line=False):
    for dfline in parsed_line_iter:
        if by_line:
            yield to_lines(dfline)
        else:
            yield sort_by_total_and_syll(dfline)
        

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


def parse_iter(txt_or_txtdf,
        by_line=False,by_syll=True,only_best=False,
        num_proc=DEFAULT_NUM_PROC,progress=True,force=False,**kwargs):
    """
    Return parses as iter
    """
    if by_line: by_syll=False
    elif not by_syll: by_line=True
    yield from iter_parsed_lines(
        txt_or_txtdf,
        num_proc=num_proc,
        progress=progress,
        by_line=by_line,
        only_best=only_best,
        force=force,
        kwargs=kwargs
    )

def parse(txt_or_txtdf,*x,**y):
    """
    Return parses
    """
    o=list(parse_iter(txt_or_txtdf,*x, **y))
    return pd.concat(o) if len(o) else pd.DataFrame()




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
    parses=pd.DataFrame(parses)
    rparses=resetindex(parses)
    pkcols = [c for c in PARSELINEKEY if c in set(rparses.columns)]
    # sum by actual data lines
    valcols = [c for c in parses.select_dtypes('number').columns
              if not c in pkcols
              if not c.endswith('_i')
              if not c.endswith('_ii')
              if not c in {'index','level_0'}
              ]
    aggfunc = dict((vc,sum) for vc in valcols)
    aggfunc['combo_num_syll']=np.median
    aggfunc['parse_num_syll']=np.median
    aggfunc['parse_num_pos']=np.median
    aggfunc['line_num_syll']=np.median
    
    lgby=['stanza_i','line_i','linepart_i']
    try:
        linesums = resetindex(rparses.groupby(pkcols).agg(aggfunc))
    except Exception:
        return pd.DataFrame()
        
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



def prosodic_line_to_data(line,viols_in_parse_str=True, total_col='*total'):
    parse_i2=1
    for parse_i,parse in enumerate(line.allParses()):
        o=[]
        parse_str=parse.posString(viols=viols_in_parse_str)
        parse_mstr=parse.str_meter()
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
                    parse_i=parse_i2,
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
                )
                o.append(odx)
        yield pd.DataFrame(o)
        parse_i2+=1

def parse_prosodic(txt_or_txtdf, lang='en',
                   meter='default_english', use_espeak=True,
                   constraints=None,constraint_weights=None):
    
    p.config['resolve_optionality']=0
    p.config['print_to_screen']=True
    p.config['en_TTS_ENGINE']='espeak' if use_espeak else 'none'
    
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
    
    o=[]
    for combo_i,combodf in sorted(txtdf.groupby('combo_i')):
        combodf=combodf.reset_index()
        words=[]
        for wi,wdf in combodf.groupby('word_i'):
            ipa_str='.'.join(wdf.syll_ipa)
            sylls_text=list(wdf.syll_str)
            token = wdf.iloc[0].word_str
            word_obj = p.dict[lang].make((ipa_str,sylls_text), token)
            wordtoken_obj = p.WordToken([word_obj], token)
            words.append(wordtoken_obj)
        
        l=p.Line()
        l.children = words
        
        l.parse(meter=meter_obj)
        for parsedf in prosodic_line_to_data(l):
            yield pd.concat([combodf,parsedf],axis=1)
        

