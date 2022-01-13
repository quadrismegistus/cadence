from ..imports import *




def apply_combos(df,group1,group2,**kwargs):
    # combo of indices?
    combo_opts = [
        [x for ii,x in grp.groupby(group2)]
        for i,grp in df.groupby(group1)
    ]

    # poss
    for combo in product(*combo_opts):
        if not len(combo): continue
        odf=pd.concat(combo)
        odf['slot_i']=[i+1 for i in range(len(odf))]
        yield odf.set_index('slot_i')

def iter_combos(txtdf,num_proc=1,**kwargs):
    for dfi,dfcombo in enumerate(apply_combos(resetindex(txtdf), 'word_i', 'word_ipa_i',**kwargs)):
        yield dfcombo.assign(combo_i=dfi+1)






def tokenize_sentwords_ll(words_ld,**kwargs):
    if not len(words_ld): return []
    listd=defaultdict(list)
    for word_d in words_ld:
        listd[word_d['sent_i']].append(word_d['word_str'])
    olist=[sentl for sent_i,sentl in sorted(listd.items())]
    return olist


def tokenize_sentwords_ll_from_df(words_df,**kwargs):
    if not len(words_df): return []
    return [
        list(sdf.sort_values('word_i').word_str)
        for si,sdf in sorted(words_df.groupby('sent_i'))
    ]




def tokenize_sents_txt(txt,**y):
    sents=nltk.sent_tokenize(txt)
    lastoffset=0
    osents=[]
    
    for sent in sents:
        offset = txt.find(sent,lastoffset)
        newpref=txt[lastoffset:offset]
        #print([newpref,offset,lastoffset,sent])
        lastoffset=offset + len(sent)
        newsent=newpref + sent
        osents.append(newsent)
    return osents

def tokenize_words_txt(txt):
    l=tokenize_nice2(txt)
    o=[]
    o0=''
    for x in l:
        if zero_punc(x):
            o+=[o0 + x]
            o0=''
        elif o:
            o[-1]+=x
        else:
            o0+=x
    return o


def tokenize_sentwords_iter(
        txt,
        sents=None,
        lang=DEFAULT_LANG,
        sep_line=SEP_LINE,
        sep_para=SEP_STANZA,
        seps_phrase=SEPS_PHRASE,
        progress=True,
        para_i=None,
        **kwargs):
    char_i=0
    line_i=1
    linepart_i=1
    linepart_ii=0
    start_offset=0
    if sents is None: sents=tokenize_sents_txt(txt)
    for sent_i, sent in enumerate(sents):
        tokens=tokenize_words_txt(sent)
        for tok_i,realtok in enumerate(tokens):
            prefstr,wordstr1,sufstr=split_punct(realtok)
            word_str=wordstr1+sufstr
            word_tok=to_token(word_str)
            if sep_line in prefstr and realtok.strip(): line_i+=1
            odx_word=dict(
                # para_i=para_i,
                **(dict(para_i=para_i) if para_i is not None else {}),
                sent_i=sent_i+1,
                sentpart_i=linepart_i,
                line_i=line_i,
                word_i=tok_i+1,
                word_pref=prefstr,
                word_str=word_str,
                word_tok=word_tok,
            )
            yield odx_word
            if set(realtok)&set(seps_phrase): linepart_i+=1


def tokenize_paras_ld(txt,sep_para=SEP_PARA, **kwargs):
    txt=clean_text(txt)
    paras_txt=txt.split(sep_para)
    num_paras=len(paras_txt)
    ld=[]
    offset=0
    para_i=0
    for pi,para_txt in enumerate(paras_txt):
        if pi: para_txt=sep_para+para_txt
        para_txt_len=len(para_txt)
        para_str=para_txt.strip()
        para_str_len=len(para_str)
        para_str_noleft=para_txt.lstrip()
        para_str_noright=para_txt.rstrip()
        diff_left=para_txt_len - len(para_str_noleft)
        diff_right=para_txt_len - len(para_str_noright)
        
        offset1=offset+diff_left
        offset2=offset+para_txt_len-diff_right

        if para_str:
            assert para_str == txt[offset1:offset2]
            para_i+=1
            dx={
                'para_i':para_i,
                'para_str':para_str,
                'para_start_char':offset1,
                'para_end_char':offset2,
                # 'para_txt':para_txt,
            }
            ld.append(dx)
        offset+=para_txt_len
    return ld


