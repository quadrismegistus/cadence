from ..imports import *
from .txtparsing import *
from .mtree import *
from .stanzanlp import *


def Text(*args,**kwargs):
    return TextModel(*args,**kwargs)

def Para(txt, *args, path_db=PATH_DB, force=False, para_i=None, **kwargs):
    _id=hashstr(txt)
    if not force:
        with dc.Cache(path_db) as db:
            if _id in db:
                # print(f'found {_id} in db')
                pdoc=pickle.loads(from_blosc(db[_id]))
                pdoc.i=para_i
                return pdoc

    pdoc=ParaModel(txt,*args,path_db=path_db,force=force,**kwargs)
    pdoc.i=para_i
    return pdoc

def Sent(txt, nlp_sent_obj=None, **kwargs):
    return SentModel(txt, nlp_sent_obj=nlp_sent_obj, **kwargs)





###
# TEXT
###

class TextModel(object):
    def __init__(self,txt_or_fn,shuffle_paras=SHUFFLE_PARAS,lim_paras=LIM_PARAS,**kwargs):
        self.fn,self.txt=to_fn_txt(txt_or_fn)
        self._kwargs=kwargs
        self._lim_paras=lim_paras
        self._shuffle_paras=shuffle_paras
        self._docs={}

        # paras
        self._paras=dict(
            (para_d['para_i'],para_d)
            for para_d in tokenize_paras_ld(self.txt, **kwargs)
        )
        self.__paras_i=set(self._paras.keys())
        self._paras_i=sorted(list(self.__paras_i))
        self._paras_i=self.paras_i(shuffle_paras=shuffle_paras,lim_paras=lim_paras,progress=False,**kwargs)
        
    
    def get(self,para_i,sent_i):
        obj=self.para(para_i)
        if sent_i: obj=obj.sent(sent_i)
        return obj
        
    
    def paras_i(self,
            para_i=[],
            shuffle_paras=False,
            reset_paras=False,
            lim_paras=None,
            progress=True,
            desc='Iterating over paragraphs',
            **kwargs):
        
        if para_i:
            para_i_l=[para_i] if type(para_i)==int else list(para_i)
        else:
            para_i_l=self._paras_i
        if reset_paras: para_i_l=sorted(list(self.__paras_i))
        if shuffle_paras: random.shuffle(para_i_l)
        if lim_paras: para_i_l=para_i_l[:lim_paras]
        if progress: para_i_l=tqdm(para_i_l,desc=desc)
        return para_i_l
    
    def paras_d(self,*args,**kwargs):
        return [self._paras[para_i] for para_i in self.paras_i(*args,**kwargs)]    
    
    def paras_df(self,*args,**kwargs):
        return pd.DataFrame(self.paras_d(*args,**kwargs)).set_index('para_i')
    
    def iter_paras(self,*args,**kwargs):
        for para_i in self.paras_i(*args,**kwargs):
            yield self.para(para_i,**kwargs)
    
    def para(self,para_i=1,**kwargs):
        if not para_i in self._docs:
            txt=self._paras[para_i]['para_str']
            self._docs[para_i]=Para(txt, para_i=para_i, **kwargs)
        return self._docs[para_i]
    
    def paras(self,*args,**kwargs):
        return list(self.iter_paras(*args,**kwargs))
    
    #############################################
    ### Data
    #############################################

    def iter_data(self,index=True,**kwargs):
        for para_i in self.paras_i(**kwargs):
            yield self.get_data(para_i,index=index,**kwargs)
    def get_data(self,para_i,index=True,**kwargs):
        odf=self.para(para_i).data(index=False,**kwargs).assign(para_i=para_i)
        return setindex(odf) if index else odf
    def data(self,para_i=None,**kwargs):
        if type(para_i)==int: return self.get_data(para_i,**kwargs)
        o=list(self.iter_data(**kwargs))
        return pd.concat(o) if len(o) else pd.DataFrame()
    


