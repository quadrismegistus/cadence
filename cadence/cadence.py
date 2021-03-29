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