def getcache_df(self, name, iter_func, index=True, cache=True,**kwargs):
    d=getattr(self,name)
    key=kwargs_key(kwargs)
    if not cache or not key in d:
        d[key]=pd.DataFrame(iter_func(**kwargs))
    odf=d[key]
    try:
        if len(odf) and index: odf=setindex(odf)
    except ValueError:
        pass
    return odf


### convenient objs
def kwargs_key(kwargs,bad_keys={'num_proc','progress','desc'}):
    return ', '.join(
        f'{k}={v}'
        for k,v in kwargs.items()
        if k not in bad_keys
    )
    




# loading txt/strings
def to_txt(txt_or_fn):
    # load txt
    if type(txt_or_fn)==str and not '\n' in txt_or_fn and os.path.exists(txt_or_fn):
        with open(txt_or_fn,encoding='utf-8',errors='replace') as f:
            return f.read()
    return txt_or_fn

    
    
def to_txt_from_scandf(scandf):
    return '\n\n'.join(
        '\n'.join(
            ''.join(
                linepartdf.index.get_level_values('line_str')[0]
                for linepart_i,linepartdf in linedf.groupby('linepart_i')
            )
            for line_i,linedf in stanzadf.groupby('line_i')
        )
        for stanza_i,stanzadf in scandf.groupby('stanza_i')
    )
    
def to_stanzas_str(full_txt,sep=SEP_STANZA,**kwargs):
    return [st.strip() for st in full_txt.strip().split(sep) if st.strip()]

def to_lines_str(stanza_txt,sep=SEP_STANZA,**kwargs):
    return [st.strip() for st in stanza_txt.strip().split(sep) if st.strip()]

def to_sents_str(stanza_txt,**kwargs):
    return list(nltk.sent_tokenize(stanza_txt))

def limit_lineparts(linepart_toks,min_len=None,max_len=None):
    if not min_len and not max_len: return [linepart_toks]

    lp=[]
    o=[]
    for tok in reversed(linepart_toks):
        lp.insert(0,tok)
        if len(lp)>=max_len:
            o.insert(0,lp)
            lp=[]
    if lp: o.insert(0,lp)
    
    return o
    

def to_lineparts_str(line_str,seps=SEPS_PHRASE,**kwargs):
    lineparts=[]
    linepart=[]
    tokens=list(tokenize_nice(line_str))
    for token in tokens:
        pref,tok,suf = split_punct(token)        
        is_pref_stopper=set(pref)&set(seps)
        is_suf_stopper=set(suf)&set(seps)
        
        if is_pref_stopper:
            lineparts.append(linepart)
            linepart=[]
        
        linepart.append(token)
        
        if is_suf_stopper:
            lineparts.append(linepart)
            linepart=[]

    # add if remaining
    if linepart:
        lineparts.append(linepart)
        linepart=[]
        
    ## Further divide by max_len
    o=[''.join(lpstr2) for lp_toks in lineparts for lpstr2 in limit_lineparts(lp_toks,**kwargs)]        
    return o






def to_lineparts_ld(
        txt_or_fn_or_lpdf,
        lang=DEFAULT_LANG,
        progress=True,
        incl_alt=INCL_ALT,
        num_proc=DEFAULT_NUM_PROC,
        linebreaks=False,
        phrasebreaks=True,
        verse=None,
        prose=None,
        min_len=MIN_WORDS_IN_PHRASE,
        max_len=MAX_WORDS_IN_PHRASE,
        seps=SEPS_PHRASE,
        desc='Iterating over line scansions',
        **kwargs):
    
    if type(txt_or_fn_or_lpdf) == pd.DataFrame:
        odf=resetindex(txt_or_fn_or_lpdf)
        if 'linepart_str' in set(odf.columns):
            return odf
        else:
            raise Exception('Input is neither string or a linepart-df [result of lineparts()]')
    
    full_txt=to_txt(txt_or_fn_or_lpdf)
    if full_txt is None: return
    
    if verse==True or prose==False:
        linebreaks=True
        phrasebreaks=False
    elif prose==True or verse==False:
        linebreaks=False
        phrasebreaks=True

    df=pd.DataFrame()
    dfl=[]
    to_lines_now = to_lines_str if linebreaks else to_sents_str
    kwargs['lang']=lang
    kwargs['incl_alt']=incl_alt
    
        
    objs=[
        dict(
            stanza_i=stanza_i+1,
            line_i=line_i+1,
            linepart_i=linepart_i+1,
            linepart_str=linepart_txt
        )
        for stanza_i,stanza_txt in enumerate(to_stanzas_str(full_txt))
        for line_i,line_txt in enumerate(to_lines_now(stanza_txt))
        for linepart_i,linepart_txt in enumerate(
            to_lineparts_str(
                line_txt,
                seps=seps,
                min_len=min_len,
                max_len=max_len
            ) if phrasebreaks else [line_txt]
        )
    ]
    return objs

