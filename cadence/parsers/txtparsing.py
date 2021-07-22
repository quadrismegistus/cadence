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

def to_lineparts(linetxt,seps=set(',:;––'),min_len=1,max_len=25):
    o=[]
    for sent in to_sents_str(linetxt):
        toks=tokenize_agnostic(sent)
        ophrase=[]
        for tok in toks:
            ophrase+=[tok]
            ophrase_len=len([x for x in ophrase if x[0].isalpha()])
            if ophrase_len>=min_len and (tok in seps or ophrase_len>=max_len):
                o+=[''.join(ophrase)]
                ophrase=[]
        if ophrase: o+=[''.join(ophrase)]
    return o    

def to_words(line_txt,lang_code=DEFAULT_LANG):
    lang = to_lang(lang_code)
    o=lang.tokenize(line_txt)
    #print(o)
    #stop
    return o
    
def to_syllables(word_txt,lang_code=DEFAULT_LANG):
    return lang.syllabify(word_txt)

def scan(txt_or_fn,**kwargs):
    return setindex(
        pd.concat(
            scan_iter(txt_or_fn,**kwargs)
        )
    )

def do_scan_iter(obj,cache=False,**kwargs):
    (
        stanza_i,stanza_txt,
        line_i,line_txt,
        linepart_i,linepart_txt,
        key
    ) = obj
#     print(key)
    if cache:
        with get_db('lines','r') as db:
            if key in db:
                return db[key]
    odf=line2df(linepart_txt, **kwargs)
    try:
        assign_proms(odf)
    except KeyError:
        pass
    if cache:
        with get_db('lines',autocommit=True) as db:
            db[key]=odf
    return odf
        

def scan_iter(txt_or_fn,lang=DEFAULT_LANG,
        progress=True,
        incl_alt=INCL_ALT,
        num_proc=DEFAULT_NUM_PROC,
        linebreaks=True,
        phrasebreaks=True,
        verse=None,
        prose=None,
        desc='Iterating over line scansions',
        **kwargs):
    full_txt=to_txt(txt_or_fn)
    if not full_txt: return
    
    if verse:
        linebreaks=True
        phrasebreaks=False
    elif prose:
        linebreaks=False
        phrasebreaks=True

    df=pd.DataFrame()
    dfl=[]
    to_lines_now = to_lines_str if linebreaks else to_sents_str
    kwargs['lang']=lang
    kwargs['incl_alt']=incl_alt
    
    def getkey(linepart_txt):
        return hashstr(str([
            linepart_txt,
            sorted(kwargs.items())
        ]))[:12]
        
    objs=[
        (
            stanza_i,stanza_txt,
            line_i,line_txt,
            linepart_i,linepart_txt,
            getkey(linepart_txt)
        )
        for stanza_i,stanza_txt in enumerate(to_stanzas(full_txt))
        for line_i,line_txt in enumerate(to_lines_now(stanza_txt))
        for linepart_i,linepart_txt in enumerate(
            to_lineparts(line_txt) if phrasebreaks else [line_txt]
        )
    ]    
    
#     with get_db('lines','r') as db:
#         objs_done=[]
#         objs_todo=[]
#         for obj in objs:
#             key=obj[-1]
#             if key in db:
#                 objs_done[key]=db[key]
    
    
    

    iterr=pmap_iter(
        do_scan_iter,
        objs,
        kwargs=kwargs,
        num_proc=num_proc,
        desc=desc,
        progress=progress
    )

#     dfl=[]
    i=0#
    #with get_db('lines','c') as db:
    lpi=None
    ol=[]
    for dfi,df in enumerate(iterr):
        (stanza_i,stanza_txt,line_i,line_txt,linepart_i,linepart_txt,key) = objs[dfi]
        lpinow=(stanza_i,line_i)
        if lpi is not None and lpi!=lpinow and ol:
            yield pd.concat(ol)
            ol=[]
        
        df['stanza_i']=stanza_i+1
        df['line_i']=line_i+1
        df['line_str']=linepart_txt#line_txt
        df['linepart_i']=linepart_i+1
        ol+=[df]
        lpi=lpinow
    if ol: yield pd.concat(ol)

        #db[key]=df
#         yield df
        #i+=1
        #if i>=100: db.commit()
        #db.commit()

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