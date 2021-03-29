from ..imports import *
from .txtparsing import *


"""
ITER LINES
"""

def iter_lines(txtdf):
    for stanza_i,stanzadf in txtdf.groupby('stanza_i'):
        lines=stanzadf.groupby('line_i')
        for line_,linedf in lines:
            yield linedf

def iter_combos(txtdf):
    for dfline in iter_lines(txtdf):
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
            yield setindex(dfcombo)

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
    for posdf in iter_unique_metrical_positions(linecombodf):
        yield parse_group(posdf)


def get_parsed_metrical_positions(linecombodf):
    return setindex(pd.concat(iter_parsed_metrical_positions(linecombodf)))


"""
Positions -> Parses
"""

def parse_combo(linecombodf):
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

def iter_parsed_combos(txtdf,num_proc=DEFAULT_NUM_PROC,progress=True):
    yield from pmap_iter_groups(
        parse_combo,
        get_all_combos(txtdf).groupby(['stanza_i','line_i','combo_i']),
        num_proc=num_proc,
        progress=progress,
        desc='Metrically parsing lines (+word IPA combinations)'
    )


def parse_line(linedf):
    """
    Line DF -> Combos -> Parsed -> Concat
    """
    return pd.concat(parse_combo(combo) for combo in iter_combos(linedf))


def iter_parsed_lines(txtdf,num_proc=DEFAULT_NUM_PROC,progress=True,data_by_line=False):
    yield from iter_combos_as_lines(
        iter_parsed_combos(
            txtdf,
            num_proc=num_proc,
            progress=progress
        ),
        data_by_line=data_by_line
    )        


def iter_combos_as_lines(iter_combo,data_by_line=False):
    lineinow=None
    combos=[]
    for dfcombo in iter_combo:
        combo_linei=dfcombo.line_i.iloc[0]
        if lineinow is not None and lineinow!=combo_linei and combos:
            dfline=pd.concat(combos)
            yield sort_by_total_and_syll(dfline) if not data_by_line else to_lines(dfline)
            combos=[]
        lineinow=combo_linei
        combos.append(dfcombo)
    if len(combos):
        dfline=pd.concat(combos)
        yield sort_by_total_and_syll(dfline) if not data_by_line else to_lines(dfline)
        



def sort_by_total_and_syll(dfline,key=LINEKEY,sortcol='sort_parse_viols',rankcol=PARSERANKCOL,totalcol='*total'):
    dfline=resetindex(dfline)
    gcols=[
        'stanza_i',
        'line_i',
        'combo_i',
        'parse_i',
    ]
    dflnsum = dfline.groupby(gcols).sum().sort_values(totalcol)
    ranks = dflnsum[totalcol].rank(method='min').apply(int)
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
    # dfline[sortcol] = list(zip(dfline[rankcol], dfline.parse_syll_i))
    odf=setindex(dfline,sort=True)
    # odf=odf.sort_values(sortcol)
    return odf


def parse_iter(txtdf,
        data_by_line=False,data_by_syll=True,
        num_proc=DEFAULT_NUM_PROC,progress=True):
    """
    Return parses as iter
    """
    if data_by_syll: data_by_line=False
    yield from iter_parsed_lines(txtdf,num_proc=num_proc,progress=progress,data_by_line=data_by_line)

def parse(txtdf,*x,**y):
    """
    Return parses
    """
    return pd.concat(parse_iter(txtdf,*x, **y))




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
    
    linesums = resetindex(rparses.groupby(pkcols).agg(aggfunc))
    linesums[rankcol] = linesums.groupby(['stanza_i','line_i'])[totalcol].rank(method='min').apply(int)
    # linesums=linesums.sort_values(['stanza_i','line_i',rankcol])
    linesums = setindex(linesums,key=PARSELINEKEY,sort=True)
    return linesums