from ..imports import *

SBY=csby=['combo_i','word_i','syll_i']
LINEKEY=[
    'stanza_i','line_i',
    'combo_i','parse_i','combo_parse_i',
    
    'word_i','word_str','word_ipa_i','word_ipa',
    'syll_i','syll_str','syll_ipa',
    
    'syll_parse','window_ii','mpos_parse',
    
    'window_key','window_i','window_ii',
]

PARSELINEKEY=[
'stanza_i','line_i',
'combo_parse_i',
'line_str',
'line_ipa',
'meter',
'stress'
]




def parse_lines(df_phon,num_proc=1,keep_best=KEEP_BEST,**y):
    yield from pmap_groups(
        parse_line,
        df_phon.groupby(['stanza_i','line_i']),
        num_proc=num_proc,
        kwargs=dict(keep_best=keep_best,num_proc=1),
        progress=True,
        desc='Parsing lines',
        **y
    )

def window_types(maxS=2,maxW=2):
    spos = [['s']*n for n in range(1,maxS+1)]
    wpos = [['w']*n for n in range(1,maxS+1)]
    pos = wpos + spos
    return list()



def line2combos(line_df,**y):
    line_df=line_df.reset_index()
    word_rows = [
        set(list(zip(word_df.word_i, word_df.word_ipa_i)))                
        for word_i,word_df in sorted(line_df.groupby('word_i'))
    ]

    dfww=line_df#.groupby(['word_i','word_ipa_i'])
    ii2row=defaultdict(list)
    for i,row in line_df.iterrows():
        ik=(row.word_i, row.word_ipa_i)
        ii2row[ik]+=[row]
        
    o=[]
    for ci,combo in enumerate(product(*word_rows)):
        combo_rows = [
            y
            for x in combo
            for y in ii2row[x]
        ]
        combodf = pd.DataFrame(combo_rows).sort_values(['word_i','syll_i'])
        combodf['combo_i']=ci
        # combodf['window_key']=get_window_keys(combodf)
        o+=[combodf]
    odf=pd.concat(o)
    odf=setindex(odf,LINEKEY)
    return odf


def get_unique_windows(df_combos,window_len=3,rolling=True):
    allwindows={}

    for ci,dfcombo in df_combos.reset_index().groupby('combo_i'):
        combo_windows = get_windows_in_combo(dfcombo, window_len=window_len, rolling=rolling)
        for window_key,windowdf in combo_windows:
            #print(window_key)
            #display(windowdf)
            #print()
            if not window_key in allwindows:
                allwindows[window_key]=windowdf
    dfo=pd.concat(allwindows.values()).drop('combo_i',1).drop('stanza_i',1).drop('line_i',1).drop_duplicates()
    return setindex(dfo,['window_key','window_ii'] + LINEKEY)

def possible_parses(window_len,maxS=2,maxW=2):
    poss = list(product(*[('w','s') for n in range(window_len)]))
    poss = [''.join(x) for x in poss]
    poss = [x for x in poss if is_ok_parse(x,maxS=maxS,maxW=maxW)]
    poss = [x for x in poss if len(x)==window_len]
    poss = list(set(poss))
    return poss


def setindex(df,key):
    cols=[]
    for x in key:
        if not x in set(cols) and x in set(df.columns):
            cols.append(x)
    return df.sort_values(cols).set_index(cols).sort_index()


def get_metrical_possibilities(df_uniq_windows,maxS=2,maxW=2):
    df=pd.DataFrame()
    dfuq=df_uniq_windows.reset_index()
    for window_i,wdf in dfuq[~dfuq.syll_i.isna()].groupby('window_key'):
        wdf=wdf.sort_values('window_ii')
        # display(wdf)
        # print(len(wdf))
        # stop
        posnum=len(wdf)
        for pi,poss_parse in enumerate(possible_parses(posnum, maxS=maxS,maxW=maxW)):
            wdf2=pd.DataFrame(wdf)
            # wdf2['parse_i']=pi
            wdf2['mpos_parse']=str(poss_parse)
            wdf2['window_ii']=list(range(len(wdf2)))
            wdf2['syll_parse']=list(poss_parse)
            wdf2['is_w']=(wdf2['syll_parse']=='w').apply(np.int32)
            wdf2['is_s']=(wdf2['syll_parse']=='s').apply(np.int32)
            df=df.append(wdf2)
    return setindex(df,['window_key','mpos_parse','window_ii','syll_parse'] + LINEKEY)

