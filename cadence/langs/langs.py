from ..imports import *
# from .english import *
from .english import scan as en_scan, get as en_get
from .english import get_df
SYLLABIFY_DF_D={}

CODE2LANG = {
    'en':en_scan,
}
CODE2LANG_SYLLABIFY={
    'en':en_get,
}

def ipa_to_stress(syl_ipa,numeric=True):
    if not syl_ipa or type(syl_ipa)!=str:
        return np.nan if numeric else ''
    elif syl_ipa[0]=="'":
        return 1.0 if numeric else 'P'
    elif syl_ipa[0]== "`":
        return 0.5 if numeric else 'S'
    else:
        return 0.0 if numeric else 'U'


def get_vowels(sylipa):
    return [
        ipa
        for ipa in sylipa
        if get_d_ipa().get(ipa,{}).get('syll') == True
    ]

def syll_is_dipthong(sylipa):
    return len(get_vowels(sylipa))>1

def syll_ends_with_consonant(sylipa):
    return get_d_ipa().get(sylipa[-1],{}).get('syll')==False

def syll_is_heavy(sylipa):
    return syll_ends_with_consonant(sylipa) or syll_is_dipthong(sylipa)

def ipa_to_weight(sylipa,numeric=True):
    is_heavy = syll_is_heavy(sylipa)
    if is_heavy:
        return 1.0 if numeric else 'H'
    else:
        return 0.0 if numeric else 'L'


def apply_proms_sylls(word_df):
    df=word_df
    cols=set(df.columns)
    if 'syll_ipa' in cols:
        df['prom_stress']=df['syll_ipa'].apply(ipa_to_stress)
        df['prom_weight']=df['syll_ipa'].apply(getweight)
        df['prom_strength']=[
            x
            for i,df_word in df.groupby('word_ipa_i')
            for x in getstrength(df_word.prom_stress)
        ]
        df['is_stressed']=(df['prom_stress']>0).apply(np.int32)
        df['is_unstressed']=(df['prom_stress']==0).apply(np.int32)
        df['is_heavy']=(df['prom_weight']==1).apply(np.int32)
        df['is_light']=(df['prom_weight']==0).apply(np.int32)
        df['is_peak']=(df['prom_strength']==1).apply(np.int32)
        df['is_trough']=(df['prom_strength']==0).apply(np.int32)

SYLL_LD_CACHE={}
def get_syllable_ld(word_str,lang=DEFAULT_LANG,force=False,**kwargs):
    global SYLL_LD_CACHE
    key=(lang,word_str.strip())
    if not key in SYLL_LD_CACHE:
        # print('looking up:',key)
        ld=CODE2LANG_SYLLABIFY[lang](word_str.strip(), **kwargs)
        # is_punc=not any(x.isalpha() for x in word_str)
        if not ld:
            ld=[{
                'word_ipa_i':0,
                'syll_i':0,
                'word_str':word_str,
                'word_tok':to_token(word_str),
                'word_ipa':"",
                'word_nsyll':0,
                'syll_ipa':"",
                'syll_str':word_str,# if is_punc else 
                'word_isfunc':np.nan
            }]
            # pass
        else:
            # tune ups
            for dx in ld:
                syll_ipa=dx['syll_ipa']
                dx['syll_stress']=ipa_to_stress(syll_ipa,numeric=False)
                dx['syll_weight']=ipa_to_weight(syll_ipa,numeric=False)
                dx['prom_stress']=ipa_to_stress(syll_ipa,numeric=True)
                dx['prom_weight']=1.0 if dx['syll_weight']=='H' else 0.0
            
            stresses = dict((dxi,dx.get('prom_stress')) for dxi,dx in enumerate(ld))
            if None not in set(stresses.values()):
                strengths = getstrength(stresses)
                for i,strength in enumerate(strengths):
                    ld[i]['prom_strength']=strength
        SYLL_LD_CACHE[key]=ld
    return [
        {**dx, **{'word_str':word_str}}
        for dx in SYLL_LD_CACHE[key]
    ]



SYLL_DF_CACHE={}
def get_syllable_df(word_str,lang=DEFAULT_LANG,force=False,**kwargs):
    global SYLL_DF_CACHE
    key=(lang,word_str)
    if not key in SYLL_DF_CACHE:
        # print('df looking up')
        odf=pd.DataFrame(get_syllable_ld(word_str,force=force,**kwargs))
        SYLL_DF_CACHE[key]=odf
    return SYLL_DF_CACHE[key]


def syllabify_df(df,**kwargs):
    df=resetindex(df)
    cols=set(df.columns)
    dfsyll=pd.concat(
        get_syllable_df(word_str,index=False,**kwargs)
        for word_str in df.word_str.unique()
    )
    if not len(dfsyll): return pd.DataFrame()
    odf=df.merge(dfsyll,on='word_str',how='left')
    ## mtree
    for col in ['prom_pstress', 'prom_lstress', 'prom_tstress', 'prom_pstrength']:
        if col in cols:
            odf.loc[
                ((odf['prom_stress']==0.0) & (odf['word_nsyll']>1)),
                col
            ]=np.nan
    return odf


def to_lang(lang_code=None):
    global LANGS
    return LANGS[lang_code]

D_IPA=None
def get_d_ipa(fn=PATH_IPA_FEATS):
    global D_IPA
    if D_IPA is None: D_IPA=pd.read_csv(fn).set_index('ipa').T.to_dict()
    return D_IPA



def assign_proms(df):
    if not len(df): return
    # set proms
    df['prom_stress']=pd.to_numeric(df['syll_ipa'].apply(getstress),errors='coerce')
    df['prom_weight']=pd.to_numeric(df['syll_ipa'].apply(getweight),errors='coerce')
    # df['syll_stress']=df.prom_stress.apply(lambda x: {1.0:'P', 0.5:'S', 0.0:'U'}.get(x,''))
    df['syll_weight']=df.prom_weight.apply(lambda x: {1.0:'H', 0.0:'L'}.get(x,''))

    df['prom_strength']=[
        x
        for i,df_word in df.groupby('word_ipa_i')
        for x in getstrength(df_word)
    ]
    df['is_stressed']=(df['prom_stress']>0).apply(np.int32)
    df['is_unstressed']=(df['prom_stress']==0).apply(np.int32)
    df['is_heavy']=(df['prom_weight']==1).apply(np.int32)
    df['is_light']=(df['prom_weight']==0).apply(np.int32)
    df['is_peak']=(df['prom_strength']==1).apply(np.int32)
    df['is_trough']=(df['prom_strength']==0).apply(np.int32)


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

# def getstrength(df_word):
#     stresses=dict(zip(df_word.syll_i,df_word.prom_stress))
def getstrength(stresses):
    strengths=[]
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
        strengths.append(strength)
    return strengths

