from ..imports import *

SBY=csby=['combo_i','word_i','syll_i']
LINEKEY=[
    'stanza_i',
    'line_i',
    'combo_i',
    'window_i',
    'parse_i',
    'mpos_parse',
    'window_ii',
    'syll_parse',
    'word_i','word_str','word_ipa_i','word_ipa',
    'syll_i','syll_str','syll_ipa',
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
        # combodf['window_key']=list(get_window_keys(combodf.syll_ipa))
        # combodf['window_key_str']=[wk.lower() for wk in get_window_keys(combodf.syll_str)]
        o+=[combodf]
    odf=pd.concat(o)
    odf=setindex(odf,LINEKEY)
    return odf

def get_window_keys(sylls_ipa,window_len=3):
    window_key=['','','']
    for x in sylls_ipa:
        window_key.append(x)
        while len(window_key)>window_len: window_key.pop(0)
        wk='_'.join(window_key)
        yield wk
    
def get_unique_windows(df_combos,window_len=3):
    window=[]
    allwindows=[]
    for i,row in df_combos.reset_index().iterrows():
        # print(i,row)
        window.append(row)
        if len(window)>window_len: window.pop(0)
        if len(window)<window_len: continue

        windowdf=pd.DataFrame(window)
        windowdf['window_i']=len(allwindows)
        windowdf['window_ii']=list(range(len(windowdf)))
        allwindows.append(windowdf)
    dfo=pd.concat(allwindows).drop('combo_i',1)
    return setindex(dfo,LINEKEY)




def possible_parses(window_len,maxS=2,maxW=2):
    poss = list(product(*[('w','s') for n in range(window_len)]))
    poss = [''.join(x) for x in poss]
    poss = [x for x in poss if is_ok_parse(x,maxS=maxS,maxW=maxW)]
    poss = [x for x in poss if len(x)==window_len]
    return poss

def add_metrical_possibilities(window, window_len=3,maxS=2,maxW=2):
    # loop metrical possibilities
    poss=possible_parses(len(window),maxS=maxS,maxW=maxW)

    for parse_i,posx in enumerate(sorted(poss)):    
        windowdf=pd.DataFrame(window)
        windowdf['syll_parse']=[x for x in posx]
        windowdf['is_w']=(windowdf['syll_parse']=='w').apply(np.int32)
        windowdf['is_s']=(windowdf['syll_parse']=='s').apply(np.int32)
        windowdf['mpos_parse']=posx
        windowdf['mpos_parse_i']=parse_i
        yield windowdf

def setindex(df,key):
    key2=[]
    for x in key:
        if not x in set(key2):
            key2.append(x)
    key=key2
    return df.set_index([x for x in key if x in set(df.columns)]).sort_index()


def get_metrical_possibilities(df_uniq_windows,maxS=2,maxW=2):
    df=pd.DataFrame()
    for window_i,wdf in df_uniq_windows.reset_index().groupby('window_i'):
        wdf=wdf.sort_values('window_ii')
        posnum=len(wdf)
        for pi,poss_parse in enumerate(possible_parses(posnum, maxS=maxS,maxW=maxW)):
            wdf2=pd.DataFrame(wdf)
            wdf2['parse_i']=pi
            wdf2['mpos_parse']=str(poss_parse)
            wdf2['parse_ii']=list(range(len(wdf2)))
            wdf2['syll_parse']=list(poss_parse)
            wdf2['is_w']=(wdf2['syll_parse']=='w').apply(np.int32)
            wdf2['is_s']=(wdf2['syll_parse']=='s').apply(np.int32)
            df=df.append(wdf2)
    return setindex(df, ['window_i','parse_i','mpos_parse','parse_ii','syll_parse'] + LINEKEY)

def join(x,y,on=['id'],how='outer'):
    # x=x.reset_index()
    # y=y.reset_index()
    xkeys=on + [c for c in x.columns if c not in set(on) and c not in set(y.columns)]
    return x[xkeys].set_index(on).join(y.set_index(on),how=how)

def parse_windows(df_metrical_poss,num_proc=1,progress=False,**y):
    df_metrical_poss=df_metrical_poss.reset_index()
    # parse
    out = pmap_groups(
        do_parse_window,
        df_metrical_poss.groupby(['window_i','parse_i']),
        num_proc=num_proc,
        progress=progress,#num_proc==1,
        desc='Parsing all combinations for line',
        **y
    )
    df_parsed_windows=pd.concat(out)#.sort_values(['window_i','mpos_parse','word_i','syll_i'])
    return setindex(df_parsed_windows,LINEKEY)


def rejoin_windows_and_combos(df_combos, df_parsed_windows):
    df = join(
        df_combos.reset_index(),
        df_parsed_windows.reset_index(),
        on=['word_i','word_ipa_i','word_ipa','syll_i','syll_ipa'],
        how='outer'
    )
    return setindex(df.reset_index(),LINEKEY)

def parse_line(line_df,num_proc=1,window_len=3,by_line=True,keep_best=KEEP_BEST,addback_str=False,**y):
    pd.options.display.max_columns=None
    pd.options.display.max_rows=25

    line_df=line_df[[c for c in line_df.columns if not c in {'stanza_i','line_i'}]]
    line_df=setindex(line_df,LINEKEY)
    
    printm('## line df')
    display(line_df)

    # get all combos and window types
    csby=['combo_i','word_i','word_ipa_i','syll_i']
    df_combos = line2combos(line_df)
    printm('## df combos')
    display(df_combos)
    
    # get just the unique 3-syll windows
    df_uniq_windows = get_unique_windows(df_combos,window_len=window_len)
    printm('## df_uniq_windows')
    display(df_uniq_windows)

    # add metrical pos
    printm('## df metrical poss')
    df_metrical_poss = get_metrical_possibilities(df_uniq_windows)
    display(df_metrical_poss)

    printm('## df_parsed_windows')
    df_parsed_windows=parse_windows(df_metrical_poss)
    display(df_parsed_windows)

    # connect back to original line df?
    df_rejoined = rejoin_windows_and_combos(df_combos, df_parsed_windows)
    printm('## df_rejoined')
    display(df_rejoined)

    odf=agg_by_line(df_rejoined) if by_line else df_rejoined
    printm('## OUTPUT DF')
    display(odf)
    yield odf


def stressint2str(x):
    if x==1.0: return 'p'
    if x==0.5: return 's'
    return 'u'

def agg_by_line(df_rejoined):
    df=pd.concat(pmap_groups(
        do_agg_by_line,
        df_rejoined.reset_index().groupby('combo_i'),
        progress=False,
        num_proc=1            
    ))
    return setindex(df,LINEKEY)


def do_agg_by_line(dfcombo):
    display(dfcombo)
    dfcombo=dfcombo.sort_values(['word_i','syll_i'])

    linestr = ' '.join(dfcombo.drop_duplicates('word_i').word_str)
    stressstr = ''.join(dfcombo.drop_duplicates(['word_i','syll_i']).prom_stress.apply(stressint2str))
    meterstr = ''.join(dfcombo.drop_duplicates(['word_i','syll_i']).syll_parse)

    dfmc=pd.DataFrame([dict(dfcombo.mean())])
    dfmc['line']=linestr
    dfmc['stress']=stressstr
    dfmc['meter']=meterstr

    pcols = [
        'line',
        'stress',
        'meter'
    ] + [c for c in dfmc.columns if c.startswith('*')]
    other=[c for c in dfmc.columns if not c in set(pcols)]
    yield dfmc[pcols + other]



def is_ok_parse(parse,maxS=2,maxW=2):
    return ('s'*(maxS+1)) not in parse and ('w'*(maxW+1)) not in parse

def do_parse_window(windowdf):
    # apply constraints
    dfc = apply_constraints(windowdf)
    yield windowdf[list(set(windowdf.columns) - set(dfc.columns))].join(dfc)

def windows2lines(df):
    combos = [
        [pdf for parse_i,pdf in sorted(cdf.groupby('window_key'))]
        for ci,cdf in sorted(df.groupby('combo_i'))
    ]
    # combos = [
    #     [y for x,y in df.groupby('mpos_parse_i')]
    # ]
    all_combos = list(product(*combos))
    # print(len(all_combos))
    printm('## all combos')
    display(pd.concat(all_combos[0]).set_index('combo_i').sort_values(['word_i','syll_i']).loc[0])#.drop_duplicates().head(20))

    df['meter_parse']=parse=''.join(df.syll_parse)
    dfm=df.groupby([
        'stanza_i','line_i','line_combo_i','parse_i','meter_parse','stress_parse'
    ]).mean()
    return dfm


def parses_by_line(df_parses, keep_best=1, maxS=2, maxW=2, dupkeys=['stanza_i','line_i','line_combo_i','word_i','word_ipa_i','syll_i']):
    df=df_parses.sort_values(['combo_i','word_i','syll_i'])


    # combos = [
    #     [pdf for parse_i,pdf in sorted(wdf.groupby('parse_i'))]
    #     for window_i,wdf in sorted(df.groupby('window_i'))
    # ]
    # all_combos = list(product(*combos))
    # alldf=pd.concat([df for ldf in combos for df in ldf])
    # #display(alldf.iloc[0])
    # alldfm=windows2lines(alldf)
    # display(alldfm)
    # alldf

    # newrows=[]
    # for combo_i,combo in enumerate(tqdm(all_combos)):
    #     combodf=pd.concat(combo)
    #     combodf_meta=combodf.drop_duplicates(dupkeys)
    #     parse=''.join(combodf_meta.syll_parse)
    #     if not is_ok_parse(parse,maxS=maxS,maxW=maxW): continue 
    #     #combodf_avg = dict(combodf.drop(dupkeys,1).fillna(0).mean())
    #     newrows+=[combodf_meta]
    

    #     # newrow = dict(combodf[['stanza_i','line_i','line_combo_i']].iloc[0])
    #     # newrow['parse']=parse
    #     # for k,v in combodf_avg.items(): newrow[k]=v
    #     # newrows.append(newrow)
    # newdf=pd.concat(newrows)
    # display(newdf)
    # stop
    


    



def _all_possible_metrical_combos(df_combo):
    wordsylls=sorted(list(set(zip(df_combo.word_i,df_combo.syll_i))))

    wordsyllsmeter = [
        [tuple(list(wsyll)+['w']), tuple(list(wsyll)+['s'])]
        for wsyll in wordsylls
    ]

    wordsyllsmeter_combos = list(product(*wordsyllsmeter))
    
    # disallow stretches of 3
    wordsyllsmeter_combos = [
        combo
        for combo in wordsyllsmeter_combos
        if ''.join([x[-1] for x in combo]).count('www')==0
        and ''.join([x[-1] for x in combo]).count('sss')==0
    ]
    return wordsyllsmeter_combos
