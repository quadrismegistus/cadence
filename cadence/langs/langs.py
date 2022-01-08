from ..imports import *
from .english import scan as en_scan
from .english import get_df
SYLLABIFY_DF_D={}

CODE2LANG = {
    'en':en_scan
}
CODE2LANG_SYLLABIFY={
    'en':get_df,
}

def to_lang(lang_code=None):
    global LANGS
    return LANGS[lang_code]


D_IPA=None
def get_d_ipa(fn=PATH_IPA_FEATS):
    global D_IPA
    if D_IPA is None: D_IPA=pd.read_csv(fn).set_index('ipa').to_dict()
    return D_IPA



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



def syllabify_df(idf,num_proc=1,lang=DEFAULT_LANG,**kwargs):
    idfwords=list(getcol(idf,'word_str'))
    idfwordkey=(lang, tuple(idfwords))
    od={}
    word_strs=list(set(getcol(idf,'word_str')))
    o=[syllabify(word_str,**kwargs) for word_str in word_strs]
    odf=pd.concat(o).fillna(0) if len(o) else pd.DataFrame()
    if len(odf):
        odf=resetindex(idf).merge(odf,on='word_str',how='outer')
        for col in odf.columns:
            if col.endswith('_i') or col.startswith('is_'):
                odf[col]=odf[col].fillna(0).apply(int)
            elif col.endswith('_ipa') or col.endswith('_str'):
                odf[col]=odf[col].fillna('')
        assign_proms(odf)
        odf=setindex(odf)
        return odf
    return idf
    




def syllabify(word_str,lang=DEFAULT_LANG,**kwargs):
    global SYLLABIFY_DF_D
    key=(lang,word_str)

    if key in SYLLABIFY_DF_D: return SYLLABIFY_DF_D[key]
    
    odf=None
    with dc.Cache(PATH_DB_SYLLABIFY) as db:
        if not key in db:
            func=CODE2LANG_SYLLABIFY[lang]
            # eprint(f'Getting word via {func}')
            odf=func(word_str, **kwargs)
            db[key]=odf#.sample(frac=1)
        else:
            odf=db[key]
    # if odf is not None: assign_proms(odf)
    SYLLABIFY_DF_D[key]=odf
    return odf




def to_phons(syll_ipa):
    pass

def to_int(x):
    try:
        xint=int(x)
        if x==xint:
            return xint
    except ValueError:
        pass
    return x

def nice_int(odf):
    for col in odf.columns:
        if col.endswith('_i') or col.startswith('is_'):
            odf[col]=pd.to_numeric(odf[col], errors='coerce', downcast='integer')
    return odf



def line2df(line_txt,
        lang=DEFAULT_LANG,
        sby=['word_i','word_ipa_i','syll_i'],
        incl_alt=INCL_ALT,**y):
    
    func = CODE2LANG.get(lang, CODE2LANG[DEFAULT_LANG] )
    odf=func(line_txt,incl_alt=incl_alt,**y)
    # try:
    #     # odf=odf.sort_values(sby)[
    #     #     sby + [col for col in odf.columns if col not in set(sby)]
    #     # ]
    #     # odf['is_syll']=odf.syll_ipa.apply(lambda x: int(x==''))#[int(x) for x in odf['syll_ipa']!='']
    #     #odf['line_num_syll']=len(odf[(odf.is_syll==1) & (odf.word_ipa_i==1)])
    #     #uniqdf=odf[odf.is_syll==1].drop_duplicates(['word_i','syll_i'])
    #     #odf['line_num_syll']=len(uniqdf)
    # except KeyError as e:
    #     pass
    return odf




# ## langs


# stress
def getstress(sylipa):
    if not sylipa.strip(): return ' '
    if sylipa.startswith("'"): return 1.0#""
    elif sylipa.startswith("`"): return 0.5
    return 0.0

def getstress_str(sylipa):
    x=getstress(sylipa)
    if x==1.0: return 'P'
    if x==0.5: return 'S'
    if x==0.0: return 'U'
    return ''

def getweight(sylipa):
    dipa=get_d_ipa()
    phondata = [dipa[ipastr] for ipastr in sylipa if ipastr in dipa]
    if not len(phondata): return np.nan
    ends_with_cons=phondata[-1]['cons']==True
    has_long_vowel=any(x['long']==True for x in phondata)
    is_dipthong=None #@TODO
    weight=1 if ends_with_cons or has_long_vowel or is_dipthong else 0
    return weight

def getweight_str(sylipa):
    if x==1: return 'H'
    if x==0: return 'L'
    return ''

# def getweight(self,df_syll):
#     ends_with_cons=df_syll.sort_values('phon_i')['phon_cons'].iloc[-1]==True
#     has_long_vowel=any(x==True for x in df_syll['phon_long'])
#     # print(has_long_vowel,ends_with_cons,[df_syll.sort_values('phon_i')['phon_cons'].iloc[-1]])
#     is_dipthong=None #@TODO
#     weight='H' if ends_with_cons or has_long_vowel or is_dipthong else 'L'
#     return [weight for i in range(len(df_syll))]

def getstrength(df_word):
    stresses=dict(zip(df_word.syll_i,df_word.prom_stress))
    strengths={}
    for si,(syll_i,syl) in enumerate(sorted(stresses.items())):
        prv=stresses.get(syll_i-1)
        nxt=stresses.get(syll_i+1)
        if nxt!=None and prv!=None:
            if syl>nxt or syl>prv:
                strength=1.0
            elif syl<nxt or syl<prv:
                strength=0.0
            else:
                strength=np.nan
        elif prv==None and nxt!=None:
            if syl>nxt:
                strength=1.0
            elif syl<nxt:
                strength=0.0
            else:
                strength=np.nan
        elif prv!=None and nxt==None:
            if syl>prv:
                strength=1.0
            elif syl<prv:
                strength=0.0
            else:
                strength=np.nan
        elif prv==None and nxt==None:
            strength=np.nan
        else:
            raise Exception("How? -getstrength()")
        #strengths.append(strength)
        strengths[syll_i]=strength
    return [
        strengths.get(syll_i)
        for syll_i in df_word.syll_i
    ]

