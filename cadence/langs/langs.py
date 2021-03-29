from ..imports import *
from .english import scan as en_scan
CODE2LANG = {
    'en':en_scan
}

def to_lang(lang_code=None):
    global LANGS
    return LANGS[lang_code]


DF_IPA=None
def get_df_ipa(fn=PATH_IPA_FEATS):
    global DF_IPA
    if DF_IPA is None: DF_IPA=pd.read_csv(fn).set_index('ipa')
    return DF_IPA

def to_phons(syll_ipa):
    pass

def line2df(line_txt,lang=DEFAULT_LANG,sby=['word_i','word_ipa_i','syll_i'],incl_alt=INCL_ALT,**y):
    func = CODE2LANG.get(lang, CODE2LANG[DEFAULT_LANG] )
    ld=func(line_txt,incl_alt=incl_alt,**y)
    if not ld: return pd.DataFrame()
    df=pd.DataFrame(ld)
    # annotate proms
    # df=anno_proms(df)
    try:
        return df.sort_values(sby)[sby + [col for col in df.columns if col not in set(sby)]]
    except KeyError:
        return df



# ## langs

# def phontypes(self):
#     return sorted(list(set(get_df_ipa().ipa)),key=lambda x: -len(x))


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
    dfipa=get_df_ipa()
    phondata = dfipa.loc[[ipastr for ipastr in sylipa if ipastr in set(dfipa.index)]]
    if not len(phondata): return np.nan
    ends_with_cons=phondata['cons'].iloc[-1]==True
    has_long_vowel=any(x==True for x in phondata['long'])
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

