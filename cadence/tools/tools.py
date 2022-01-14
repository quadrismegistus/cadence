from ..imports import *

def concatt(o,index=None):
    odf=pd.DataFrame()
    o=list(o)
    if len(o):
        odf=pd.concat(o)
        if index==True:
            odf=setindex(odf)
        elif index==False:
            odf=resetindex(odf)
    return odf


def safe_merge(df1,df2,on=['sent_i','word_i'],badcols={'word_str'},how='outer'):
    df1=resetindex(df1)
    df2=resetindex(df2)
    if df1 is None and df2 is None: return pd.DataFrame()
    if not len(df1) and not len(df2): return pd.DataFrame()
    if len(df1) and not len(df2): return df1
    if len(df2) and not len(df1): return df2
    
    df1cols=set(df1.columns)
    df2cols=set(df2.columns)
    
    if set(on) - df2cols: return df1
    if set(on) - df1cols: return df2
    
    df2cols = (df2cols - df1cols) | set(on)

    return df1[df1cols].merge(df2[df2cols],on=on,how=how)

def to_token(toktxt,**y):
    #return split_punct(toktxt.lower())[1]
    return zero_punc(toktxt.strip()).lower()



def nice_int_df(odf):
    for col in odf.columns:
        if col.endswith('_i') or col.startswith('is_') or col.endswith('_rank'):
            odf[col]=pd.to_numeric(odf[col], errors='coerce', downcast='integer')
    return odf


def clean_text(txt):
    return txt.replace('\r\n','\n').replace('\r','\n')

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, end='\n', **kwargs)

### convenient objs
def kwargs_key(kwargs,bad_keys={'num_proc','progress','desc','by_line','only_best'},good_keys={}):
    return ', '.join(
        f'{k}={v}'
        for k,v in kwargs.items()
        if not bad_keys or k not in bad_keys
        and not good_keys or k in good_keys
    )
    

def to_blosc(obj):
    import pickle,blosc
    binary=pickle.dumps(obj)
    compressed=blosc.compress(binary)
    return compressed
    
def from_blosc(compressed):
    import pickle,blosc
    binary=blosc.decompress(compressed)
    obj=pickle.loads(binary)
    return obj


def getcol(df,col):
    if col in set(df.columns):
        return pd.Series(df[col])
    elif col in set(df.index.names):
        return pd.Series(df.index.get_level_values(col))
    else:
        return pd.Series()


def split_punct(tok):
    if not tok: return ('','','')
    toks=tokenize_agnostic(tok)
    wordil=[]
    
    try:
        for i,x in enumerate(toks):
            if any(y.isalpha() for y in x):
                wordil+=[i]
        pref=''.join([
            x
            for i,x in enumerate(toks)
            if i<wordil[0]
        ])
        suf=''.join([
            x
            for i,x in enumerate(toks)
            if i>wordil[-1]
        ])
        words=''.join(
            toks[wordil[0] : wordil[-1]+1]
        ) if wordil else ''
        return (pref,words,suf)
    except IndexError:
        return ('',tok,'')

def zero_punc(token):
    return ''.join(x for x in token if x.isalpha())

def tokenize_agnostic(txt):
    return re.findall(r"[\w']+|[.,!?; -—–'\n]", txt)
    
def tokenize_fast(line,lower=False):
	line = line.lower() if lower else line
	import re
	# tokenize using reg ex (fast)
	tokens = re.findall("[A-Z]{2,}(?![a-z])|[A-Z][a-z]+(?=[A-Z])|[\'\w\-]+",line)
	# remove punctuation on either end
	from string import punctuation
	tokens = [tok.strip(punctuation) for tok in tokens]
	# make sure each thing in list isn't empty
	tokens = [tok for tok in tokens if tok]
	return tokens

# tokenize
def tokenize_nltk(txt,lower=False):
	# lowercase
	txt_l = txt.lower() if lower else txt
	# use nltk
	tokens = nltk.word_tokenize(txt_l)
	# weed out punctuation
	tokens = [
		tok
		for tok in tokens
		if tok[0].isalpha()
	]
	# return
	return tokens

# def tokenize_nice(xstr,starters=set("([‘“"),**kwargs):
#     l=tokenize_agnostic(xstr)
#     l2=[]
#     addback=False
#     for x in l:
#         if not x:#.strip():
#             pass
#         elif x[0].isalpha():
#             if addback and len(l2):
#                 l2[-1]+=x
#                 addback=False
#             else:
#                 l2+=[x]
#         else:
#             if x in starters:
#                 l2+=[x]
#                 addback=True
#             elif len(l2):
#                 l2[-1]+=x
#             else:
#                 l2+=[x]
#                 addback=True
#     return l2


