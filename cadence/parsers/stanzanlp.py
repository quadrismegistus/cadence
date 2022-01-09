from ..imports import *
from .mtree import recurse_tree

NLPD={}
badcols={'feats','id','text'}
# badcols={'feats','start_char','end_char','id','text'}

def get_nlp(
        lang=DEFAULT_LANG,
        
        pretokenized=True,
        postag=NLP_PARSE_POSTAG,
        tokenize=NLP_PARSE_TOKENIZE,
        constituency=NLP_PARSE_CONSTITUENCY,
        depparse=NLP_PARSE_DEPPARSE,

        processors=[],
        verbose=False,
        **kwargs
        ):
    global NLPD

    if not processors:
        processors=get_processors(constituency=constituency,depparse=depparse,postag=postag)
    
    procstr=','.join(processors)
    
    kwargs=dict(
        lang=lang,
        tokenize_pretokenized=pretokenized,
        processors=procstr,
    )

    key=kwargs_key(kwargs)

    if not key in NLPD:
        eprint('\nLoading NLP model:',kwargs)
        
        import stanza
        kwargs2={**dict(verbose=verbose), **kwargs}
        NLPD[key] = stanza.Pipeline(**kwargs2)
        NLPD[key].procstr=procstr
        # NLPD[key].processors=processors
    return NLPD[key]




def get_processors(
        tokenize=True,
        postag=True,
        constituency=True,
        depparse=True,
        **kwargs):
    #o=dict(DEFAULT_PROCESSORS)
    o={}
    if tokenize:
        o['tokenize']=''
    if postag:
        o['tokenize']=''
        o['pos']=''
        o['lemma']=''
    if constituency:
        o['tokenize']=''
        o['pos']=''
        o['constituency']=''
    if depparse:
        o['tokenize']=''
        o['pos']=''
        o['lemma']=''
        o['depparse']=''
    return sorted(list(o.keys()))



def tokenize_sents_txt(txt,**y): return nltk.sent_tokenize(txt)
def tokenize_words_txt(txt,**y): return tokenize_nice2(txt)
def to_token(toktxt,**y):
    return split_punct(toktxt.lower())[1]
def get_syllable_ld(word_str,lang=DEFAULT_LANG,**kwargs):
    func=CODE2LANG_SYLLABIFY[lang]
    o_ld=func(word_str,**kwargs)
    return o_ld

def getcache_df(self, name, iter_func, index=True, cache=True,**kwargs):
    d=getattr(self,name)
    key=kwargs_key(kwargs)
    if not cache or not key in d:
        d[key]=pd.DataFrame(iter_func(**kwargs))
    odf=d[key]
    try:
        if len(odf) and index: odf=setindex(odf)
    except ValueError:
        pass
    return odf


def tokenize_sentwords_iter(
        txt,
        lang=DEFAULT_LANG,
        sep_line=SEP_LINE,
        sep_para=SEP_STANZA,
        seps_phrase=SEPS_PHRASE,
        progress=True,
        para_i=None,
        **kwargs):
    char_i=0
    line_i=1
    linepart_i=1
    linepart_ii=0
    start_offset=0
    sents=tokenize_sents_txt(txt)
    for sent_i, sent in enumerate(sents):
        tokens=tokenize_words_txt(sent)
        for tok_i,realtok in enumerate(tokens):
            prefstr,wordstr,sufstr=split_punct(realtok)
            tokstr=wordstr+sufstr
            if sep_line in prefstr and realtok.strip(): line_i+=1
            odx_word=dict(
                para_i=para_i,
                sent_i=sent_i+1,
                sentpart_i=linepart_i,
                line_i=line_i,
                word_i=tok_i+1,
                word_pref=prefstr,
                word_str=tokstr,
                word_tok=wordstr.lower(),
            )
            yield odx_word
            if set(realtok)&set(seps_phrase): linepart_i+=1



