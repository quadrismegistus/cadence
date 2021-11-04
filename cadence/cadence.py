# system imports
from .imports import *


### convenient objs
def kwargs_key(kwargs,bad_keys={'num_proc','progress','desc'}):
    return hashstr(str(sorted(
        (k,v)
        for k,v in kwargs.items()
        if k not in bad_keys
    )))




def Verse(txt,**kwargs):
    kwargs={**dict(verse=True), **kwargs}
    return Text(txt,**kwargs)
def Poem(txt,**kwargs):
    kwargs={**dict(verse=True), **kwargs}
    return Text(txt,**kwargs)
def Prose(txt,**kwargs):
    kwargs={**dict(prose=True), **kwargs}
    return Text(txt,**kwargs)
def FreeVerse(txt,**kwargs):
    kwargs={**dict(linebreaks=True,phrasebreaks=True), **kwargs}
    return Text(txt,**kwargs)
    
### texts
class Text(object):
    def __init__(self,
            txt_or_fn_or_scandf,
            **kwargs):
        self.fn=None
        self.txt=None
        self.scandf=None
        self._scans={}
        self._parses={}
        self._num_lines=None
        self._num_stanzas=None
        self.infod={}
        
        self.kwargs=kwargs
        for k,v in self.kwargs.items(): setattr(self,k,v)
        self.kwargs_key=kwargs_key(self.kwargs)
        
        # load data
        if type(txt_or_fn_or_scandf)==str:
            if os.path.exists(txt_or_fn_or_scandf):
                self.fn=txt_or_fn_or_scandf
                self.txt=to_txt(self.fn)
            else:
                self.fn=None
                self.txt=txt_or_fn_or_scandf
        elif type(txt_or_fn_or_scandf)==pd.DataFrame:
            self.fn=None
            self.scandf=self._scans[self.kwargs_key]=scandf=txt_or_fn_or_scandf
            self.txt=to_txt_from_scandf(scandf)
        else:
            raise Exception(f'Input not recognised: {type(txt_or_fn_or_scandf)}')
    
    
    
    def __repr__(self):
        o=self.txt.split('\n\n')[0] if self.txt is not None else ""
        o='\t' + '\n\t'.join(l for l in o.split('\n'))
        o=f'''<cadence.Text: {self.first_line} ({self.num_stanzas} stanza{"s" if self.num_stanzas>1 else ""}, {self.num_lines} line{"s" if self.num_lines>1 else ""})>'''.strip()
        #o='\n'.join(l.strip() for l in o.split('\n'))
        return o
    
    @property
    def first_line(self):
        from string import punctuation
        return self.txt.strip().split('\n')[0].strip(punctuation).strip()
    @property
    def first_stanza(self):
        return self.txt.strip().split('\n\n')[0].strip()
    
    
    @property
    def num_lines(self):
        if self._num_lines is None:
            self._num_lines=get_num_lines(
                self.txt if self.scandf is None else self.scandf
            )
        return self._num_lines
    @property
    def num_stanzas(self):
        if self._num_stanzas is None:
            self._num_stanzas=get_num_stanzas(
                self.txt if self.scandf is None else self.scandf
            )
        return self._num_stanzas
    
    
    def scan(self, force=False, **kwargs):
        kwargs={**self.kwargs, **kwargs}
        key=kwargs_key(kwargs)
        if force or not key in self._scans:
            self._scans[key]=scan(self.txt,**kwargs)
        return self._scans[key]
    
    def parse(self,
            force=False,
            verbose=True,
            only_best=False,
            only_unbounded=True,
            **kwargs):
        kwargs['verbose']=verbose
        kwargs_line={**self.kwargs, **kwargs, **{'by_syll':False}}
        kwargs_syll={**self.kwargs, **kwargs, **{'by_syll':True}}
        key_line=kwargs_key(kwargs_line)
        key_syll=kwargs_key(kwargs_syll)
        if force or not (key_syll in self._parses) or (not key_line in self._parses):
            self._parses[key_syll]=parse(self.txt, **kwargs_syll)
            self._parses[key_line]=to_lines(self._parses[key_syll])
        elif kwargs.get('verbose',True):
            for li,linedf in sorted(self._parses[key_syll].reset_index().groupby(['stanza_i','line_i'])):
                display(show_parse(linedf))

        self.infod=info_parses(self._parses[key_line])
        if verbose: printm(show_info_parses(self.infod))
                
        
    def parses(self,
            force=True,
            only_best=False,
            only_unbounded=True,
            **kwargs):
        kwargs={**self.kwargs, **kwargs}
        kwargs_line={**self.kwargs, **kwargs, **{'by_syll':False}}
        kwargs_syll={**self.kwargs, **kwargs, **{'by_syll':True}}
        key_line=kwargs_key(kwargs_line)
        key_syll=kwargs_key(kwargs_syll)
        key=key_syll if kwargs.get('by_syll') else key_line
        if not key in self._parses:
            self.parse(force=force, **kwargs)
        if not key in self._parses: return
        
        odf=self._parses[key]
        if only_unbounded and ('parse_is_bounded' in set(odf.index.names) or 'parse_is_bounded' in set(odf.columns)):
            #odf=odf[odf.parse_is_bounded==False]
            odf=odf.query('parse_is_bounded==False')
        if only_best and ('parse_rank' in set(odf.index.names) or 'parse_rank' in set(odf.columns)):
            odf=odf.query('parse_rank==1')
        
        return odf

    def best_parses(self, force=False, **kwargs):
        return self.parses(force=force,only_best=True,**kwargs)
    def all_parses(self, force=False,**kwargs):
        return self.parses(force=force,only_best=False,only_unbounded=False,**kwargs)
    def unbounded_parses(self, force=False,**kwargs):
        return self.parses(force=force,only_best=False,only_unbounded=True,**kwargs)