# def tokenize(txt,*x,**y):
# 	return tokenize_fast(txt,*x,**y)
def tokenize_nice_iter2(s,sep=' ',**kwargs):
    s=s.replace('\r\n','\n')
    s=s.replace('\r','\n')
    s=s.replace('\n',' \n ')
    s=s.replace('\t',' \t ')
    wnow=''
    for i,w in enumerate(s.split(sep)):
        w2=sep+w if i else w
        if w.strip(): # word
            word=wnow+w2
            yield word
            wnow=''
        else:
            wnow+=w2

def tokenize_nice2(s,**kwargs): return list(tokenize_nice_iter2(s,**kwargs))
def to_words_str(s,**kwargs): return tokenize_nice(s,**kwargs)

def subfinder(mylist, pattern):
    matches = []
    for i in range(len(mylist)):
        if mylist[i] == pattern[0] and mylist[i:i+len(pattern)] == pattern:
            matches.append(pattern)
    return matches

DTOK_TREEBANK=None
def detokenize_treebank(x):
    global DTOK_TREEBANK
    if DTOK_TREEBANK is None:
        from nltk.tokenize.treebank import TreebankWordDetokenizer
        DTOK_TREEBANK = TreebankWordDetokenizer()
    return DTOK_TREEBANK.detokenize(x)

def detokenize(x):
    x=detokenize_treebank(x)
    return x

def setindex(df,key=LINEKEY,badcols={'index','level_0'},sort=True):
    if not len(df): return df
    df = df[set(df.columns) - set(df.index.names)]
    df = resetindex(df)

    cols=[]
    for x in key:
        if not x in set(cols) and x in set(df.columns):
            cols.append(x)
    nice_int_df(df)
    odf=df.set_index(cols)
    if sort: odf=odf.sort_index()
    odf=odf[
        sorted([col for col in odf.columns if not col in badcols and col not in key])
    ]

    constraints = [c for c in odf.columns if c.startswith('*')]
    resortcols = ['*total'] + [c for c in constraints if c!='*total']
    resortcols+= list(sorted([c for c in odf.columns if c not in set(constraints)]))
    return odf[[c for c in resortcols if c in odf.columns]]

def resetindex(df,badcols={'level_0','index'},**y):
    cols=list(df.columns)
    inds=list(df.index.names)
    both=set(cols)&set(inds)
    okcols=set(cols) - both - badcols
    newdf=df[okcols].reset_index(**y)
    nowcols=list(newdf.columns)
    newcols=[col for col in LINEKEY if col in set(nowcols) and col not in badcols]
    newcols+=[col for col in nowcols if col not in set(LINEKEY) and col not in badcols]
    newdf=newdf[newcols]
    newdf=nice_int_df(newdf)
    return newdf
    # if set(newdf.columns) & badcols: return df
    # return newdf


def occurrences(string, sub):
    count = start = 0
    while True:
        start = string.find(sub, start) + 1
        if start > 0:
            count+=1
        else:
            return count

import numpy as np
def rolling_slices(df,window_len=3,incl_empty=True,keep_last_keys=[]):
    nrad=(window_len - 1)//2
    for i in range(len(df)):
        mini = i-nrad
        maxi = i+nrad
        empty_row=pd.Series(dict((k,np.nan) for k in df.columns))
        for xx in keep_last_keys: empty_row[xx]=df.iloc[0][xx]
        irows=[]
        inames=[]
        for ii in range(mini,maxi+1):
            inames+=[ii]
            if ii<0 or ii>=len(df):
                if incl_empty:

                    irows+=[empty_row]
            else:
                irows+=[df.iloc[ii]]
        yield pd.DataFrame(irows,index=inames)
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# def product(*args):
# 	if not args:
# 		return iter(((),)) # yield tuple()
# 	return (items + (item,)
# 		for items in product(*args[:-1]) for item in args[-1])


def hashstr(*x):
    import hashlib
    return hashlib.sha224(str(x).encode('utf-8')).hexdigest()

def pmap_do(inp):
    func,obj,args,kwargs = inp
    return func(obj,*args,**kwargs)