def tokenize_paras_ld(txt,sep_para=SEP_PARA, **kwargs):
    txt=clean_text(txt)
    paras_txt=txt.split(sep_para)
    num_paras=len(paras_txt)
    ld=[]
    offset=0
    para_i=0
    for pi,para_txt in enumerate(paras_txt):
        if pi: para_txt=sep_para+para_txt
        para_txt_len=len(para_txt)
        para_str=para_txt.strip()
        para_str_len=len(para_str)
        para_str_noleft=para_txt.lstrip()
        para_str_noright=para_txt.rstrip()
        diff_left=para_txt_len - len(para_str_noleft)
        diff_right=para_txt_len - len(para_str_noright)
        
        offset1=offset+diff_left
        offset2=offset+para_txt_len-diff_right

        if para_str:
            assert para_str == txt[offset1:offset2]
            para_i+=1
            dx={
                'para_i':para_i,
                'para_str':para_str,
                'para_start_char':offset1,
                'para_end_char':offset2,
                # 'para_txt':para_txt,
            }
            ld.append(dx)
        offset+=para_txt_len
    return ld


########
# Tokenize NLP
########


### NLP FUNCS
def get_nlp_doc(doc_ll_or_txt,nlp=None,**kwargs):
    if nlp is None: nlp=get_nlp(**kwargs)
    try:
        return nlp(doc_ll_or_txt)
    except Exception as e:
        eprint(f'!! NLP Parser error: {e}')

def get_nlp_doc_wordfeat_df(doc,**kwargs):
    if doc is None: return pd.DataFrame()
    ld=[]
    sents=doc.sentences
    sentd_orig=None
    for sent_i, sent in enumerate(sents):
        ## Get Word Info
        for word_i,word in enumerate(sent.tokens):
            feats=word.to_dict()[0]
            statd=dict((f'word_{k}',v) for k,v in feats.items() if k not in badcols)
            for feat in feats.get('feats','').split('|'):
                if not feat: continue
                fk,fv=feat.split('=',1)
                statd[f'word_{fk.lower()}']=fv
            dx={
                'sent_i': sent_i+1,
                'word_i': word_i+1,
                'word_str':word.text,
                **statd
            }
            ld.append(dx)
    return pd.DataFrame(ld).fillna('')

def get_nlp_doc_constituency_df(doc,**kwargs):
    if doc is None: return pd.DataFrame()
    ## Constituency?
    ld=[]
    sents=doc.sentences
    sentd_orig=None
    for sent_i, sent in enumerate(sents):
        if hasattr(sent,'constituency'):
            if sentd_orig is None:
                sentd_orig=dict((get_sent_id_tokens(sent), sent) for sent in sents)
            sent_id_constituency=get_sent_id_constituency(sent)
            if sent_id_constituency not in sentd_orig: continue
            sent_orig=sentd_orig[sent_id_constituency]        
            
            senttree=recurse_tree(sent.constituency, node_i=0, path=[])
            for word_i,word_constituency_path in enumerate(senttree):
                word_constituency_path_str='('.join(word_constituency_path)
                constituency_depth=len(word_constituency_path)
                dx={
                    'sent_i': sent_i+1,
                    'word_i': word_i+1,
                    'word_depth':constituency_depth,
                    'word_constituency':word_constituency_path_str,
                }
                ld.append(dx)
    return pd.DataFrame(ld).fillna('')

def get_nlp_feats_df(doc,**kwargs):
    df_feats=get_nlp_doc_wordfeat_df(doc,**kwargs)
    df_const=get_nlp_doc_constituency_df(doc,**kwargs)
    odf=df_feats.merge(df_const,on=['sent_i','word_i'],how='inner')
    return odf

def tokenize_sentwords_ll(words_ld,**kwargs):
    if not len(words_ld): return []
    listd=defaultdict(list)
    for word_d in words_ld:
        listd[word_d['sent_i']].append(word_d['word_str'])
    olist=[sentl for sent_i,sentl in sorted(listd.items())]
    return olist



def get_sent_id_tokens(sent,hash=True):
    o=[tok.text for tok in sent.tokens]
    return tuple(o)
def get_sent_id_constituency(sent,hash=True):
    o=[tok.split()[-1] for tok in str(sent.constituency).split(')') if tok]
    o=[x.replace('(-RRB-',')') for x in o]
    return tuple(o)





# def tokenize_sents_txt(txt): return nltk.sent_tokenize(txt)
# def tokenize_words_txt(txt): return tokenize_nice2(txt)

# def tokenize_nlp_txt(
#         txt,
#         nlp=None,
#         sentwords=None,
#         pretokenized=True,
#         lang=DEFAULT_LANG,
#         processors=['tokenize'],
#         **kwargs):
#     #print(nlp,processors)
#     if nlp is None:
#         nlp=get_nlp(
#             lang=lang,
#             processors=processors,
#             tokenize_pretokenized=pretokenized
#         )
    
