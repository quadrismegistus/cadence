from ..imports import *

# loading txt/strings
def to_txt(txt_or_fn):
    # load txt
    if not txt_or_fn: return
    if os.path.exists(txt_or_fn):
        with open(txt_or_fn) as f:
            txt=f.read()
    else:
        txt=txt_or_fn
    return txt

# tokenizers

# txt -> stanzas
def to_stanzas(full_txt):
    return [st.strip() for st in full_txt.strip().split('\n\n') if st.strip()]

# stanza -> line 
def to_lines(stanza_txt):
    return [l.strip() for l in stanza_txt.split('\n') if l.strip()]

# line -> words
def to_words(line_txt,lang_code=DEFAULT_LANG):
    lang = to_lang(lang_code)
    return lang.tokenize(line_txt)

# word -> sylls
def to_syllables(word_txt,lang_code=DEFAULT_LANG):
    return lang.syllabify(word_txt)



# --> 

def do_parse_phon(obj):
    stanza_i,line_i,line_txt,lang_code,incl_alt,kwargs = obj
    df=line2df(line_txt,lang=lang_code,incl_alt=incl_alt,**kwargs)
    cols=list(df.columns)
    df['stanza_i']=stanza_i
    df['line_i']=line_i
    prefix=['stanza_i','line_i','word_i','word_ipa_i','syll_i']
    df=df[prefix + [c for c in cols if c not in set(prefix)]]
    return df

def parse_phon(txt_or_fn,lang=DEFAULT_LANG,progress=True,incl_alt=INCL_ALT,num_proc=DEFAULT_NUM_PROC,**kwargs):
    full_txt=to_txt(txt_or_fn)
    if not full_txt: return

    #stanza_iter = to_stanzas(full_txt) if not progress else tqdm(to_stanzas(full_txt),desc='Tokenizing and syllabifying')


    df=pd.DataFrame()
    objs=[]

    for stanza_i,stanza_txt in enumerate(to_stanzas(full_txt)):
        for line_i,line_txt in enumerate(to_lines(stanza_txt)):
            objs+=[(stanza_i,line_i,line_txt,lang,incl_alt,kwargs)]
    
    df = pd.concat(
        pmap(
            do_parse_phon,
            objs,
            num_proc=num_proc,
            desc='Tokenizing and syllabifying',
            progress=progress
        )
    )

    # assign proms
    assign_proms(df)
    return df
    

def assign_proms(df):
    # set proms
    df['prom_stress']=pd.to_numeric(df['syll_ipa'].apply(getstress),errors='coerce')
    # # df['syll_weight']=[
    # #     weight
    # #     for i,df_syll in df.groupby(['word_i','word_ipa_i','syll_i'])
    # #     for weight in self.lang.getweight(df_syll)
    # # ]f
    df['prom_strength']=[
        x
        for i,df_word in df.groupby(['word_i','word_ipa_i'])
        for x in getstrength(df_word)
    ]
    
    df['is_stressed']=(df['prom_stress']>0).apply(np.int32)
    df['is_unstressed']=1-df['is_stressed']
    df['is_peak']=(df['prom_strength']==True).apply(np.int32)
    df['is_trough']=(df['prom_strength']==False).apply(np.int32)