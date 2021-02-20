from tqdm import tqdm
import pandas as pd,numpy as np,random,json,pickle
from collections import defaultdict,Counter
from constraints import *

sortby_l=['stanza_i','line_i','word_i','word_ipa_i','syll_i']#,'phon_i']
MIN_WORDS_IN_PHRASE=2

class Unit(object):
    pass

## langs
class Language(object):
    def __init__(self):
        self.load_ipa()

    def load_ipa(self,fn='../data/data.feats.ipa.csv'):
        self.df_ipa=pd.read_csv(fn)#.set_index('index')
        self.df_ipa.columns = ['phon_'+c for c in self.df_ipa.columns]

    @property
    def phontypes(self):
        return sorted(list(set(self.df_ipa.phon_ipa)),key=lambda x: -len(x))

    def syll_ipa2phon_ipa(self,sylipa):
        ipastr=sylipa.replace("'",'').replace("`","")
        
        phonnow = ''
        phons=[]

        while ipastr:
            for phonstr in self.phontypes:
                    if ipastr.startswith(phonstr):
                        phons.append(phonstr)
                        ipastr=ipastr[len(phonstr):]
                        break
            else:
                break
        if ipastr:
            phons.append(ipastr)
        return phons


    # stress
    def getstress(self,sylipa):
        if not sylipa.strip(): return ' '
        if sylipa.startswith("'"):
            return 1.0#""
        elif sylipa.startswith("`"):
            return 0.5
        return 0.0

    def getweight(self,df_syll):
        ends_with_cons=df_syll.sort_values('phon_i')['phon_cons'].iloc[-1]==True
        has_long_vowel=any(x==True for x in df_syll['phon_long'])
        # print(has_long_vowel,ends_with_cons,[df_syll.sort_values('phon_i')['phon_cons'].iloc[-1]])
        is_dipthong=None #@TODO
        weight='H' if ends_with_cons or has_long_vowel or is_dipthong else 'L'
        return [weight for i in range(len(df_syll))]

    def getstrength(self,df_word):
        stresses=dict(zip(df_word.syll_i,df_word.syll_stress))
        strengths={}
        for si,(syll_i,syl) in enumerate(sorted(stresses.items())):
            prv=stresses.get(syll_i-1)
            nxt=stresses.get(syll_i+1)
            if nxt!=None and prv!=None:
                if syl>nxt or syl>prv:
                    strength=True
                elif syl<nxt or syl<prv:
                    strength=False
                else:
                    strength=None
            elif prv==None and nxt!=None:
                if syl>nxt:
                    strength=True
                elif syl<nxt:
                    strength=False
                else:
                    strength=None
            elif prv!=None and nxt==None:
                if syl>prv:
                    strength=True
                elif syl<prv:
                    strength=None
                else:
                    strength=None
            elif prv==None and nxt==None:
                strength=None
            else:
                raise Exception("How? -getstrength()")
            #strengths.append(strength)
            strengths[syll_i]=strength
        return [
            strengths.get(syll_i)
            for syll_i in df_word.syll_i
        ]

