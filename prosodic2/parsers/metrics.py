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

def iter_combos(dfline):
    for dfline in iter_lines(dfline):
        ldf=dfline.reset_index()
        linedf_nopunc = ldf[ldf.word_ipa!=""]
        for dfi,dfcombo in enumerate(apply_combos(linedf_nopunc, 'word_i', 'word_ipa_i')):
            dfcombo['combo_i']=dfi
            dfcombo['line_stress']=''.join(dfcombo.syll_stress)
            dfcombo['combo_syll_i']=list(index_by_truth(dfcombo.is_syll))
            dfcombo['combo_num_syll']=dfcombo['combo_syll_i'].max()+1
            dfcombo['line_ipa']=' '.join(
                '.'.join(wdf.syll_ipa)
                for wi,wdf in sorted(dfcombo.groupby('word_i'))
            )
            yield setindex(dfcombo)

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
                'num_pos':len(parse),
                'num_syll':tlen,
                'pos_i':pos_i,
                'pos_parse':''.join(pos)
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
        posdf['syll_parse'] = pos
        posdf['pos_parse'] = ''.join(pos)
        posdf['pos_i'] = posi
        yield posdf


def iter_parsed_metrical_positions(linecombodf):
    for posdf in iter_unique_metrical_positions(linecombodf):
        yield parse_group(posdf)


