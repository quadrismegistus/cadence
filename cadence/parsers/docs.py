from ..imports import *
from .txtparsing import *
from .mtree import *
from .stanzanlp import *
from .metrics import *


def Text(*args,**kwargs):
    return TextModel(*args,**kwargs)

def Prose(*args,**kwargs):
    kwargs={**kwargs, **dict(linebreaks=False, phrasebreaks=True)}
    return Text(*args,**kwargs)
def Verse(*args,**kwargs):
    kwargs={**kwargs, **dict(linebreaks=True, phrasebreaks=False)}
    return Text(*args,**kwargs)
def ProseVerse(*args,**kwargs):
    kwargs={**kwargs, **dict(linebreaks=True, phrasebreaks=True)}
    return Text(*args,**kwargs)

def Para(txt, *args, path_db=PATH_DB, force=False, para_i=None, **kwargs):
    txt=txt.strip()
    _id=get_para_key(txt, kwargs)
    #print('Para Key =',_id)
    if not force:
        with dc.Cache(path_db) as db:
            if _id in db:
                # eprint(f'[cadence] Found paragraph cached in db, loading...')
                pdoc=pickle.loads(from_blosc(db[_id]))
                pdoc.i=para_i
                return pdoc

    pdoc=ParaModel(txt,*args,path_db=path_db,**kwargs)
    pdoc.i=para_i
    return pdoc

def Sent(txt, nlp_sent_obj=None, **kwargs):
    return SentModel(txt, nlp_sent_obj=nlp_sent_obj, **kwargs)


def get_para_key(txt, kwargs):
    return (hashstr(txt), kwargs_key(kwargs))

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
            for para_d in tokenize_paras_ld(self.txt, **self.kwargs(kwargs))
        )
        self.__paras_i=set(self._paras.keys())
        self._paras_i=sorted(list(self.__paras_i))
        self._paras_i=self.paras_i(shuffle_paras=shuffle_paras,lim_paras=lim_paras,progress=False,**self.kwargs(kwargs))
        self._num_paras=len(self._paras)

    def __repr__(self):
        return f'<Text: “{self.para(1).fsent_str}...” ({self.num_paras} paras)>'
    
    def kwargs(self,kwargs):
        return {**self._kwargs, **kwargs}

    def get(self,para_i,sent_i):
        obj=self.para(para_i)
        if sent_i: obj=obj.sent(sent_i)
        return obj
        

    """
    PARA MANAGEMENT
    """

    @property
    def num_paras(self): return len(self._paras)
    
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
        if progress and len(para_i_l)>1: para_i_l=tqdm(para_i_l,desc=desc)
        return para_i_l
    
    def paras_d(self,*args,**kwargs):
        return [self._paras[para_i] for para_i in self.paras_i(*args,**self.kwargs(kwargs))]    
    
    def paras_df(self,*args,**kwargs):
        return pd.DataFrame(self.paras_d(*args,**self.kwargs(kwargs))).set_index('para_i')
    
    def iter_paras(self,*args,**kwargs):
        for para_i in self.paras_i(*args,**self.kwargs(kwargs)):
            yield self.para(para_i,**self.kwargs(kwargs))
    
    def para(self,para_i=1,**kwargs):
        if not para_i in self._docs:
            if not para_i in self._paras: return
            txt=self._paras[para_i]['para_str']
            #print('Making new paragraph',para_i,self.kwargs(kwargs),'...')
            self._docs[para_i]=Para(txt, para_i=para_i, **self.kwargs(kwargs))
        return self._docs[para_i]
    def paras(self,*args,**kwargs):
        return list(self.iter_paras(*args,**self.kwargs(kwargs)))

    @property
    def num_stanzas(self): return self.num_paras
    def stanzas_i(self,**kwargs): return self.paras_i(**kwargs)
    def stanzas_d(self,**kwargs): return self.paras_d(**kwargs)
    def stanzas_df(self,**kwargs): return self.paras_df(**kwargs)
    def iter_stanzas(self,**kwargs): return self.iter_paras(**kwargs)
    def stanza(self,**kwargs): return self.para(**kwargs)
    def stanzas(self,**kwargs): return self.paras(**kwargs)
    
    #############################################
    ### Data
    #############################################

    def iter_data(self,data_type='data',index=True,**kwargs):
        for para_i in self.paras_i(**kwargs):
            yield self.get_data(para_i,data_type=data_type,index=index,**self.kwargs(kwargs))
    def get_data(self,para_i,data_type='data',index=True,**kwargs):
        paras=[self.para(para_i,**kwargs)] if para_i else self.paras(**kwargs)
        o=[]
        for para in paras:
            if para is None: continue
            if hasattr(para,data_type):
                func=getattr(para,data_type)
                odf=func(index=index,**self.kwargs(kwargs))
                odf['para_i']=para.i
                o.append(odf)
        return concatt(o,index=index)

    #############################################
    ### Data types
    #############################################
    def words(self,para_i=None,**kwargs): return self.get_data(para_i,'words',**kwargs)
    @property
    def num_words(self): return sum(para.num_words for para in self.paras())
    
    def sents(self,para_i=None,**kwargs):
        sents=[sent for para in self.paras(para_i,**kwargs) for sent in para.sents(**kwargs)]
        return sents
    def sent(self,sent_i,para_i=None,**kwargs):
        if type(sent_i)==int:
            sents=self.sents(para_i,**kwargs)
            sent_i-=1
            if sent_i<len(sents): return sents[sent_i]
        elif type(sent_i) in {tuple,list}:
            para_i,sent_i=sent_i
            para=self.para(para_i,**kwargs)
            if para is not None:
                return para.sent(sent_i,**kwargs)
    @property
    def num_sents(self): return sum(para.num_sents for para in self.paras())
    @property
    def fsent_str(self): return self.para(1).fsent_str
    @property
    def lsent_str(self): return self.para(1).lsent_str

    def sylls(self,para_i=None,**kwargs): return self.get_data(para_i,'sylls',**kwargs)
    def syntax(self,para_i=None,**kwargs): return self.get_data(para_i,'syntax',**kwargs)
    def mtrees(self,para_i=None,**kwargs): return self.get_data(para_i,'mtrees',**kwargs)
    def data(self,para_i=None,**kwargs): return self.get_data(para_i,'data',**kwargs)
    def parse(self,para_i=None,**kwargs): return self.get_data(para_i,'parse',**kwargs)
    def parses(self,para_i=None,**kwargs): return self.get_data(para_i,'parses',**kwargs)
    def parse_iter(self,**kwargs):
        for para in self.paras(**kwargs):
            yield from para.parse_iter(**kwargs)