def join(x,y,on=['id'],how='outer'):
    # x=x.reset_index()
    # y=y.reset_index()
    if type(on)==str: on=[on]
    xkeys=on + [c for c in x.columns if c not in set(on) and c not in set(y.columns)]
    return x[xkeys].set_index(on).join(y.set_index(on),how=how)

def merge(x,y,on=[],left_on=[],right_on=[],how='outer'):
    if type(on)==str: on=[on]
    if on: left_on,right_on=on,on
    if not (left_on and right_on): return 
    
    xcols = set(x.columns)
    ycols = set(y.columns)
    
    return x[xcols | set(left_on)].merge(
        y[(ycols - xcols) | set(right_on)],
        left_on=left_on,
        right_on=right_on,
        how=how
    )

def parse_windows(df_metrical_poss,num_proc=1,progress=False,**y):
    df_metrical_poss=df_metrical_poss.reset_index()
    # parse
    out = pmap_groups(
        do_parse_window,
        df_metrical_poss.groupby(['window_key','mpos_parse']),
        num_proc=num_proc,
        progress=progress,
        desc='Parsing all combinations for line',
        **y
    )
    df_parsed_windows=pd.concat(out)#.sort_values(['window_i','mpos_parse','word_i','syll_i'])
    df_parsed_windows=setindex(df_parsed_windows,LINEKEY)
    # mean by window type
    dfm = df_parsed_windows.groupby(['window_key','mpos_parse','window_ii','syll_parse']).mean()
    return dfm


def get_window_keys(dfcombo,window_len=3):
    return [x[0] for x in get_windows_in_combo(dfcombo,window_len=3)]
    
def get_window_key_from_slice(windowdf):
    return "|".join(
        f'{x.lower()}_{y}_{z}' if type(x)==str else ''
        for x,y,z in zip(windowdf.word_str, windowdf.syll_i, windowdf.syll_ipa))


def get_windows_in_combo(dfcombo,window_len=3,rolling=True):
    allwindows=[]
    for slicedf in rolling_slices(dfcombo,window_len=3):
        windowdf=pd.DataFrame(slicedf)
        window_key = get_window_key_from_slice(windowdf)
        windowdf['window_key']=str(window_key)
        # windowdf['window_i']=len(allwindows)
        windowdf['window_ii']=list(range(len(windowdf)))
        allwindows.append((window_key,windowdf))
    return allwindows

def avg_out_sylls(poss_parse_rows):
    return pd.DataFrame(poss_parse_rows).mean()

def rejoin_windows_and_combos(df_combos, df_parsed_windows, window_len=3, by_parse=True):
    df_combos=df_combos.reset_index()
    dfpw=df_parsed_windows.reset_index().set_index(['window_key','mpos_parse'])
    o=[]
    for ci,dfcombo in df_combos.groupby('combo_i'):

        for poss_i,poss_parse in enumerate(possible_parses(len(dfcombo))):
            dfparse=pd.DataFrame(dfcombo)
            dfparse['combo_i']=ci
            dfparse['parse_i']=poss_i
            dfparse['combo_parse_i']=len(o)
            dfparse['syll_parse']=list(poss_parse)

            poss_parse_rows = []

            for window_key,window_df in get_windows_in_combo(dfparse):
                mpos_key=''.join(window_df.syll_parse.dropna())
                mstatdf=dfpw.loc[(window_key,mpos_key)].reset_index()
                windowstatdf = merge(
                    window_df,
                    mstatdf,
                    left_on=['window_key','window_ii'],
                    right_on=['window_key','window_ii'],
                    how='outer'
                )
                correct_row=windowstatdf.iloc[1]
                poss_parse_rows+=[correct_row]
            
            # add back
            if by_parse:
                avg_row = avg_for_parse(poss_parse_rows)
                o+=[avg_row]
            else:
                o+=poss_parse_rows

    odf=pd.DataFrame(o)
    # for col in odf.columns:
        # if col.endswith('_i') or col.endswith('_ii'):
            # odf[col]=odf[col].apply(int)
    odf=odf.sort_values('*total')
    return setindex(odf,LINEKEY) if not by_parse else setindex(odf,PARSELINEKEY)


