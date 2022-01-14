from ..imports import *



def iter_combos(txtdf,num_proc=1,**kwargs):
    try:
        txtdf=resetindex(txtdf)
        # txtdf=txtdf[txtdf.word_tok!=""]
        for dfi,dfcombo in enumerate(apply_combos(txtdf, 'word_i', 'word_ipa_i',**kwargs)):
            yield dfcombo.assign(combo_i=dfi+1)
    except KeyError:
        yield pd.DataFrame()

def apply_combos(df,group1,group2,**kwargs):
    # combo of indices?
    combo_opts = [
        [x for ii,x in grp.groupby(group2)]
        for i,grp in df.groupby(group1)
    ]

    # poss
    for combo in product(*combo_opts):
        if not len(combo): continue
        odf=pd.concat(combo)
        odf['slot_i']=[i+1 for i in range(len(odf))]
        yield odf.set_index('slot_i')



def tokenize_sentwords_ll(words_ld,**kwargs):
    if not len(words_ld): return []
    listd=defaultdict(list)
    for word_d in words_ld:
        listd[word_d['sent_i']].append(word_d['word_str'].strip())
    olist=[sentl for sent_i,sentl in sorted(listd.items())]
    return olist


def tokenize_sentwords_ll_from_df(words_df,**kwargs):
    if not len(words_df): return []
    return [
        [w.strip() for w in sdf.sort_values('word_i').word_str]
        for si,sdf in sorted(words_df.groupby('sent_i'))
    ]




def tokenize_sents_txt(txt,**y):
    sents=nltk.sent_tokenize(txt)
    lastoffset=0
    osents=[]
    
    for sent in sents:
        offset = txt.find(sent,lastoffset)
        newpref=txt[lastoffset:offset]
        #print([newpref,offset,lastoffset,sent])
        lastoffset=offset + len(sent)
        newsent=newpref + sent
        osents.append(newsent)
    return osents

# def tokenize_words_txt(txt):
#     l=tokenize_nice2(txt)
#     o=[]
#     o0=''
#     for x in l:
#         if zero_punc(x):
#             o+=[o0 + x]
#             o0=''
#         elif o:
#             o[-1]+=x
#         else:
#             o0+=x
#     return o

def tokenize_words_txt(txt):
    l=tokenize_agnostic(txt)
    o=[]
    x0=''
    for x in l:
        if not x.strip():
            x0+=x
        else:
            o+=[x0 + x]
            x0=''
        # if o and not x.strip():# and not o[-1].strip():
        #     o[-1]+=x
        # else:
        #     o+=[x]
    return o

def tokenize_sentwords_iter(
        txt,
        sents=None,
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
    if sents is None: sents=tokenize_sents_txt(txt)
    for sent_i, sent in enumerate(sents):
        tokens=tokenize_words_txt(sent)
        for tok_i,word_str in enumerate(tokens):
            # word_tok=to_token(word_str)
            if sep_line in word_str: line_i+=1
            is_punc=int(not any(x.isalpha() for x in word_str))
            odx_word=dict(
                # para_i=para_i,
                **(dict(para_i=para_i) if para_i is not None else {}),
                sent_i=sent_i+1,
                sentpart_i=linepart_i,
                line_i=line_i,
                word_i=tok_i+1,
                word_str=word_str,
                # word_tok=word_tok,
                word_ispunc=is_punc
            )
            yield odx_word
            if set(word_str)&set(seps_phrase): linepart_i+=1


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



# loading txt/strings
def to_txt(txt_or_fn):
    # load txt
    if type(txt_or_fn)==str and not '\n' in txt_or_fn and os.path.exists(txt_or_fn):
        with open(txt_or_fn,encoding='utf-8',errors='replace') as f:
            return f.read()
    return txt_or_fn



SIZELIM=53687091200

def get_db_scan(path=None):
    if not path or not os.path.exists(path): path=PATH_DB_SCAN
    return get_db(path=path)

def get_db_parse(path=None):
    if not path or not os.path.exists(path): path=PATH_DB_PARSE
    return get_db(path=path)

def get_db(path=None):
    if not path or not os.path.exists(path): path=PATH_DB
    return dc.Cache(path,size_limit=SIZELIM)


def get_linepart_str(lpdf_or_str):
    if type(lpdf_or_str)==str: return lpdf_or_str
    elif type(lpdf_or_str)==pd.DataFrame:
        lpdf=resetindex(lpdf_or_str)
        return ''.join(lpdf[(lpdf.word_ipa_i==1) & (lpdf.syll_i==1)].word_str)
    return ''

def get_linepart_df(lpdf_or_str,**kwargs):
    if type(lpdf_or_str)==pd.DataFrame: return resetindex(lpdf_or_str)
    elif type(lpdf_or_str)==str: return resetindex(get_scansion(lpdf_or_str,**kwargs))
    return pd.DataFrame()








sonnet="""How heavy do I journey on the way,
When what I seek, my weary travel's end,
Doth teach that ease and that repose to say
'Thus far the miles are measured from thy friend!'
The beast that bears me, tired with my woe,
Plods dully on, to bear that weight in me,
As if by some instinct the wretch did know
His rider loved not speed, being made from thee:
The bloody spur cannot provoke him on
That sometimes anger thrusts into his hide;
Which heavily he answers with a groan,
More sharp to me than spurring to his side;
For that same groan doth put this in my mind;
My grief lies onward and my joy behind."""
sonnet1="How heavy do I journey on the way,"

