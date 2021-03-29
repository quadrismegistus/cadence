# system imports
from .imports import *




### convenient objs



### texts
class Text(object):
    def __init__(self,txt_or_fn,lang='en'):
        self.txt_or_fn=txt_or_fn
        self.lang=lang
        self._df_phon={}
        self._df_metr={}
    
    def parse_phon(self,**y):
        key=hashstr(self.txt_or_fn,self.lang)[:12]
        if key not in self._df_phon:
            self._df_phon[key] = parse_phon(self.txt_or_fn, lang=self.lang,**y)
        return self._df_phon[key]
    
    # def to_combos(self,df=None,incl_alt=True,**y):
    #     if df is None: df=self.to_df(incl_alt=incl_alt,**y)
    #     return all_combo_dfs(df, **y)

    def parse_meter(self,df=None,**y):
        key=hashstr(y)[:12]
        if not key in self._df_metr:
            if df is None: df = self.parse_phon(**y)
            l=[]
            for group in parse_lines(df,**y):
                yield group
                l+=[group]
            self._df_metr[key] = l
        # return self._df_metr[key]
        else:
            yield from l


    # def parse(self):
    #     line2combos = self.all_phonological_combos()
    #     # line2stressstr = 
    #     dfall=pd.DataFrame()
    #     for line_i,line_combos in tqdm(sorted(line2combos.items()),desc='Parsing lines',position=0):
    #         for ci,combo in enumerate(line_combos):
    #             df_combo = self.df[
    #                 self.df.apply(
    #                     lambda row: (row.word_i,row.word_ipa_i,row.word_ipa) in set(combo),
    #                     axis=1
    #                 )
    #             ]
    #             df=self.parse_phonological_combo(df_combo)
    #             df['line_combo_i']=int(ci)
    #             dfall=dfall.append(df)
        
    #     # join?
    #     idxcols=['stanza_i','line_i','word_i','word_ipa_i','syll_i']#,'phon_i']
    #     #newcols=idxcols[:2] + ['line_str','word_str','line_combo_i','meter_combo_i'] + idxcols[2:]
    #     newcols=['stanza_i','line_i','line_str','line_combo_i','stress_parse','line_combo_ipa','meter_combo_i','meter_combo_str','meter_combo_str_w','word_i','word_str','word_ipa_i','word_ipa','syll_i','syll_ipa','parse']
    #     dfj=self._df.set_index(idxcols).join(dfall.set_index(idxcols)).reset_index()
    #     return dfj.sort_values(newcols)[newcols+list(set(dfj.columns)-set(newcols))].set_index(newcols)
