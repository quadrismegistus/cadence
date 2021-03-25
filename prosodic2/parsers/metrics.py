from ..imports import *

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

def parse_line(line_df,num_proc=1,by_line=True,keep_best=KEEP_BEST,addback_str=False,**y):
    df_combos = line2combos(line_df)
    out = pmap_groups(
        parse_combo,
        df_combos.groupby(['stanza_i','line_i','line_combo_i']),
        num_proc=num_proc,
        progress=False,#num_proc==1,
        desc='Parsing all combinations for line',
        **y
    )
    yield parses_by_line(pd.concat(out))# if by_line else out


def parses_by_line(df_parses, keep_best=1):
    pcols=[
        'stanza_i',
        'line_i',
        'meter_parse',   
        'meter_parse_repr',
        'stress_parse_ipa',
        # 'stress_parse_repr',
    ]
    ccols = [c for c in df_parses.columns if c.startswith('*')]
    dfg=df_parses.groupby(pcols).sum()[ccols].reset_index()
    
    if keep_best:
        dfg=dfg.sort_values('*total').groupby(['stanza_i','line_i']).head(keep_best)

    return dfg




def do_parse_combo(df_mcombo):
    # apply constraints
    df_mcombo_parsed = apply_constraints(df_mcombo)
    yield df_mcombo_parsed

def mpos_windows(df_all_combos, windowlen=3):
    windows_done=set()
    window=[None,None,None]
    for i,row in df_all_combos.iterrows():
        window=window[1:] + [row]
        window_key=tuple(
            row.parse if row is not None else None
            for row in window
        )
        if window_key in windows_done: continue
        windows_done|={window_key}

        yield pd.DataFrame(window)

def parse_combo(df_combo):
    wordsyllsmeter_combos = _all_possible_metrical_combos(df_combo)
    dfwsc = df_combo.set_index(['word_i','syll_i'])
    dfall=pd.DataFrame()
    # objs=[]
    for wi,wsc in enumerate(wordsyllsmeter_combos):#,desc='Parsing line combos',position=1)):
        ws2mtr=dict(([((w,s),c) for w,s,c in wsc]))
        df_mcombo = pd.DataFrame(dfwsc.loc[ws2mtr.keys()].reset_index().sort_values(['word_i','syll_i']))
        df_mcombo['parse']=[ws2mtr.get((w,s)) for w,s in zip(df_mcombo.word_i,df_combo.syll_i)]
        df_mcombo['meter_parse_i']=wi
        df_mcombo['meter_parse']=''.join(df_mcombo['parse'])
        df_mcombo['is_w']=(df_mcombo['parse']=='w').apply(np.int32)
        df_mcombo['is_s']=(df_mcombo['parse']=='s').apply(np.int32)
        df_mcombo['meter_parse_repr']=''
        # df_mcombo['meter_parse_repr']='|'.join(
        #     '.'.join([
        #         tok.upper() if parse=='s' else tok.lower()
        #         for tok,parse in zip(df_word.syll_str, df_word.parse)
        #     ])
        #     for i,df_word in sorted(df_mcombo.groupby(['word_i','word_ipa_i']))
        # )
        dfall=dfall.append(df_mcombo)
    
    
    ### make unique
    windows = list(mpos_windows(dfall))
    print(len(windows))
    yield from pmap_groups(
        do_parse_combo,
        windows,
        num_proc=1,
        progress=False,
        use_cache=False
    )



def line2combos(line_df,**y):
    word_rows = [
        set(list(zip(word_df.word_i, word_df.word_ipa_i, word_df.word_ipa)))                
        # set(list(zip(word_df.word_i, word_df.word_ipa_i, word_df.word_ipa)))                
        for word_i,word_df in sorted(line_df.groupby('word_i'))
    ]

    # divide at blank points
    word_rows_div=[]
    word_row_div = []
    for wordforms in word_rows:
        # split into phrases?
        if len(wordforms)==1 and not list(wordforms)[0][-1].strip():
            if len(word_row_div)>=MIN_WORDS_IN_PHRASE:
                word_rows_div.append(word_row_div)
                word_row_div=[]
        else:
            word_row_div.append(wordforms)
    if word_row_div: word_rows_div.append(word_row_div)

    from pprint import pprint
    
    # gen combos
    all_combos = []
    for word_row_div in word_rows_div:
        combos = list(product(*word_row_div))
        all_combos.extend(combos)
    
    # loop
    combo_dfs=pd.DataFrame()
    ldf=line_df.set_index(['word_i','word_ipa_i'])
    for combo_i,combo in enumerate(all_combos):
        # print(combo)
        combo_df=pd.DataFrame(ldf.loc[[(cx[0],cx[1]) for cx in combo]].reset_index())
        # display(combo_df)
        combo_df['line_combo_i']=combo_i
        combo_df['stress_parse']=''.join(
            ''.join([getstress_str(sylipa) for sylipa in df_word.syll_ipa])
            for i,df_word in combo_df.groupby(['word_i','word_ipa_i'])
        ).lower()
        combo_df['stress_parse_ipa']='|'.join(
            '.'.join(df_word.syll_ipa)
            for i,df_word in combo_df.groupby(['word_i','word_ipa_i'])
        )#.lower()
        combo_df['stress_parse_repr']='|'.join(
            '.'.join([
                tok.upper() if stress>0 else tok.lower()
                for tok,stress in zip(df_word.syll_str, df_word.prom_stress)
            ])
            for i,df_word in combo_df.groupby(['word_i','word_ipa_i'])
        )
        combo_dfs=combo_dfs.append(combo_df)
        # break
    return combo_dfs





    



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
