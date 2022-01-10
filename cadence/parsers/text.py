from ..imports import *
from .txtparsing import *
from .stanzanlp import *
from .mtree import *

def Text(*args,**kwargs):
    return TextModel(*args,**kwargs)

class TextModel(object):
    def __init__(self,txt_or_fn,**kwargs):
        self.fn,self.txt=to_fn_txt(txt_or_fn)
        self.attrs=kwargs

        self._numparas={}
        self._paras_d={}
        self._words_d={}
        self._sylls_d={}
        self._paras_df={}
        self._words_df={}
        self._sylls_df={}
        self._nlp_doc={}
        self._syntax_d={}
        self._syntax_df={}
        self._mtree_d={}
        self._mtree_df={}

    ####################################
    ## PARAGRAPHS
    ####################################

    def gen_paras_d(self,**kwargs):
        if not self._paras_d:
            for para_d in tokenize_paras_ld(self.txt, **kwargs):
                self._paras_d[para_d['para_i']] = para_d
            self._numparas=len(self._paras_d)

    def get_para_d(self,para_i,**kwargs):
        self.gen_paras_d()
        return self._paras_d.get(para_i)
    
    def get_paras_ld(self,shuffle_paras=SHUFFLE_PARAS,lim_paras=LIM_PARAS,**kwargs):
        self.gen_paras_d()
        paras_ld=[v for k,v in sorted(self._paras_d.items())]
        if shuffle_paras: random.shuffle(paras_ld)
        if lim_paras: paras_ld=paras_ld[:lim_paras]
        return paras_ld

    def iter_paras_d(self,
            progress=True,
            desc='Iterating over paragraphs',
            **kwargs):
        paras_ld=self.get_paras_ld(**kwargs)
        if progress: paras_ld=tqdm(paras_ld,desc=desc)
        yield from paras_ld
    
    def paras(self,**kwargs):
        return getcache_df(self, '_paras_df', self.iter_paras_d, cache=False, **kwargs)
    


    ####################################
    ## WORDS
    ####################################

    def get_words_ld(self,para_i,**kwargs):
        if not para_i in self._words_d:
            para_d=self.get_para_d(para_i)
            if para_d is None: 
                print(para_i)
                return []
            para_str=para_d['para_str']
            self._words_d[para_i]=list(tokenize_sentwords_iter(para_str,para_i=para_i,**kwargs))
        return self._words_d[para_i]
    def get_words_df(self,para_i,**kwargs):
        odf=pd.DataFrame(self.get_words_ld(para_i,**kwargs))
        return odf.assign(para_i=para_i)
    
    def iter_words_d(self,**kwargs):
        if not 'desc' in kwargs: kwargs['desc']='Tokenizing sentences and words'
        for para_d in self.iter_paras_d(**kwargs):
            yield from self.get_words_ld(para_d['para_i'])
    def words(self,**kwargs):
        return getcache_df(self, '_words_df', self.iter_words_d, cache=False, **kwargs)
    
    ####################################
    ## SYLLABIFY
    ####################################

    def syllabify_df(self,df,**kwargs):
        try:
            return syllabify_df(df,**kwargs)
        except Exception as e:
            print('!!',e)
            return df


    def get_sylls_df(self,para_i,**kwargs):
        if not para_i in self._sylls_df:
            dfwords=self.get_words_df(para_i,**kwargs)
            self._sylls_df[para_i]=self.syllabify_df(dfwords,**kwargs)
        return self._sylls_df[para_i].assign(para_i=para_i)
    
    def iter_sylls_d(self,**kwargs):
        if not 'desc' in kwargs: kwargs['desc']='Tokenizing syllables'
        for para_d in self.iter_paras_d(**kwargs):
            yield self.get_sylls_df(para_d['para_i'])

    def sylls(self,**kwargs):
        return syllabify_df(self.words())


    ####################################
    ## NLP DOCS
    ####################################

    def get_nlp_doc(self,para_i,**kwargs):
        if not para_i in self._nlp_doc:
            para_words_ld=self.get_words_ld(para_i,**kwargs)
            para_words_ll=tokenize_sentwords_ll(para_words_ld)
            self._nlp_doc[para_i]=get_nlp_doc(para_words_ll,para_i=para_i,**kwargs)
        return self._nlp_doc[para_i]
    def iter_nlp_docs(self,**kwargs):
        if not 'desc' in kwargs: kwargs['desc']='Parsing NLP documents'
        for para_d in self.iter_paras_d(**kwargs):
            yield self.get_nlp_doc(para_d['para_i'],**kwargs)
    def docs(self,**kwargs):
        return list(self.iter_nlp_docs(**kwargs))

    ####################################
    ## NLP FEATS
    ####################################

    def get_syntax_df(self,para_i,sent_i=None,index=True,**kwargs):
        if not para_i in self._syntax_d:
            para_doc=self.get_nlp_doc(para_i)
            dffeat=get_nlp_feats_df(para_doc, **kwargs)
            dfword=self.get_words_df(para_i)
            try:
                #odf=dfword.merge(dffeat,on=['sent_i','word_i'])
                odf=dffeat
            except KeyError:
                odf=dfword
            self._syntax_d[para_i]=odf
        return self._syntax_d[para_i].assign(para_i=para_i)
    def merge_syntax_df(self, para_i, para_word_df, joiner=COLS_JOINER, **kwargs):
        try:
            dfsyntax=self.get_syntax_df(para_i, **kwargs)
            odf=para_word_df.merge(dfsyntax,on=COLS_JOINER,how='left')
            return odf
        except AssertionError as e:
            print('!!',e)
            return para_word_df

            
    def iter_syntax_df(self,**kwargs):
        if not 'desc' in kwargs: kwargs['desc']='Parsing NLP documents'
        for para_d in self.iter_paras_d(**kwargs):
            yield self.get_syntax_df(para_d['para_i'],**kwargs)
    def syntax(self,index=True,**kwargs):
        o=list(self.iter_syntax_df(index=False,**kwargs))
        odf=pd.concat(o).fillna('') if len(o) else pd.DataFrame()
        return setindex(odf) if index else odf

    ####################################
    ## Mtrees
    ####################################

    def get_mtrees(self,para_i,sent_i=None,**kwargs):
        if not para_i in self._mtree_d:
            self._mtree_d[para_i]=[
                get_mtree(sent,**kwargs)
                for sent in self.get_nlp_doc(para_i,**kwargs).sentences
            ]
        o=self._mtree_d[para_i]
        return o if sent_i is None else o[sent_i-1]
    def get_mtrees_df(self,para_i,sent_i=None,**kwargs):
        if not para_i in self._mtree_df:
            mtrees=self.get_mtrees(para_i,**kwargs)
            o=[
                mtreeobj.get_stats(**kwargs).assign(sent_i=sent_i+1) if mtreeobj is not None else pd.DataFrame()
                for sent_i,mtreeobj in enumerate(mtrees)
            ]
            self._mtree_df[para_i]=pd.concat(o) if len(o) else pd.DataFrame()
        odf=self._mtree_df[para_i]
        return odf.assign(para_i=para_i)

    def merge_mtrees_df(self,para_i,para_word_df,**kwargs):
        try:
            mdf=self.get_mtrees_df(para_i,**kwargs)
            mdfcols=set(mdf.columns)
            okcols=(mdfcols - set(para_word_df.columns)) | set(COLS_JOINER)
            return para_word_df.merge(mdf[okcols], on = COLS_JOINER, how='left')
        except AssertionError as e:
            print('!!',e)
            return para_word_df
        
    def iter_mtrees_df(self,**kwargs):
        for para_d in self.iter_paras_d(**kwargs):
            para_i=para_d['para_i']
            yield self.get_mtrees_df(para_i,**kwargs)

    def mtrees(self,index=True,**kwargs):
        o=list(self.iter_mtrees_df(index=False,**kwargs))
        odf=pd.concat(o).fillna('') if len(o) else pd.DataFrame()
        return setindex(odf) if index else odf

    ####################################
    ## Combined
    ####################################

    def iter_data(self,**kwargs):
        for para_d in self.iter_paras_d(**kwargs):
            odf=self.get_data(para_d['para_i'],**kwargs)
            if len(odf): yield odf

    def get_data(self,para_i,sent_i=None,syntax=True,sylls=True,mtree=True,index=True,proms=True,**kwargs):
        odf = self.get_words_df(para_i,**kwargs)
        if syntax: odf=self.merge_syntax_df(para_i,odf,index=False,**kwargs)
        if mtree: odf=self.merge_mtrees_df(para_i, odf, **kwargs)
        if sylls: odf=self.syllabify_df(odf,**kwargs)
        if odf is None: return pd.DataFrame()
        if len(odf) and sent_i is not None: odf=odf[odf.sent_i==sent_i]
        if len(odf) and index: odf=setindex(odf)
        return odf

    # t.alldata=alldata

    