def avg_for_parse(rows):
    dfparse=pd.DataFrame(rows)
    
    linestr = ' '.join(dfparse.drop_duplicates('word_i').word_str)
    ipastr = ' '.join(dfparse.drop_duplicates('word_i').word_ipa)
    stressstr = ''.join(dfparse.prom_stress.apply(stressint2str))
    meterstr = ''.join(dfparse.syll_parse)

    statrow=dict(dfparse.mean())
    statrow=dict((k,v) for k,v in statrow.items() if not k in set(LINEKEY))
    for k in PARSELINEKEY:
        if k in dfparse.columns:
            statrow[k]=dfparse[k].iloc[0]
    statrow['line_str']=linestr
    statrow['line_ipa']=ipastr
    statrow['stress']=stressstr
    statrow['meter']=meterstr
    return statrow




def parse_line(line_df,num_proc=1,window_len=3,by_line=True,keep_best=KEEP_BEST,addback_str=False,**y):
    """
    Parse Line
    """
    pd.options.display.max_columns=None
    pd.options.display.max_rows=100

    # line_df=line_df[[c for c in line_df.columns if not c in {'stanza_i','line_i'}]]
    line_df=setindex(line_df,LINEKEY)
    
    # printm('## line df')
    # display(line_df)

    # get all combos and window types
    csby=['combo_i','word_i','word_ipa_i','syll_i']
    df_combos = line2combos(line_df)
    # printm('## df combos')
    # display(df_combos)

    # # metrical pss for combos?
    # all_combo_all_poss = get_metrical_possibilities(df_combos)
    # printm('## all combo all poss')
    # display(all_combo_all_poss)
    # stop
    
    # get just the unique 3-syll windows
    df_uniq_windows = get_unique_windows(df_combos,window_len=window_len)
    # printm('## df_uniq_windows')
    # display(df_uniq_windows)

    # add metrical pos
    # printm('## df metrical poss')
    df_metrical_poss = get_metrical_possibilities(df_uniq_windows)
    # display(df_metrical_poss)

    # printm('## df_parsed_windows')
    df_parsed_windows=parse_windows(df_metrical_poss)
    # display(df_parsed_windows.head(10))

    # connect back to original line df?
    # printm('## df_rejoined')
    df_rejoined = rejoin_windows_and_combos(df_combos, df_parsed_windows)
    # display(df_rejoined)
    # display(df_rejoined.head(100))
    yield df_rejoined

# def avg_for_line(dfcombo):
#     # produce avg
#     lineavg = dfcombo.groupby(['combo_i','parse_i','word_i','syll_i','word_str','word_ipa','syll_str','syll_ipa','syll_parse']).mean()
#     display(lineavg)
#     stop

#     linestr = ' '.join(dfcombo.drop_duplicates('word_i').word_str)
#     stressstr = ''.join(dfcombo.drop_duplicates(['word_i','syll_i']).prom_stress.apply(stressint2str))
#     meterstr = ''.join(dfcombo.drop_duplicates(['word_i','syll_i']).syll_parse)

#     dfmc=pd.DataFrame([dict(dfcombo.mean())])
#     dfmc['line']=linestr
#     dfmc['stress']=stressstr
#     dfmc['meter']=meterstr

#     pcols = [
#         'line',
#         'stress',
#         'meter'
#     ] + [c for c in dfmc.columns if c.startswith('*')]
#     other=[c for c in dfmc.columns if not c in set(pcols)]
#     yield dfmc[pcols + other]




def stressint2str(x):
    if x==1.0: return 'p'
    if x==0.5: return 's'
    return 'u'

def agg_by_line(df_rejoined):
    df=pd.concat(pmap_groups(
        do_agg_by_line,
        df_rejoined.reset_index().groupby(['combo_i','parse_i']),
        progress=False,
        num_proc=1            
    ))
    return setindex(df,LINEKEY)
    # return windows2lines(df_rejoined.reset_index())






def is_ok_parse(parse,maxS=2,maxW=2):
    return ('s'*(maxS+1)) not in parse and ('w'*(maxW+1)) not in parse

def do_parse_window(windowdf):
    # apply constraints
    dfc = apply_constraints(windowdf)
    yield windowdf[list(set(windowdf.columns) - set(dfc.columns))].join(dfc)