def to_words(line_txt,lang_code=DEFAULT_LANG):
    lang = to_lang(lang_code)
    o=lang.tokenize(line_txt)
    #print(o)
    #stop
    return o
    
def to_syllables(word_txt,lang_code=DEFAULT_LANG):
    lang = to_lang(lang_code)
    return lang.syllabify(word_txt)

# def scan(txt_or_fn,**kwargs):
#     try:
#         return setindex(
#             pd.concat(
#                 scan_iter(txt_or_fn,**kwargs)
#             )
#         )
#     except ValueError:
#         return pd.DataFrame()





def lineparts(
        txt_or_fn_or_lpdf,
        lang=DEFAULT_LANG,
        progress=True,
        incl_alt=INCL_ALT,
        num_proc=DEFAULT_NUM_PROC,
        linebreaks=False,
        phrasebreaks=True,
        verse=None,
        prose=None,
        min_len=MIN_WORDS_IN_PHRASE,
        max_len=MAX_WORDS_IN_PHRASE,
        seps=SEPS_PHRASE,
        desc='Iterating over line scansions',
        **kwargs):
    
    if type(txt_or_fn_or_lpdf) == pd.DataFrame:
        odf=resetindex(txt_or_fn_or_lpdf)
        if 'linepart_str' in set(odf.columns):
            return odf
        else:
            raise Exception('Input is neither string or a linepart-df [result of lineparts()]')
    

    full_txt=to_txt(txt_or_fn_or_lpdf)
    if full_txt is None: return
    
    if verse==True or prose==False:
        linebreaks=True
        phrasebreaks=False
    elif prose==True or verse==False:
        linebreaks=False
        phrasebreaks=True

    df=pd.DataFrame()
    dfl=[]
    to_lines_now = to_lines_str if linebreaks else to_sents_str
    kwargs['lang']=lang
    kwargs['incl_alt']=incl_alt
    
        
    objs=[
        dict(
            stanza_i=stanza_i+1,
            line_i=line_i+1,
            linepart_i=linepart_i+1,
            linepart_str=linepart_txt
        )
        for stanza_i,stanza_txt in enumerate(to_stanzas_str(full_txt))
        for line_i,line_txt in enumerate(to_lines_now(stanza_txt))
        for linepart_i,linepart_txt in enumerate(
            to_lineparts(
                line_txt,
                seps=seps,
                min_len=min_len,
                max_len=max_len
            ) if phrasebreaks else [line_txt]
        )
    ]
    return objs


SIZELIM=53687091200

def get_db_scan(path=None):
    if not path or not os.path.exists(path): path=PATH_DB_SCAN
    return get_db(path=path)

def get_db_parse(path=None):
    if not path or not os.path.exists(path): path=PATH_DB_PARSE
    return get_db(path=path)

def get_db(path=None):
    if not path or not os.path.exists(path): path=PATH_DB
    return dc.Cache(path,size_limit=SIZELIM)


def get_linepart_str(lpdf_or_str):
    if type(lpdf_or_str)==str: return lpdf_or_str
    elif type(lpdf_or_str)==pd.DataFrame:
        lpdf=resetindex(lpdf_or_str)
        return ''.join(lpdf[(lpdf.word_ipa_i==1) & (lpdf.syll_i==1)].word_str)
    return ''

def get_linepart_df(lpdf_or_str,**kwargs):
    if type(lpdf_or_str)==pd.DataFrame: return resetindex(lpdf_or_str)
    elif type(lpdf_or_str)==str: return resetindex(get_scansion(lpdf_or_str,**kwargs))
    return pd.DataFrame()






def get_line_data(linepart_txt,**kwargs):
    try:
        df=line2df(linepart_txt,**kwargs)
        df['word_i']=df['word_i'].rank(method='dense').apply(int)
        df=df[df.syll_i!=0]
        # df['linepart_str']=linepart_txt
        df['linepart_num_syll']=len(df[df['word_ipa_i']==1])
        df['linepart_num_monosyll']=sum([
            1 if len(g)==1 else 0
            for i,g in df[df.word_ipa_i==1].groupby('word_i')
        ])
        assign_proms(df)
        # df=setindex(df)
        return df
    except Exception as e:
        return pd.DataFrame()

