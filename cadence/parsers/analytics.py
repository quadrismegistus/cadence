# ### 

# ## Cadence/Prosodic integration with LLTK?

# ###
# from ..imports import *

# def get_path_cadence(path_txt):
#     opath=path_txt.replace('/txt/','/cadence/')
#     opath=os.path.splitext(opath)[0]+'.pkl'
#     return opath

# def gen_parses_cadence(path_txt,opath=None,force=False,**attrs):
#     if not path_txt: return
#     if not opath: opath=get_path_cadence(path_txt)
#     if not force and os.path.exists(opath): return
#     if not os.path.exists(path_txt): return
    
#     import cadence as cd
#     odf=parse(path_txt,verbose=False,prose=True,progress=False,by_syll=True)    


#     odir=os.path.dirname(opath)
#     ensure_dir_exists(odir)
#     odf.to_pickle(opath)


# ## Corpus
# def gen_parses_cadence_pmap(self, **attrs):
#     ipaths=list(t.path_txt for t in self.texts())
#     res=pmap(gen_parses_cadence, ipaths, **attrs)

# def get_parses_cadence(self):
#     ipath=get_path_cadence(self.path_txt)
#     return read_df(ipath)


# # def inform_text_metrics(t,**attrs):
# #     from functools import partial
# #     t.parses=partial(get_parses_cadence,self=t,**attrs)
# #     t.parse=partial(gen_parses_cadence,path_txt=t.path_txt,force=True,**attrs)

# # def inform_corpus_metrics(C,**attrs):
# #     from functools import partial
# #     C.parse=partial(gen_parses_cadence_pmap,self=C,force=True,**attrs)


# # ------