def pmap_iter(func, objs, args=[], kwargs={}, num_proc=DEFAULT_NUM_PROC, use_threads=False, progress=True, desc=None, position=0, leave=True, **y):
    """
    Yields results of func(obj) for each obj in objs
    Uses multiprocessing.Pool(num_proc) for parallelism.
    If use_threads, use ThreadPool instead of Pool.
    Results in any order.
    """

    # imports
    import multiprocessing as mp
    from tqdm import tqdm

    # check num proc
    num_cpu = mp.cpu_count()
    if num_proc>num_cpu: num_proc=num_cpu

    # if parallel
    if not desc: desc=f'Mapping {func.__name__}()'
    if desc: desc=f'{desc} [x{num_proc}]'
    if num_proc>1 and ((type(objs) not in {list,tuple,set}) or len(objs)>1):

        # real objects
        objects = [(func,obj,args,kwargs) for obj in objs]

        # create pool
        pool=mp.Pool(num_proc) if not use_threads else mp.pool.ThreadPool(num_proc)

        # yield iter
        iterr = pool.imap(pmap_do, objects)
        iterr=tqdm(
            iterr,
            total=len(objects),
            desc=desc,
            disable=not progress,
            leave=leave,
            position=position
        )
        yield from iterr

        # Close the pool?
        pool.close()
        pool.join()
    else:
        # yield
        iterr=tqdm(
            objs,
            desc=desc,
            disable=not progress,
            leave=leave,
            position=position
        )
        for obj in iterr:
            yield func(obj,*args,**kwargs)

def pmap(*x,**y):
    """
    Non iterator version of pmap_iter
    """
    # return as list
    return list(pmap_iter(*x,**y))

def index_by_truth(x):
    i=0
    for y in x:
        if y:
            yield i
            i+=1
        else:
            yield np.nan


def joindfs(a,b):
    bcols = set(b.columns) - set(a.columns)
    return a.join(b[bcols])


def hashstr(x):
	import hashlib
	return hashlib.sha224(str(x).encode('utf-8')).hexdigest()


# # Use sqlite dictionary
# def get_db(
#         prefix,
#         mode='c',
#         folders=[],
#         autocommit=False,
#         ):
#     if mode=='w': autocommit=True
#     ofnfn=os.path.join(PATH_DATA, f'db.{prefix}.sqlite')
#     odir=os.path.dirname(ofnfn)
#     if not os.path.exists(odir): os.makedirs(odir)
#     if not os.path.exists(ofnfn): mode='c'
#     return SqliteDict(
#         ofnfn,
#         tablename='data',
#         autocommit=autocommit,
#         flag='r' if mode=='r' else 'c',
#         timeout=30
#     )


# loading txt/strings
def to_fn_txt(txt_or_fn):
    # load txt
    if type(txt_or_fn)==str and not '\n' in txt_or_fn and os.path.exists(txt_or_fn):
        fn=txt_or_fn
        with open(fn,encoding='utf-8',errors='replace') as f:
            txt=f.read()
    else:
        fn=''
        txt=txt_or_fn
    return (fn,txt.strip())



def slices(l,n,strict=True):
    o=[]
    for x in l:
        o.append(x)
        if len(o)>n: o.pop(0)
        if not strict or len(o)==n:
            yield list(o)

# def apply_combos(df,group1,group2,combo_key='combo_i'):
#     # combo of indices?
#     combo_opts = [
#         [x for ii,x in grp.groupby(group2)]
#         for i,grp in df.groupby(group1)
#     ]

#     # poss
#     for combo in product(*combo_opts):
#         if not len(combo): continue
#         yield pd.concat(combo)# if len(combo) else pd.DataFrame()

def pmap_iter_groups(func,df_grouped,use_cache=False,num_proc=DEFAULT_NUM_PROC,iter=False,**attrs):
    import os,tempfile,pandas as pd
    from tqdm import tqdm


    # get index/groupby col name(s)
    group_key=df_grouped.grouper.names
    # if not using cache
    # if not use_cache or attrs.get('num_proc',1)<2:
    if not use_cache or len(df_grouped)<2 or num_proc<2:
        objs=[
            (func,group_df,group_key,group_name)
            for group_name,group_df in df_grouped
        ]
    else:
        objs=[]
        tmpdir=tempfile.mkdtemp()
        # for i,(group_name,group_df) in enumerate(tqdm(list(df_grouped),desc='Preparing input')):
        for i,(group_name,group_df) in enumerate(df_grouped):
            tmp_path = os.path.join(tmpdir, str(i)+'.pkl')
            # print([i,group_name,tmp_path,group_df])
            group_df.to_pickle(tmp_path)
            objs+=[(func,tmp_path,group_key,group_name)]

    # desc?
    if not attrs.get('desc'): attrs['desc']=f'Mapping {func.__name__}'

    #iterfunc = pmap if not iter else pmap_iter
    #return pd.concat(iterfunc) if not iter else
    return pmap_iter(
        do_pmap_group,
        objs,
        num_proc=num_proc,
        **attrs
    )