class English(Language):
    contractions = {"n't","'ve","'ll","'m","'d","'s","'m","'re"}

    def __init__(self):
        super().__init__()
        self.load_cmu()
    
    def tokenize(self,txt):
        import nltk
        l=nltk.word_tokenize(txt,language="english")
        l2=[]
        for w in l:
            if l2 and (w.startswith("'") or w.lower() in self.contractions):
                l2[-1]+=w
            else:
                l2+=[w]
        return l2

    def load_cmu(self,fn='../data/data.en.cmudict.txt'):
        self.tok2ipa=defaultdict(list)
        with open(fn) as f:
            for ln in f:
                if not '\t' in ln: continue
                tok,ipa=ln.strip().split('\t',1)
                self.tok2ipa[tok]+=[ipa]



    # def syllabify(self,tok):
    #     ipas=self.tok2ipa.get(tok.lower(),[" "])
    #     all_ld=[]
    #     for ipa_i,ipa in enumerate(ipas):
    #         for syll_i,syll_ipa in enumerate(ipa.split('.')):
    #             phons=self.syll_ipa2phon_ipa(syll_ipa)
    #             #print(syll_i,syll_ipa,phons)
    #             for phon_i,phon_str in enumerate(phons):
    #                 dx={
    #                     'word_str':tok,
    #                     'word_ipa_i':ipa_i,
    #                     'word_ipa':ipa,
    #                     'syll_i':syll_i,
    #                     'syll_ipa':syll_ipa,
    #                     'phon_i':phon_i,
    #                     'phon_ipa':phon_str,
    #                 }
    #                 all_ld.append(dx)
    #     df=pd.DataFrame(all_ld)
    #     df=df.merge(self.df_ipa,on='phon_ipa')
    #     df=df.sort_values(['word_ipa_i','syll_i','phon_i'])
    #     return df
    def syllabify(self,tok):
        ipas=self.tok2ipa.get(tok.lower(),[" "])
        all_ld=[]
        for ipa_i,ipa in enumerate(ipas):
            for syll_i,syll_ipa in enumerate(ipa.split('.')):
                dx={
                    'word_str':tok,
                    'word_ipa_i':ipa_i,
                    'word_ipa':ipa,
                    'syll_i':syll_i,
                    'syll_ipa':syll_ipa,
                }
                all_ld.append(dx)
        df=pd.DataFrame(all_ld)
        df=df.sort_values(['word_ipa_i','syll_i'])#,'phon_i'])
        return df





