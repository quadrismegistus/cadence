from ..imports import *
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
	df = df[set(df.columns) - set(df.index.names)]
	df = resetindex(df)
		
	cols=[]
	for x in key:
		if not x in set(cols) and x in set(df.columns):
			cols.append(x)
		
	odf=df.set_index(cols)
	if sort: odf=odf.sort_index()
	odf=odf[[col for col in odf.columns if not col in badcols and col not in key]]
	
	constraints = [c for c in odf.columns if c.startswith('*')]
	resortcols = ['*total'] + [c for c in constraints if c!='*total']
	resortcols+= list(sorted([c for c in odf.columns if c not in set(constraints)]))
	return odf[[c for c in resortcols if c in odf.columns]]

def resetindex(df,badcols={'level_0','index'},**y):
	cols=set(df.columns)
	inds=set(df.index.names)
	both=cols&inds
	# print(cols)
	# print(inds)
	# print(both)
	newdf=df[cols - both - badcols].reset_index(**y)
	# print(newdf.columns)
	# print()
	return newdf


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

def pmap_iter(func, objs, args=[], kwargs={}, num_proc=DEFAULT_NUM_PROC, use_threads=False, progress=True, desc=None, **y):
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
	if num_proc>1 and len(objs)>1:

		# real objects
		objects = [(func,obj,args,kwargs) for obj in objs]

		# create pool
		pool=mp.Pool(num_proc) if not use_threads else mp.pool.ThreadPool(num_proc)

		# yield iter
		iterr = pool.imap(pmap_do, objects)
		
		for res in tqdm(iterr,total=len(objects),desc=desc) if progress else iterr:
			yield res

		# Close the pool?
		pool.close()
		pool.join()
	else:
		# yield
		for obj in (tqdm(objs,desc=desc) if progress else objs):
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
		for x,y in zip(group_key,group_name): out[x]=y
	return out
	
def joindfs(a,b):
    bcols = set(b.columns) - set(a.columns)
    return a.join(b[bcols])



def slices(l,n,strict=True):
    o=[]
    for x in l:
        o.append(x)
        if len(o)>n: o.pop(0)
        if not strict or len(o)==n:
            yield list(o)
def apply_combos(df,group1,group2,combo_key='combo_i'):
    # combo of indices?
    combo_opts = [
        [x for ii,x in grp.groupby(group2)]
        for i,grp in df.groupby(group1)
    ]
    
    # poss
    for combo in product(*combo_opts):
        yield pd.concat(combo)
def pmap_iter_groups(func,df_grouped,use_cache=True,num_proc=DEFAULT_NUM_PROC,iter=False,**attrs):
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
def pmap_groups(*x,**y):
	res = list(pmap_iter_groups(*x,**y))
	# print([type(x) for x in res])
	# for y in res[-1]:
		# print(type(y), y)
	resl = []
	for x in res:
		if type(x)==list:
			for y in x:
				resl.append(y)
		else:
			resl.append(x)
	return pd.concat(resl)







### utils
def printm(x):
	from IPython.display import display,Markdown
	display(Markdown(x))
