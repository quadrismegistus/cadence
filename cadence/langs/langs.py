from ..imports import *
from .english import scan as en_scan
CODE2LANG = {
    'en':en_scan
}

def to_lang(lang_code=None):
    global LANGS
    return LANGS[lang_code]


D_IPA=None
def get_d_ipa(fn=PATH_IPA_FEATS):
    global D_IPA
    if D_IPA is None: D_IPA=pd.read_csv(fn).set_index('ipa').to_dict()
    return D_IPA



def to_phons(syll_ipa):
    pass

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

