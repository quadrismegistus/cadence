from ..imports import *
from .mtree import recurse_tree

NLPD={}
# badcols={'feats','id','text'}
badcols={'feats','start_char','end_char','id','text','misc','lemma'}

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
        processors=get_processors(
            constituency=constituency,
            depparse=depparse,
            postag=postag
        )
    
    procstr=','.join(processors)
    
    kwargs=dict(
        lang=lang,
        tokenize_pretokenized=pretokenized,
        processors=procstr,
    )

    key=kwargs_key(kwargs)

    if not key in NLPD:
        # eprint('Loading NLP model:',kwargs)
        
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
# def to_token(toktxt,**y):
#     #return split_punct(toktxt.lower())[1]
#     return zero_punc(toktxt).lower()




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
            prefstr,wordstr1,sufstr=split_punct(realtok)
            word_str=wordstr1+sufstr
            word_tok=to_token(word_str)
            if sep_line in prefstr and realtok.strip(): line_i+=1
            odx_word=dict(
                para_i=para_i,
                sent_i=sent_i+1,
                sentpart_i=linepart_i,
                line_i=line_i,
                word_i=tok_i+1,
                word_pref=prefstr,
                word_str=word_str,
                word_tok=word_tok,
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
        # eprint(f'!! NLP Parser error: {e}')
        pass

COLS_RENAMER_NLP=dict(
    deprel='dep_type',
    head='dep_head',
    upos='pos_upos',
    xpos='pos_xpos',
    lemma='word_lemma',
)


def get_nlp_doc_wordfeat_df(doc,**kwargs):
    if doc is None: return pd.DataFrame()
    ld=[]
    sents=doc.sentences
    sentd_orig=None
    for sent_i, sent in enumerate(sents):
        ## Get Word Info
        for word_i,word in enumerate(sent.tokens):
            feats=word.to_dict()[0]
            statd=dict(
                # (v,feats[k])
                # for k,v in COLS_RENAMER_NLP.items()
                # if k in feats
                (COLS_RENAMER_NLP.get(k,k), feats[k])
                for k in feats
                if k not in badcols
            )
            for feat in feats.get('feats','').split('|'):
                if not feat: continue
                fk,fv=feat.split('=',1)
                statd[f'pos_{fk.lower()}']=fv
            dx={
                'sent_i': sent_i+1,
                'word_i': word_i+1,
                # 'word_str':word.text,
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

    depthstrd=Counter()
    def getdepthstr(lvlstr):
        lvlstr=lvlstr.split('-',1)[-1]
        depthstrd[lvlstr]+=1
        return f'{lvlstr}-{depthstrd[lvlstr]}'

    pathseend={}

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
                word_constituency_path_nolvl=[xx.split('-',1)[-1] for xx in word_constituency_path]
                


                constituency_depth=len(word_constituency_path)
                dx={
                    'sent_i': sent_i+1,
                    'word_i': word_i+1,
                    'word_depth':constituency_depth,
                    # 'word_constituency':word_constituency_path_str,
                }
                max_wc_len=10
                for wci in range(2,len(word_constituency_path)+1):
                    if wci>max_wc_len: break
                    wcpath=word_constituency_path[:wci]
                    pathseen=tuple(wcpath)
                    if not pathseen in pathseend: pathseend[pathseen]=f'{word_i+1:03}'
                    newlevel=pathseend[pathseen]
                    wcpathstr=f'{newlevel}_{"(".join(wcpath)}'
                    dx[f'sent_depth{wci-1}']=wcpathstr
                ld.append(dx)
    return pd.DataFrame(ld).fillna('')

def get_nlp_feats_df(doc,**kwargs):
    df_feats=get_nlp_doc_wordfeat_df(doc,**kwargs)
    # display(df_feats)

    df_const=get_nlp_doc_constituency_df(doc,**kwargs)
    # display(df_const)

    if len(df_feats) and len(df_const):
        return df_feats.merge(df_const,on=['sent_i','word_i'],how='inner')
    elif len(df_feats):
        return df_feats
    elif len(df_const):
        return dc_const
    return pd.DataFrame()

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




