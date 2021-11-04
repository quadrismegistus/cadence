

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



def parse_line(linedf,engine=ENGINE,**kwargs):
    """
    Line DF -> Combos -> Parsed -> Concat
    """
    if engine==ENGINE_PROSODIC:
        return parse_prosodic_line(linedf,**kwargs)
    else:
        return setindex(pd.concat(parse_combo(combo) for combo in iter_combos(linedf)))






def apply_constraints_cadence(mpos_window,constraints=DEFAULT_CONSTRAINTS):
    total=None
    assert len(set(mpos_window.parse_pos_i))==1
    dfc=pd.DataFrame(index=mpos_window.index)
    for cname,cfunc in constraints.items():
        cvals=cfunc(mpos_window)
        dfc['*'+cname]=cvals
    dfc['*total']=dfc.sum(axis=1)
    return dfc




# default constraints
DEFAULT_CONSTRAINTS_FUNC = {
    'w/peak':no_weak_peaks,
    'w/stressed':no_stressed_weaks,
    's/unstressed':no_unstressed_strongs,
    # 's/trough':no_strong_troughs,
    'clash':no_clash,
    'lapse':no_lapse,
    'f-res':f_resolution,
    'w-res':w_resolution,
}