### texts
class Text(Unit):
    def __init__(self,txt=None,fn=None,lang='en',lang_kwargs={}):
        # load
        assert txt or fn
        self.txt=txt
        if not self.txt and fn and os.path.exists(fn):
            with open(fn) as f:
                self.txt=f.read().replace('\r\n','\n').replace('\r','\n').strip()
        assert type(self.txt)==str
        # load
        self.langcode=lang
        self.lang=code2lang[lang](**lang_kwargs)
    
    @property
    def df(self):
        if not hasattr(self,'_df') or self._df is None:
            ld_words=[]
            stanza_i=0
            line_i=0
            word_i=0
            for st_i,stanza in enumerate(self.txt.split('\n\n')):
                stanza=stanza.strip()
                for i,ln in enumerate(stanza.split('\n')):
                    if not ln.strip(): continue
                    for wi,w in enumerate(self.lang.tokenize(ln)):
                        wdx={
                            'stanza_i':stanza_i,
                            'line_i':line_i,
                            'line_str':ln,
                            'word_i':word_i,
                            'word_str':w
                        }
                        ld_words.append(wdx)
                        word_i+=1
                    line_i+=1
                stanza_i+=1

            # join up
            dfw=self.df_words=pd.DataFrame(ld_words)
            dfsyll = pd.concat([self.lang.syllabify(w) for w in dfw.word_str])    
            df=self._df=dfw.merge(dfsyll,on='word_str').sort_values(sortby_l)


            # annotate all features
            df['syll_stress']=df['syll_ipa'].apply(self.lang.getstress)
            # df['syll_weight']=[
            #     weight
            #     for i,df_syll in df.groupby(['word_i','word_ipa_i','syll_i'])
            #     for weight in self.lang.getweight(df_syll)
            # ]
            df['syll_strength']=[
                weight
                for i,df_word in df.groupby(['word_i','word_ipa_i'])
                for weight in self.lang.getstrength(df_word)
            ]


        return self._df

    def all_phonological_combos(self,df=None,min_words_in_phrase=MIN_WORDS_IN_PHRASE):
        if df is None: df=self.df
        line2combos={}
        for line_i,line_df in sorted(df.groupby('line_i')):
            word_rows = [
                set(list(zip(word_df.word_i, word_df.word_ipa_i, word_df.word_ipa)))                
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
            # pprint(word_rows_div)
            
            # gen combos
            all_combos = []
            for word_row_div in word_rows_div:
                combos = list(product(*word_row_div))
                all_combos.extend(combos)
            line2combos[line_i]=all_combos
        return line2combos
            

    def all_metrical_combos(self,df_combo):
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
        # for wsc in wordsyllsmeter_combos:
            # print(wsc)
        return wordsyllsmeter_combos


    def constraints(self):
        return {
            'w/stressed':no_stressed_weaks,
            's/unstressed':no_unstressed_strongs,
            'w/peak':no_weak_peaks,
        }

    def parse_metrical_combo(self,df_mcombo):
        for cname,cfunc in self.constraints().items():
            df_mcombo['*'+cname]=cfunc(df_mcombo)
        return df_mcombo


    def parse_phonological_combo(self,df_combo):
        wordsyllsmeter_combos = self.all_metrical_combos(df_combo)
        dfwsc = df_combo.set_index(['word_i','syll_i'])
        dfall=pd.DataFrame()
        # for wi,wsc in enumerate(tqdm(wordsyllsmeter_combos,desc='Parsing line combos',position=1)):
        for wi,wsc in enumerate(wordsyllsmeter_combos):#,desc='Parsing line combos',position=1)):
            ws2mtr=dict(([((w,s),c) for w,s,c in wsc]))
            df_mcombo = pd.DataFrame(dfwsc.loc[ws2mtr.keys()].reset_index().sort_values(['word_i','syll_i']))
            df_mcombo['parse']=[ws2mtr.get((w,s)) for w,s in zip(df_mcombo.word_i,df_combo.syll_i)]
            
            df_mcombo_parsed = self.parse_metrical_combo(df_mcombo)
            df_mcombo_parsed['meter_combo_i']=int(wi)
            df_mcombo_parsed['meter_combo_str']=''.join(df_mcombo['parse'])
            cstrcols=[col for col in df_mcombo_parsed.columns if col.startswith('*')]
            df_mcombo_parsed['*total']=df_mcombo_parsed[cstrcols].sum(axis=1)
            
            dfcols=['stanza_i','line_i','word_i','word_ipa_i','syll_i','meter_combo_i','meter_combo_str','parse']
            dfall=dfall.append(df_mcombo_parsed[
                dfcols+cstrcols+['*total']
            ])
        return dfall

        # stop
        
        # df=self.df.groupby(('word_i','word_ipa_i'))


    def parse(self):
        line2combos = self.all_phonological_combos()
        dfall=pd.DataFrame()
        for line_i,line_combos in tqdm(sorted(line2combos.items()),desc='Parsing lines',position=0):
            for ci,combo in enumerate(line_combos):
                df_combo = self.df[
                    self.df.apply(
                        lambda row: (row.word_i,row.word_ipa_i,row.word_ipa) in set(combo),
                        axis=1
                    )
                ]
                df=self.parse_phonological_combo(df_combo)
                df['line_combo_i']=int(ci)
                dfall=dfall.append(df)
        
        # join?
        idxcols=['stanza_i','line_i','word_i','word_ipa_i','syll_i']#,'phon_i']
        #newcols=idxcols[:2] + ['line_str','word_str','line_combo_i','meter_combo_i'] + idxcols[2:]
        newcols=['stanza_i','line_i','line_str','line_combo_i','meter_combo_i','meter_combo_str','word_i','word_str','word_ipa_i','word_ipa','syll_i','syll_ipa','parse']
        dfj=self._df.set_index(idxcols).join(dfall.set_index(idxcols)).reset_index()
        return dfj.sort_values(newcols)[newcols+list(set(dfj.columns)-set(newcols))].set_index(newcols)



## code 2 lang lookup
code2lang={
    'en':English
}

def product(*args):
	if not args:
		return iter(((),)) # yield tuple()
	return (items + (item,)
		for items in product(*args[:-1]) for item in args[-1])




if __name__=='__main__':
    # lang = English()
    # x=lang.tokenize("This isn't a test! ok")
    # print(x)
    # y=lang.syllabify('orthography')
    # print(y)

    pd.options.display.max_rows=50
    t=Text("""
BELOVED, gaze in thine own heart,
The holy tree is growing there;
From joy the holy branches start,
And all the trembling flowers they bear.
    """)
    # print(t.df)
    df=t.parse()
    print(df)

    xdf=df.reset_index()
    x=xdf[xdf.line_i==0].groupby(['line_str','meter_combo_str','line_combo_i','meter_combo_i']).mean().reset_index().sort_values('*w/peak').tail(10)
    print(x)
    print