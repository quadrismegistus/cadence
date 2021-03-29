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
def to_stanzas(full_txt):
    return [st.strip() for st in full_txt.strip().split('\n\n') if st.strip()]
def to_lines(stanza_txt):
    return [l.strip() for l in stanza_txt.split('\n') if l.strip()]
def to_words(line_txt,lang_code=DEFAULT_LANG):
    lang = to_lang(lang_code)
    return lang.tokenize(line_txt)
def to_syllables(word_txt,lang_code=DEFAULT_LANG):
    return lang.syllabify(word_txt)

def scan(txt_or_fn,lang=DEFAULT_LANG,progress=True,incl_alt=INCL_ALT,num_proc=DEFAULT_NUM_PROC,**kwargs):
    full_txt=to_txt(txt_or_fn)
    if not full_txt: return

    df=pd.DataFrame()
    objs=[]

    for stanza_i,stanza_txt in enumerate(to_stanzas(full_txt)):
        for line_i,line_txt in enumerate(to_lines(stanza_txt)):
            df=line2df(line_txt,lang=lang,incl_alt=incl_alt,**kwargs)            
            df['stanza_i']=stanza_i+1
            df['line_i']=line_i+1
            df['line_str']=line_txt
            df['is_syll']=[int(x) for x in df['syll_ipa']!='']
            objs+=[df]
    odf=pd.concat(objs)
    assign_proms(odf)
    
    # add other info
    return setindex(odf)
    
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