def get_scansion(linepart_txt,path=None,cache=True,force=False,**kwargs):
    if type(linepart_txt)==pd.DataFrame:
        return linepart_txt
    
    # lpl=linepart_txt.strip().split()
    #lptxt=' '.join(lpl)
    #lpkey='_'.join(lpl)
    lptxt=linepart_txt#.strip().replace(' ','_')
    lpkey=lptxt
    key=f'{lpkey}{DBSEP}scan'
    if not force and cache:
        with get_db(path=path) as d:
            if not key in d:
                d[key]=get_line_data(lptxt,**kwargs)
            odf=d[key]
    else:
        odf=get_line_data(lptxt)
    
    if len(odf): odf['linepart_str']=lptxt
    return setindex(odf)



def scan_iter(df_or_txt_or_fn,num_proc=1,lim=None,progress=True,lineparts_ld=[],**kwargs):
    if not lineparts_ld:
        lineparts_ld=to_lineparts_ld(df_or_txt_or_fn,**kwargs)
    iterr_o=pmap_iter(
        do_scan_iter,
        lineparts_ld,
        progress=progress,
        num_proc=num_proc,
        desc='Scanning lines'
    )
    for i,odf in enumerate(iterr_o):
        if lim and i>=lim: break
        yield odf

        
def scan(txt_or_fn,**kwargs):
    o=list(scan_iter(txt_or_fn,**kwargs))
    return pd.concat(o) if len(o) else pd.DataFrame()

def do_scan_iter(rowd,**kwargs):
    lpstr=rowd['linepart_str']
    odf=get_scansion(lpstr,**kwargs)
    for k,v in rowd.items(): odf[k]=v
    return setindex(odf)



# def assign_proms(df):
#     # set proms
#     df['prom_stress']=pd.to_numeric(df['syll_ipa'].apply(getstress),errors='coerce')
#     df['prom_weight']=pd.to_numeric(df['syll_ipa'].apply(getweight),errors='coerce')
#     df['syll_stress']=df.prom_stress.apply(lambda x: {1.0:'P', 0.5:'S', 0.0:'U'}.get(x,''))
#     df['syll_weight']=df.prom_weight.apply(lambda x: {1.0:'H', 0.0:'L'}.get(x,''))

#     df['prom_strength']=[
#         x
#         for i,df_word in df.groupby(['word_i','word_ipa_i'])
#         for x in getstrength(df_word)
#     ]
#     df['is_stressed']=(df['prom_stress']>0).apply(np.int32)
#     df['is_unstressed']=(df['prom_stress']==0).apply(np.int32)
#     df['is_heavy']=(df['prom_weight']==1).apply(np.int32)
#     df['is_light']=(df['prom_weight']==0).apply(np.int32)
#     df['is_peak']=(df['prom_strength']==1).apply(np.int32)
#     df['is_trough']=(df['prom_strength']==0).apply(np.int32)


def get_info_byline(txtdf):
    linedf=txtdf.xs([0,0,0],level=['word_i','word_ipa_i','syll_i'])
    linedf=linedf.reset_index(level=['word_str','word_ipa','syll_str','syll_ipa','line_ii'],drop=True)
    return linedf#.reset_index().set_index(['stanza_i','line_i'])







sonnet="""How heavy do I journey on the way,
When what I seek, my weary travel's end,
Doth teach that ease and that repose to say
'Thus far the miles are measured from thy friend!'
The beast that bears me, tired with my woe,
Plods dully on, to bear that weight in me,
As if by some instinct the wretch did know
His rider loved not speed, being made from thee:
The bloody spur cannot provoke him on
That sometimes anger thrusts into his hide;
Which heavily he answers with a groan,
More sharp to me than spurring to his side;
For that same groan doth put this in my mind;
My grief lies onward and my joy behind."""
sonnet1="How heavy do I journey on the way,"



def syllabify_df(df,**kwargs):
    cols=set(df.columns)
    if not 'word_tok' in cols and 'word_str' in cols:
        df['word_tok']=df.word_str.apply(to_token)
    dfsyll=pd.concat(
        get_syllable_df(word_tok,index=False,**kwargs)
        for word_tok in df.word_tok.unique()
    )
    odf=df.merge(dfsyll,on='word_tok',how='left')

    ## mtree
    for col in cols:
        if col.startswith('mtree_'):
            odf.loc[
                ((odf['syll_stress']==0.0) & (odf['word_nsyll']>1)),
                col
            ]=np.nan
    return odf