#     if pretokenized:
#         return nlp(sentwords)
#     else:
#         return nlp(txt)

# def clean_text(txt):
#     return txt.replace('\r\n','\n').replace('\r','\n')


# def tokenize_paras_df(txt,**kwargs):
#     return pd.DataFrame(tokenize_paras_ld(txt,**kwargs))


# def do_tokenize_paras_nlp_iter(row,pretokenized=True,**kwargs):
#     txt=row['para_str']
#     tokdf=row['para_tokdf']=tokenize_sentwords(txt,**kwargs)
#     sentwords=tokenize_sentwords_ll(tokdf)
#     doc=tokenize_nlp_txt(
#         txt,
#         sentwords=sentwords,
#         pretokenized=True,
#         **kwargs
#     )
#     row['para_doc']=doc
#     return row

# def tokenize_paras_nlp_iter(
#         txt,
#         ld_paras=None,
#         progress=True,
#         num_proc=1,
#         shuffle_paras=False,
#         lim_paras=None,

#         lang=DEFAULT_LANG,
#         processors=DEFAULT_PROCESSORS,
#         pretokenized=True,
#         **kwargs):

#     #from stanza_batch import batch    
    
#     if ld_paras is None: ld_paras=tokenize_paras_ld(txt,**kwargs)
#     if shuffle_paras: random.shuffle(ld_paras)
#     if lim_paras: ld_paras=ld_paras[:lim_paras]

#     nlp=get_nlp(lang=lang,processors=processors,tokenize_pretokenized=pretokenized)
#     kwargs['nlp']=nlp
#     kwargs['lang']=lang
#     kwargs['processors']=processors
#     # kwargs['pretokenized']=pretokenized

#     iterr=pmap_iter(
#         do_tokenize_paras_nlp_iter,
#         ld_paras,
#         num_proc=num_proc,
#         desc='Scanning paragraphs',
#         kwargs=kwargs
#     )
#     yield from iterr


# def tokenize_sentwords_iter(
#         txt,
#         doc=None,
#         lang=DEFAULT_LANG,
#         engine='',
#         sep_line=SEP_LINE,
#         sep_para=SEP_STANZA,
#         seps_phrase=SEPS_PHRASE,
#         processors=DEFAULT_PROCESSORS,
#         progress=True,
#         para_i=None,
#         **kwargs):
#     char_i=0
#     line_i=1
#     linepart_i=1
#     linepart_ii=0

#     #if not doc:
#     #    doc=tokenize_nlp_txt(txt,processors=processors,lang=lang,**kwargs)
    
#     #sents=doc.sentences
#     # start_offset=sents[0].tokens[0].start_char
#     start_offset=0

#     sents=tokenize_sents_txt(txt)

#     for sent_i, sent in enumerate(sents):
#         tokens=tokenize_words_txt(sent)
#         for tok_i,tok in enumerate(tokens):
#             #prefstr=txt[char_i-start_offset : tok.start_char - start_offset]
#             # realtok=tok.text
#             realtok=tok
#             prefstr,wordstr,sufstr=split_punct(realtok)
#             tokstr=wordstr+sufstr
#             #tokstr=txt[tok.start_char - start_offset : tok.end_char - start_offset]
#             #realtok=txt[char_i-start_offset:tok.end_char-start_offset]
#             #print([prefstr,tokstr])
#             if sep_line in prefstr and realtok.strip(): line_i+=1
#             # char_i=tok.end_char
#             #featd=tok.to_dict()[0]
#             #print()
#             odx_para=dict(para_i=para_i) if para_i is None else {}
#             #odx_feat=dict(('word_'+k,v) for k,v in featd.items() if k not in badcols)
#             odx_word=dict(
#                 para_i=para_i,
#                 sent_i=sent_i+1,
#                 sentpart_i=linepart_i,
#                 line_i=line_i,
#                 word_i=tok_i+1,
#                 word_pref=prefstr,
#                 word_str=tokstr,
#                 # word_str=wordstr,
#                 # word_suf=sufstr,
#                 # word_str=realtok,
#                 word_tok=wordstr.lower(),
#                 # word_str1=tok.text,
#                 # word_str2=tokstr,
#                 # word_tok3=realtok,
#             )

#             # assert tok.text==tokstr
            
#             # odx=dict(**odx_para, **odx_word, **odx_feat)
#             #print(odx)
#             yield odx_word
            
