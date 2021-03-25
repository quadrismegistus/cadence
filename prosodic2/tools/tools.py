from ..imports import *

def occurrences(string, sub):
	count = start = 0
	while True:
		start = string.find(sub, start) + 1
		if start > 0:
			count+=1
		else:
			return count

def product(*args):
	if not args:
		return iter(((),)) # yield tuple()
	return (items + (item,)
		for items in product(*args[:-1]) for item in args[-1])


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



def do_pmap_group(obj,*args,**kwargs):
	import pandas as pd
	import types
	func,group_df,group_key,group_name = obj
	
	if type(group_name) not in {list,tuple}:group_name=[group_name]
	if type(group_df)==str: group_df=pd.read_pickle(group_df)

	outgen=func(group_df,*args,**kwargs)
	# outdf=pd.concat(out) if isinstance(out, types.GeneratorType) else out
	for outdf in outgen:
		for x,y in zip(group_key,group_name): outdf[x]=y
		yield outdf


def pmap_groups(func,df_grouped,use_cache=True,num_proc=DEFAULT_NUM_PROC,iter=False,**attrs):
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
	for group_iter in pmap_iter(
		do_pmap_group,
		objs,
		num_proc=num_proc,
		**attrs
	):
		yield from group_iter