def do_pmap_group(obj,*args,**kwargs):
    import pandas as pd
    import types
    func,group_df,group_key,group_name = obj

    if type(group_name) not in {list,tuple}:group_name=[group_name]
    if type(group_df)==str: group_df=pd.read_pickle(group_df)
    out=func(group_df,*args,**kwargs)
    if isinstance(out, types.GeneratorType):
        out=[x for x in out]
    if type(out)==list:
        try:
            out=[x for x in out if type(x) in {pd.DataFrame, pd.Series}]
            out=pd.concat(out)
        except ValueError:
            return out
    if type(out)==pd.DataFrame:
        cols1=list(out.columns)
        for x,y in zip(group_key,group_name): out[x]=y
        out=out[group_key + cols1]
    return out


def pmap_groups(*x,**y):
    res = list(pmap_iter_groups(*x,**y))
    resl = []
    for x in res:
        if type(x)==list:
            for y in x:
                resl.append(y)
        else:
            resl.append(x)
    return pd.concat(resl) if len(resl) else pd.DataFrame()


def check_basic_config():
    # check basic config
    try:
        if not os.path.exists(PATH_HOME):
            os.makedirs(PATH_HOME)
            print(f'[cadence] Created directory {PATH_HOME} to store data within')
    except Exception:
        pass
    if not os.path.exists(PATH_DATA): os.makedirs(PATH_DATA)
    if not os.path.exists(os.path.join(PATH_DATA,'en')):
        zipfn=os.path.join(PATH_HOME,'data_cadence.zip')
        download(DATA_URL, zipfn)
        unzip(zipfn, PATH_HOME, progress=False)
    try:
        nltk.word_tokenize('testing')
    except LookupError:
        nltk.download('punkt',quiet=True)
    try:
        nltk.corpus.stopwords.words('english')
    except LookupError:
        nltk.download('stopwords',quiet=True)


### utils
def printm(x):
    try:
        from IPython.display import Markdown
        return display(Markdown(x))
    except ImportError:
        print(x)



def download_wget(url, save_to, verbose=True, **attrs):
    import wget
    save_to_dir,save_to_fn=os.path.split(save_to)
    if save_to_dir:
        if not os.path.exists(save_to_dir): os.makedirs(save_to_dir)
        os.chdir(save_to_dir)
    fn=wget.download(url,bar=wget.bar_adaptive)
    os.rename(fn,save_to_fn)
    # print('\n>> saved:',save_to)

def download(url,save_to,force=False,desc='',verbose=True):
    here=os.getcwd()
    download_wget(url,save_to,desc=desc,verbose=verbose)
    os.chdir(here)




def unzip(zipfn, dest='.', flatten=False, overwrite=False, replace_in_filenames={},desc='',progress=True):
    from zipfile import ZipFile
    from tqdm import tqdm

    # Open your .zip file
    if not desc: desc=f'Extracting {os.path.basename(zipfn)}'
    with ZipFile(zipfn) as zip_file:
        namelist=zip_file.namelist()

        # Loop over each file
        iterr=tqdm(iterable=namelist, total=len(namelist),desc=desc) if progress else namelist
        for member in iterr:
            # Extract each file to another directory
            # If you want to extract to current working directory, don't specify path
            filename = os.path.basename(member)
            if not filename: continue
            target_fnfn = os.path.join(dest,member) if not flatten else os.path.join(dest,filename)
            for k,v in replace_in_filenames.items(): target_fnfn = target_fnfn.replace(k,v)
            if not overwrite and os.path.exists(target_fnfn): continue
            target_dir = os.path.dirname(target_fnfn)
            try:
                if not os.path.exists(target_dir): os.makedirs(target_dir)
            except FileExistsError:
                pass
            except FileNotFoundError:
                continue

            with zip_file.open(member) as source, open(target_fnfn,'wb') as target:
                shutil.copyfileobj(source, target)




def get_num_lines(filename):
    from smart_open import open

    def blocks(files, size=65536):
        while True:
            b = files.read(size)
            if not b: break
            yield b

    with open(filename, 'r', errors='ignore') as f:
        numlines=sum(bl.count("\n") for bl in blocks(f))

    return numlines






def read_df(ifn,key='',**attrs):
	if not os.path.exists(ifn): return
	import pandas as pd
	ext = os.path.splitext(ifn.replace('.gz',''))[-1][1:]
	if ext=='csv':
		return pd.read_csv(ifn,**attrs)
	elif ext in {'xls','xlsx'}:
		return pd.read_excel(ifn,**attrs)
	elif ext in {'txt','tsv'}:
		return pd.read_csv(ifn,sep='\t',**attrs)
	elif ext=='ft':
		return pd.read_feather(ifn,**attrs)
	elif ext=='pkl':
		return pd.read_pickle(ifn,**attrs)
	elif ext=='h5':
		return pd.read_hdf(ifn, key=key,**attrs)
	else:
		raise Exception(f'[save_df()] What kind of df is this: {ifn}')



def read_url(url):
    return requests.get(url).content.decode('utf-8')