class ParaModel(object):
    def __init__(self,txt,path_db=PATH_DB,**kwargs):
        self.txt=txt
        self._id=hashstr(txt)
        self._sents_str=tokenize_sents_txt(txt)
        self._words=None
        self._sylls=None
        self._doc=None
        self._syntax=None
        self._mtrees=None
        self._mtrees_obj=None
        self._path_db=path_db
        self._sents=None

    def __repr__(self):
        istr=f' #{self.i}' if self.i else ''
        return f'<Paragraph{istr}: “{self.fsent_str}...” ({self.num_sents} sents, {self.num_words} words)>'.replace('\n',' ')

    ####################################
    ## WORDS
    ####################################

    def words(self,index=True,**kwargs):
        if self._words is None:
            iterr=tokenize_sentwords_iter(self.txt,sents=self._sents_str,**kwargs)
            self._words=pd.DataFrame(iterr)
        return setindex(self._words) if index else self._words

    @property
    def num_words(self): return len(self.words(index=False))
    
    ####################################
    ## SENTS
    ####################################

    # def sent(self,sent_i):

    def sents(self,**kwargs):
        if self._sents is None:
            self._sents=[]
            doc = self.doc(**kwargs)
            sentobjs = list(doc.sentences) if doc is not None else []
            for si,sent_str in enumerate(self._sents_str):
                sent_i=si+1
                nlp_sent_obj = sentobjs[si] if si<len(sentobjs) else None
                sentobj = Sent(sent_str, i=sent_i, nlp_sent_obj=nlp_sent_obj, **kwargs)
                self._sents.append(sentobj)
        return self._sents
    
    def sent(self,sent_i,**kwargs):
        sents=self.sents(**kwargs)
        si=sent_i-1
        return sents[si] if si<len(sents) else None
    
    @property
    def num_sents(self): return len(self._sents_str)
    @property
    def fsent_str(self): return self._sents_str[0]
    @property
    def lsent_str(self): return self._sents_str[-1] if self.num_sents>1 else ''

    ####################################
    ## SYLLABIFY
    ####################################

    def syllabify(self,df,index=False,**kwargs):
        odf=syllabify_df(df=df,**kwargs)
        return setindex(odf) if index else odf

    def sylls(self,df=None,index=True,**kwargs):
        if df is None: df=self.words(index=False)
        return self.syllabify(df,index=index,**kwargs)

    ####################################
    ## NLP DOCS
    ####################################

    def doc(self,**kwargs):
        if self._doc is None:
            sentwords_ll=tokenize_sentwords_ll_from_df(self.words(index=False))
            self._doc=get_nlp_doc(sentwords_ll,**kwargs)
        return self._doc

    ####################################
    ## NLP FEATS
    ####################################

    def syntax(self,index=True,**kwargs):
        if self._syntax is None:
            doc=self.doc()
            self._syntax=get_nlp_feats_df(doc, **kwargs)
        return setindex(self._syntax) if index else self._syntax

    ####################################
    ## Mtrees
    ####################################

    def mtrees(self,index=True,**kwargs):
        if self._mtrees is None:
            o=[
                sent.mtree_df(**kwargs).assign(sent_i=sent.i)
                for sent in self.sents(**kwargs)
            ]
            self._mtrees=pd.concat(o) if len(o) else pd.DataFrame()
        return setindex(self._mtrees) if index else self._mtrees

    ####################################
    ## Combined
    ####################################

    def data(self,
            syntax=True,
            sylls=True,
            mtree=True,
            index=True,
            save=True,
            **kwargs):

        odf = self.words(index=False,**kwargs)
        if syntax: odf=safe_merge(odf,self.syntax(index=False,**kwargs))
        if mtree: odf=safe_merge(odf,self.mtrees(index=False,**kwargs))
        if sylls: odf=self.syllabify(df=odf,**kwargs)
        if save: self.save()
        return setindex(odf) if index else odf


    ####################################
    ## Save
    ####################################

    def save(self,path_db=None):
        if path_db is None: path_db=self._path_db
        with dc.Cache(path_db) as db:
            #print(f'Saving {self._id}')
            db[self._id] = to_blosc(pickle.dumps(self))




class SentModel(object):
    def __init__(self,txt,i=None,nlp_sent_obj=None):
        self.txt=txt
        self.i=i
        self.nlp=nlp_sent_obj
        self._mtree=None
        self._mtree_df=None
    
    def mtree(self,**kwargs):
        if self._mtree is None:
            self._mtree=get_mtree(self.nlp,**kwargs)
        return self._mtree
    
    def mtree_df(self,**kwargs):
        if self._mtree_df is None:
            mtree=self.mtree(**kwargs)
            self._mtree_df=mtree.get_stats(**kwargs) if mtree is not None else pd.DataFrame()
        return self._mtree_df#.assign(sent_i=self.i)
    