class ParaModel(TextModel):
    def __init__(self,txt,path_db=PATH_DB,i=None,**kwargs):
        self.txt=txt
        self._parses={}
        self._id=get_para_key(txt, kwargs)
        self._sents_str=tokenize_sents_txt(txt)
        self._words=None
        self._sylls=None
        self._doc=None
        self._syntax=None
        self._mtrees=None
        self._mtrees_obj=None
        self._path_db=path_db
        self._sents=None
        self._kwargs=kwargs
        self.i=i

    def __repr__(self):
        istr=f' #{self.i}' if self.i else ''
        return f'<Paragraph/Stanza{istr}: “{self.fsent_str}...” ({self.num_sents} sents, {self.num_words} words)>'.replace('\n',' ')

    

    ####################################
    ## WORDS
    ####################################

    def words(self,index=True,**kwargs):
        if self._words is None:
            iterr=tokenize_sentwords_iter(self.txt,sents=self._sents_str,**self.kwargs(kwargs))
            self._words=pd.DataFrame(iterr)
        return setindex(self._words) if index else resetindex(self._words)

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
                sentobj = Sent(sent_str, i=sent_i, nlp_sent_obj=nlp_sent_obj, **self.kwargs(kwargs))
                self._sents.append(sentobj)
        return self._sents
    
    def sent(self,sent_i,**kwargs):
        sents=self.sents(**self.kwargs(kwargs))
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
        kwargs=self.kwargs(kwargs)
        odf=syllabify_df(df=df,**kwargs)
        return setindex(odf) if index else resetindex(odf)

    def sylls(self,df=None,index=True,**kwargs):
        if df is None: df=self.words(index=False)
        return self.syllabify(df,index=index,**self.kwargs(kwargs))

    ####################################
    ## NLP DOCS
    ####################################

    def doc(self,**kwargs):
        if self._doc is None:
            sentwords_ll=tokenize_sentwords_ll_from_df(self.words(index=False))
            self._doc=get_nlp_doc(sentwords_ll,**self.kwargs(kwargs))
        return self._doc

    ####################################
    ## NLP FEATS
    ####################################

    def syntax(self,index=True,**kwargs):
        if self._syntax is None:
            doc=self.doc()
            self._syntax=get_nlp_feats_df(doc, **self.kwargs(kwargs))
        return setindex(self._syntax) if index else resetindex(self._syntax)

    ####################################
    ## Mtrees
    ####################################

    def mtrees(self,index=True,**kwargs):
        if self._mtrees is None:
            o=[
                sent.mtree_df(**self.kwargs(kwargs)).assign(sent_i=sent.i)
                for sent in self.sents(**self.kwargs(kwargs))
            ]
            self._mtrees=pd.concat(o) if len(o) else pd.DataFrame()
        return setindex(self._mtrees) if index else resetindex(self._mtrees)

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

        odf = self.words(index=False,**self.kwargs(kwargs))
        if syntax: odf=safe_merge(odf,self.syntax(index=False,**self.kwargs(kwargs)))
        if mtree: odf=safe_merge(odf,self.mtrees(index=False,**self.kwargs(kwargs)))
        if sylls: odf=self.syllabify(df=odf,**self.kwargs(kwargs))
        if save: self.save()
        return setindex(odf) if index else resetindex(odf)


    ####################################
    ## Save
    ####################################

    def save(self,path_db=None):
        if path_db is None: path_db=self._path_db
        with dc.Cache(path_db) as db:
            #print(f'Saving {self._id}')
            db[self._id] = to_blosc(pickle.dumps(self))



    ####################################
    ## Units
    ####################################

    def iter_units(self,**kwargs):
        dfdata = self.data(index=False, sylls=True, **self.kwargs(kwargs))
        try:
            divide_parse_units(dfdata,**self.kwargs(kwargs))
            yield from (g for i,g in dfdata.groupby('unit_i'))
        except KeyError:
            yield pd.DataFrame()
    
    def units(self,index=True,**kwargs):
        o=list(self.iter_units(**self.kwargs(kwargs)))
        odf=pd.concat(o) if len(o) else pd.DataFrame()
        return setindex(odf) if index and len(odf) else resetindex(odf)

    ####################################
    ## Combos
    ####################################

    def iter_combos(self,**kwargs):
        for dfunit in self.iter_units(**self.kwargs(kwargs)):
            for dfcombo in iter_combos(dfunit,**self.kwargs(kwargs)):
                yield dfcombo

    ####################################
    ## Units
    ####################################
        
    def get_parse_key(self,kwargs,good_keys={'constraints'}):
        kwargs=dict((k,v) for k,v in kwargs.items() if k in good_keys)
        if not 'constraints' in kwargs or not kwargs['constraints']:
            kwargs['constraints']=DEFAULT_CONSTRAINTS
        else:
            kwargs['constraints']=[
                func if type(func)==str else func.__name__
                for func in kwargs['constraints']
            ]
        kwargs['constraints']=sorted(list(kwargs['constraints']))
        return kwargs_key(kwargs)


    def parse_iter(self,index=True,force=False,num_proc=None,incl_data=True,by_line=False,verbose=True,progress=True,**kwargs):
        if num_proc is None: num_proc = mp.cpu_count()//2
        key=self.get_parse_key(kwargs)
        if force or not key in self._parses:
            units=list(self.iter_units(**self.kwargs(kwargs)))
            oiterr=pmap_iter(
                parse_unit_combos,
                units,
                num_proc=num_proc,
                desc='Metrically parsing line units',
                kwargs=self.kwargs(kwargs),
                progress=progress if not verbose else False
            )
        else:
            oiterr=(g for i,g in sorted(self._parses[key].groupby('unit_i')))
        o=[]
        for odf in oiterr:
            if not len(odf): continue
            if verbose: printm(parse_markdown(odf))
            o.append(odf)
            if by_line: odf=to_lines(odf,**kwargs)
            odf=setindex(odf) if index else resetindex(odf)
            yield odf
        self._parses[key]=concatt(o)
    
    def parse(self,index=True,incl_data=True,force=False,by_line=False,verbose=True,**kwargs):
        key=self.get_parse_key(kwargs)
        parsed=False
        if force or not key in self._parses:
            o=[]
            kwargs=self.kwargs(kwargs)
            if 'by_line' in kwargs: del kwargs['by_line']
            kwargs['verbose']=verbose
            oiterr=self.parse_iter(force=force,by_line=False,**kwargs)
            list(oiterr)
            if not key in self._parses: return pd.DataFrame()
            parsed=True
        
        odf=self._parses[key]
        if not len(odf): return pd.DataFrame()

        if verbose and not parsed:
            for i,g in odf.groupby('unit_i'):
                printm(parse_markdown(g))

        if incl_data:
            data=self.data(**self.kwargs(kwargs))
            odf=safe_merge(odf, data, on=['sent_i','word_i','word_ipa_i','syll_i'],how='left')
        odf=setindex(odf) if index else resetindex(odf)
        if by_line: odf=to_lines(odf,**kwargs)
        return odf
        
    def parses(self,**kwargs): return self.parse(**kwargs)