#             # if change_linepart:
#                 # linepart_i+=1
#                 # change_linepart=False
#             if set(realtok)&set(seps_phrase):
#                 linepart_i+=1
#                 # change_linepart=True

# def tokenize_sentwords(txt,doc=None,**kwargs):
#     iterr=tokenize_sentwords_iter(txt,doc=doc,**kwargs)
#     tokdf=pd.DataFrame(iterr)
#     return tokdf

# def tokenize_sentwords_ll(tokdf,**kwargs):
#     if not len(tokdf): return []
#     return [list(sdf.word_str) for si,sdf in sorted(tokdf.groupby('sent_i'))]

# def tokenize_nlp_iter(
#         txt,
#         constituency=True,
#         depparse=True,
#         syllabify=True,
#         num_proc=1,
#         **kwargs):
#     # make proc list
    
#     processors=get_processors(constituency=constituency,depparse=depparse,**kwargs)

#     iterr=tokenize_paras_nlp_iter(txt,processors=processors,num_proc=num_proc,**kwargs)
    
#     for para_row in iterr:
#         para_str,para_doc=para_row['para_str'], para_row['para_doc']
        
#         # tokenize
#         tokdf=tokenize_sentwords(para_str,doc=para_doc,**kwargs)
        
#         # add anno?
#         if constituency: tokdf=tokenize_constituency(tokdf,para_doc,**kwargs)
#         if depparse: tokdf=tokenize_deps(tokdf,para_doc,**kwargs)
#         if syllabify: tokdf=syllabify_df(tokdf,**kwargs)

#         for k in ['para_i']: tokdf[k]=para_row[k]
        
#         # done
#         odf=setindex(tokdf)
#         odf.attrs=dict(para_row)
#         yield odf







# def tokenize_constituency(tokdf,doc,**kwargs):
#     sents=doc.sentences
#     ld=[]
#     sentd_orig=dict((get_sent_id_tokens(sent), sent) for sent in sents)
#     for sent_i, sent in enumerate(sents):
#         # print('????',sent_i)
#         # print(sent.constituency)
#         # sent_id_tokens=get_sent_id_tokens(sent)
#         try:
#             sent_id_constituency=get_sent_id_constituency(sent)
#             sent_orig=sentd_orig[sent_id_constituency]        
#         except (KeyError,AttributeError) as e:
#             # print('!! Cannot find sentence id',e)
#             continue

#         senttree=recurse_tree(sent.constituency, node_i=0, path=[])
#         for word_i,word_constituency_path in enumerate(senttree):
#             word_constituency_path_str='('.join(word_constituency_path)
#             constituency_depth=len(word_constituency_path)
#             dx={
#                 'sent_i': sent_orig.id+1,
#                 'word_i': word_i+1,
#                 'word_depth':constituency_depth,
#                 'word_constituency':word_constituency_path_str,
#             }
#             ld.append(dx)
#         # stop
#     df=pd.DataFrame(ld)
#     if not len(df): return tokdf
#     return tokdf.merge(df,on=['sent_i','word_i'],how='left')

# def tokenize_deps(tokdf,doc,cols_done=set(),lang=DEFAULT_LANG,**kwargs):
#     sents=doc.sentences
#     ld=[]
#     cols_done=set(tokdf.columns)
#     for sent_i, sent in enumerate(sents):
#         for word_i,word in enumerate(sent.tokens):
#             feats=word.to_dict()[0]
#             statd=dict((f'word_{k}',v) for k,v in feats.items() if k not in badcols)
#             for feat in feats.get('feats','').split('|'):
#                 if not feat: continue
#                 fk,fv=feat.split('=',1)
#                 statd[fk]=fv
            
#             dx={
#                 'sent_i': sent.id+1,
#                 'word_i': word_i+1,
#                 **statd
#             }
#             ld.append(dx)
#     df=pd.DataFrame(ld).fillna('')
#     joiner=['sent_i','word_i']
#     ocols=(set(df.columns)-set(tokdf.columns))|set(joiner)
#     return tokdf.merge(df[ocols],on=joiner,how='left')



# ########
# # Scanning
# ########

# def scan_iter_stanzanlp(txt,**kwargs):
#     iterr=tokenize_nlp_iter(txt,**kwargs)
#     yield from iterr


# def scan_iter(txt,**kwargs): return scan_iter_stanzanlp(txt,**kwargs)