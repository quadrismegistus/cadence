from ..imports import *









# loading txt/strings
def to_txt(txt_or_fn):
    # load txt
    if not txt_or_fn: return
    if os.path.exists(txt_or_fn):
        with open(txt_or_fn,encoding='utf-8',errors='replace') as f:
            txt=f.read()
    else:
        txt=txt_or_fn
    
    # clean?
    txt=txt.replace('--','—')

    return txt

    
    
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
    
def to_stanzas(full_txt):
    return [st.strip() for st in full_txt.strip().split('\n\n') if st.strip()]
def to_lines_str(stanza_txt):
    return [l.strip() for l in stanza_txt.split('\n') if l.strip()]
def to_sents_str(stanza_txt):
    return [
        sent.replace('\n',' ').strip()
        for sent in nltk.sent_tokenize(stanza_txt)
    ]

def to_lineparts(linetxt,seps=SEPS_PHRASE,min_len=1,max_len=15):
    o=[]
    for sent in to_sents_str(linetxt):
        sentparts=[]
        sentpart=[]
        for token in tokenize_nice(sent):
            pref,tok,suf = split_punct(token)

            # end prev?
            if sentpart and set(pref)&set(seps) and len(sentpart)>=min_len:
                sentparts.append(sentpart)
                sentpart=[]

            # add no matter what
            sentpart.append(token)

            # end after? or if too long?
            if sentpart and ((set(suf)&set(seps) and len(sentpart)>=min_len) or len(sentpart)>=max_len):
                sentparts.append(sentpart)
                sentpart=[]

        # add if remaining
        if sentpart:
            sentparts.append(sentpart)
            sentpart=[]
        o+=sentparts
    return [''.join(x) for x in o]

def to_words(line_txt,lang_code=DEFAULT_LANG):
    lang = to_lang(lang_code)
    o=lang.tokenize(line_txt)
    #print(o)
    #stop
    return o
    
def to_syllables(word_txt,lang_code=DEFAULT_LANG):
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
        txt_or_fn,
        lang=DEFAULT_LANG,
        progress=True,
        incl_alt=INCL_ALT,
        num_proc=DEFAULT_NUM_PROC,
        linebreaks=False,
        phrasebreaks=True,
        verse=None,
        prose=None,
        linepart_min_len=MIN_WORDS_IN_PHRASE,
        linepart_max_len=MAX_WORDS_IN_PHRASE,
        linepart_seps=SEPS_PHRASE,
        desc='Iterating over line scansions',
        **kwargs):
    
    full_txt=to_txt(txt_or_fn)
    if not full_txt: return
    
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
        for stanza_i,stanza_txt in enumerate(to_stanzas(full_txt))
        for line_i,line_txt in enumerate(to_lines_now(stanza_txt))
        for linepart_i,linepart_txt in enumerate(
            to_lineparts(
                line_txt,
                seps=linepart_seps,
                min_len=linepart_min_len,
                max_len=linepart_max_len
            ) if phrasebreaks else [line_txt]
        )
    ]
    return pd.DataFrame(objs)




def get_db_scan(path=None):
    if not path or not os.path.exists(path): path=PATH_DB_SCAN
    with dc.Cache(path) as of: return of

def get_db_parse(path=None):
    if not path or not os.path.exists(path): path=PATH_DB_PARSE
    with dc.Cache(path) as of: return of

def get_db(path=None):
    if not path or not os.path.exists(path): path=PATH_DB
    with dc.Cache(path) as of: return of


def get_line_data(linepart_txt,**kwargs):
    df=line2df(linepart_txt,**kwargs)
    df=df[df.syll_i!=0]
    df['linepart_num_syll']=len(df[df['word_ipa_i']==1])
    df['linepart_num_monosyll']=sum([
        1 if len(g)==1 else 0
        for i,g in df[df.word_ipa_i==1].groupby('word_i')
    ])
    assign_proms(df)
    # df=setindex(df)
    return df

def get_scansion(linepart_txt,path=None,**kwargs):
    lptxt=linepart_txt.strip()
    key=f'{lptxt}{DBSEP}scan'
    with get_db(path=path) as d:
        if not key in d:
            d[key]=get_line_data(lptxt,**kwargs)
        return d[key]



def do_scan_iter(dfx):
    ltxts=getcol(dfx,'linepart_str')
    return get_scansion(ltxts.iloc[0].strip()) if len(ltxts) else pd.DataFrame()
    

def scan_iter(df_or_txt_or_fn,num_proc=1,**kwargs):
    if type(df_or_txt_or_fn) not in {pd.DataFrame,str}: return

    if type(df_or_txt_or_fn)!=pd.DataFrame:
        txt=to_txt(df_or_txt_or_fn)
        df=lineparts(txt,**kwargs)
    else:
        df=df_or_txt_or_fn

    dfg=df.groupby(['stanza_i','line_i','linepart_i'])
    for odf in pmap_iter_groups(do_scan_iter, dfg, num_proc=num_proc):
        yield odf


def scan(txt_or_fn,**kwargs):
    odf=pd.DataFrame()
    try:
        odf=pd.concat(scan_iter(txt_or_fn,**kwargs))
        odf=setindex(odf)
    except ValueError:
        pass
    return odf


def assign_proms(df):
    # set proms
    df['prom_stress']=pd.to_numeric(df['syll_ipa'].apply(getstress),errors='coerce')
    df['prom_weight']=pd.to_numeric(df['syll_ipa'].apply(getweight),errors='coerce')
    df['syll_stress']=df.prom_stress.apply(lambda x: {1.0:'P', 0.5:'S', 0.0:'U'}.get(x,''))
    df['syll_weight']=df.prom_weight.apply(lambda x: {1.0:'H', 0.0:'L'}.get(x,''))

    df['prom_strength']=[
        x
        for i,df_word in df.groupby(['word_i','word_ipa_i'])
        for x in getstrength(df_word)
    ]
    df['is_stressed']=(df['prom_stress']>0).apply(np.int32)
    df['is_unstressed']=(df['prom_stress']==0).apply(np.int32)
    df['is_heavy']=(df['prom_weight']==1).apply(np.int32)
    df['is_light']=(df['prom_weight']==0).apply(np.int32)
    df['is_peak']=(df['prom_strength']==1).apply(np.int32)
    df['is_trough']=(df['prom_strength']==0).apply(np.int32)


def get_info_byline(txtdf):
    linedf=txtdf.xs([0,0,0],level=['word_i','word_ipa_i','syll_i'])
    linedf=linedf.reset_index(level=['word_str','word_ipa','syll_str','syll_ipa','line_ii'],drop=True)
    return linedf#.reset_index().set_index(['stanza_i','line_i'])







sonnet="""
How heavy do I journey on the way,
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
My grief lies onward and my joy behind.
"""