class SentModel(ParaModel):
    def __init__(self,txt,i=None,nlp_sent_obj=None,**kwargs):
        self.txt=txt
        self.i=i
        self.nlp=nlp_sent_obj
        self._mtree=None
        self._mtree_df=None
        self._kwargs=kwargs

    def __repr__(self):
        txt=self.txt.replace("\n"," ")
        return f'<Sentence #{self.i}: {txt}>'
    
    def mtree(self,**kwargs):
        if self._mtree is None:
            self._mtree=get_mtree(self.nlp,**self.kwargs(kwargs))
        return self._mtree
    
    def mtree_df(self,**kwargs):
        if self._mtree_df is None:
            mtree=self.mtree(**self.kwargs(kwargs))
            self._mtree_df=mtree.get_stats(**self.kwargs(kwargs)) if mtree is not None else pd.DataFrame()
        return self._mtree_df#.assign(sent_i=self.i)
    
    def grid(self,**kwargs):
        import plotnine as p9
        p9.options.figure_size=(11,5)
        figdf=resetindex(self.mtree_df(**kwargs))
        figdf['prom_tstress']+=0.1
        figdf['prom_tstress']=figdf['prom_tstress'].fillna(0)
        return p9.ggplot(
            figdf,
            p9.aes(x='word_i',y='prom_tstress',label='word_str')
        ) + p9.geom_col(alpha=.25) + p9.geom_text(size=9,angle=45) + p9.theme_void()