def get_parsed_metrical_positions(linecombodf):
    return setindex(pd.concat(iter_parsed_metrical_positions(combodf)


def is_valid_combo(dfcombo,numsyll=None):
    dfnodup=dfcombo.reset_index().drop_duplicates(['syll_i','pos_i'])
    if len(dfnodup)!=len(dfcombo): return False
    return True
def is_valid_parse(parse,parsedf,numsyll):
    if not is_ok_parse(parse): return False
    if len(set(parsedf.combo_syll_i))!=numsyll: return False
    return True


def parse_combo(linecombodf):
    lfpc=linecombodf.reset_index()
    # setup
    numsyll=len(lfpc)
    done=set()
    
    # parse just the positions
    dfpm = get_parsed_metrical_positions(lfpc)
    dfpmr=dfpm.reset_index()
    dfposs=get_poss_df(numsyll)

    # join with parsed positions
    dfjoin=setindex(dfpmr.merge(dfposs, left_on=['combo_syll_i','pos_i','syll_parse','pos_parse'], right_on=['parse_syll_i','parse_pos_i','parse_syll','parse_pos']))
    
    # concat on way out
    o=[]
    for parse,parsedf in dfjoin.groupby(level='parse'):
        pdf=parsedf.drop_duplicates(['parse_syll_i','parse_syll','parse_pos_i','parse_pos'])
        if not is_valid_parse(parse,pdf,numsyll): continue
        o+=[pdf]
    return pd.concat(o)




def iter_poss_parses(df_window):
    df=df_window
    num_sylls = len(df.reset_index().query('word_ipa!=""'))
    for posi,pparse in enumerate(possible_parses(num_sylls)):
        df['parse_i']=posi
        df['parse_ii']=list(range(len(pparse)))
        df['parse']=pparse
        df['syll_parse']=list(pparse)
        df['is_w']=[np.int(x=='w') for x in pparse]
        df['is_s']=[np.int(x=='s') for x in pparse]
        yield setindex(df)



def parse_group(df,constraints=DEFAULT_CONSTRAINTS):
    dfcols=set(df.columns)
    if not 'is_w' in dfcols: df['is_w']=[np.int(x=='w') for x in df.syll_parse]
    if not 'is_s' in dfcols: df['is_s']=[np.int(x=='s') for x in df.syll_parse]
    dfpc=apply_constraints(df)
    lkeys=[c for c in df.columns if c not in set(dfpc.columns)]
    return df[lkeys].join(dfpc)



def iter_parsed(df):
    iter=iter_poss_parses(df)
    for pi,dfp in enumerate(iter):
        dfpc=parse_group(dfp)
        yield dfpc


def iter_parsed_windows(df):
    for window in iter_windows(df):
        for parsed in iter_parsed(window):
            yield parsed


def get_parsed_windows(txtdf):
    # get all combos
    return pmap_groups(
        iter_parsed_windows,
        txtdf.groupby(['stanza_i','line_i']),
        progress=True,
        num_proc=7,
        desc='Parsing all windows'
    )



"""
Line -> Stanzas
"""


def summarize_by_syll_pos(df_parsed_windows_of_line,num_syll=10000):
    df=df_parsed_windows_of_line
    qcols=['stanza_i','line_i','line_ii','syll_parse']
    dfr=df[[x for x in df.columns if not x in df.index.names]].reset_index()
    icols=[x for x in dfr.columns if x.endswith('_i') or x.endswith('_ii')]
    dfr_i=dfr[set(icols) | set(qcols)]
    dfr_x=dfr[(set(dfr.columns) - set(icols)) | set(qcols)]
    odf_x=dfr_x.groupby(qcols).mean()
    odf_i=dfr_i.groupby(qcols).count()
    odf=odf_x#.join(odf_i)
    return odf.reset_index()



def apply_combos_meter(dfsyll,group1='line_ii',group2='syll_parse',combo_key='line_parse_i',num_syll=None):
    # combo of indices?
    df=dfsyll

    # ok
    combo_opts = [
        [(mtr,mdf.mean()) for mtr,mdf in sorted(df.groupby(group2))]
        for i,grp in sorted(df.groupby(group1))
    ]

    # is valid?
    combos = product(*combo_opts)
    vci=-1
    done=set()
    for ci,combo in enumerate(combos):
        cparse = ''.join(i for i,x in combo)
        cparse=cparse[:num_syll]
        if cparse in done: continue
        if not is_ok_parse(cparse): continue
        vci+=1
        odf=pd.DataFrame(x for i,x in combo)
        odf['parse_i']=vci
        odf['parse']=cparse
        if type(odf)!=pd.DataFrame or not len(odf): continue
        yield odf
        done|={cparse}

def iter_parsed_lines(df_parsed_windows_of_line):
    numsyll=df_parsed_windows_of_line.num_syll.iloc[0]
    dfsyll = summarize_by_syll_pos(df_parsed_windows_of_line,num_syll=numsyll)
    iterr = apply_combos_meter(dfsyll,num_syll=numsyll)
    yield from iterr

def get_parsed_lines(dfpw,summarized=True):
    df=pmap_groups(
        iter_parsed_lines,
        dfpw.groupby(level=['stanza_i','line_i']),
        num_proc=1,
        progress=True
    )
    
    badcols = [c for c in df.columns if c.startswith('word_') or c.startswith('syll_') or c=='line_ii']
    df=df[set(df.columns) - set(badcols)]
    qkey=['stanza_i','line_i','parse_i','parse']
    df=df.groupby(qkey).mean().sort_index()
    df=df.sort_values(['stanza_i','line_i','*total'])
    return df


def get_info_byline(txtdf):
    linedf=txtdf.xs([0,0,0],level=['word_i','word_ipa_i','syll_i'])
    linedf=linedf.reset_index(level=['word_str','word_ipa','syll_str','syll_ipa','line_ii'],drop=True)
    return linedf#.reset_index().set_index(['stanza_i','line_i'])





def parse(txtdf):
    # already loaded, right?
    if type(txtdf)==str: txtdf=load(txtdf)
    # parse windows
    df_parsed_windows = get_parsed_windows(txtdf)
    # put into lines
    dfparsedlines = get_parsed_lines(df_parsed_windows)
    # get info by line and join
    linedf=get_info_byline(txtdf)
    odf=setindex(joindfs(dfparsedlines, linedf))
    return odf.sort_values('*total')

