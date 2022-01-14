from ...imports import *
from .deptree import *
from .metricaltree import *
STRESS_STRS=set("`'")
ALLOW_AMBIG_MTREE=False


def recurse_tree(tree,node_i=0,path=[]):
    o=[]
    if not hasattr(tree,'node_i'):
        tree.node_i=node_i
        node_i+=1

    # path+=[f'{tree.node_i}-{tree.label}']
    if not tree.is_leaf():
        path+=[f'{tree.node_i}-{tree.label}']
        for x in tree.children:
            o+=recurse_tree(x,node_i=node_i,path=list(path))
    else:
        o+=[tuple(path)]
        path=[]
    return o


def get_dtree_str(sent):
    o=[]
    for dep in sent.dependencies:
        w1,rel,w2=dep
        ostr=f'{rel}({w1.text}-{w1.id}, {w2.text}-{w2.id})'
        o+=[ostr]
    return '\n'.join(o)


def get_ctree_str(sent):
    return str(sent.constituency)

def get_treeparse_str(sent):
    ctree=get_ctree_str(sent)
    dtree=get_dtree_str(sent)
    return f'{ctree}\n\n{dtree}'

def get_mtree(sent,**kwargs):
    try:
        tree_str=get_treeparse_str(sent)
        depobj=DependencyTree.fromstring(tree_str)
        metrobj=CadenceMetricalTree.convert(depobj)
        return metrobj
    #except (IndexError,KeyError,AttributeError,ValueError) as e:
    except AssertionError as e:
        print('!!',e)
        pass


def find_phrasal_heads(self):
    for subtree in self:
        if type(subtree)!=str:
            numsubs=len(subtree)
            firstsub,lastsub=subtree[0],subtree[-1]
            if numsubs>1 and not subtree._preterm and lastsub._preterm:
                if lastsub._word_tok: lastsub._phrasal_head=1
                # print('phrasal head', str(subtree))
                for sub in subtree[:-1]:
                    if sub._word_tok: sub._phrasal_head=0
                    # print('not phrasal head', str(sub))
            find_phrasal_heads(subtree)



class CadenceMetricalTree(MetricalTree):
    def __init__(self,
            node,
            children,
            dep=None,
            lstress=0,
            pstress=np.nan,
            stress=np.nan,
            allow_ambig=ALLOW_AMBIG_MTREE,
            **kwargs):

        self._lstress = lstress
        self._pstress = pstress
        self._stress = stress
        super(MetricalTree, self).__init__(node, children, dep)
        self.set_label()
        self._phrasal_head=np.nan
        self._phrasal_stress_peak=np.nan
        self._phrasal_stress_valley=np.nan
        self._pstrength=np.nan
        self._stress_num_binary=1.0
        self._stress_num=1.0
        self._seg = None
        self._nsyll = np.nan
        self._nstress = np.nan
        self._word_tok=''
        

        if self._preterm:
            word_str=str(self[0])
            word_tok=to_token(word_str)
            if word_tok:
                sylls_df=get_syllable_df(word_str,**kwargs)
                if len(sylls_df):
                    self._num_variants=sylls_df.word_ipa_i.max()
                    self._is_ambig=self._num_variants>1
                    self._word_tok=word_tok
                    
                    # go for least stressed possible
                    sylgrps = [g for i,g in sylls_df.groupby('word_ipa_i')]
                    sylgrps.sort(key=lambda g: g.prom_stress.sum())
                    sylls_df1=sylgrps[0]
                    
                    self._nsyll=sylls_df1.syll_i.max()
                    self._seg='.'.join(sylls_df1.syll_ipa)
                    self._nstress=len([x for x in sylls_df1.prom_stress if x>0])
                    
                    # ambig?
                    self._stress_num=sylls_df1.prom_stress.max()
                    if allow_ambig and self._nsyll==1 and self._is_ambig:
                        self._stress_num=.5
                        self._lstress=self._stress_num - 1.0
                        self._stress_num_binary = 1.0
                    else:
                        self._stress_num_binary = 1.0 if self._stress_num>0 else 0.0
                        self._lstress=self._stress_num_binary - 1.0
            else:
                self._stress_num_binary=np.nan
                self._stress_num=np.nan
                self._word_tok=''


    def lstress(self): return self._lstress
    def pstress(self): return self._pstress
    def pstress_pos(self): return -(self._pstress-1)
    def stress(self): return self._stress
    def stress_pos(self): return -(self._stress-1)
    def seg(self): return self._seg if self._seg is not None else []
    def nseg(self): return len(self._seg) if self._seg is not None else np.nan
    def nsyll(self): return self._nsyll
    def nstress(self): return self._nstress


    # =====================================================================
    # Set the lexical stress of the node
    def set_lstress(self,allow_ambig=ALLOW_AMBIG_MTREE):
        # self.gen_word_info()

        if self._preterm:
            if self[0].lower() in super(MetricalTree, self)._contractables:
                self._lstress = np.nan
            elif self._cat in super(MetricalTree, self)._punctTags:
                self._lstress = np.nan
            elif self._cat in MetricalTree._unstressedTags:
                self._lstress = -1
            elif allow_ambig and self._cat in MetricalTree._ambiguousTags:
                self._lstress = -.5
            elif self._dep in MetricalTree._unstressedDeps:
                self._lstress = -1
            elif allow_ambig and self._dep in MetricalTree._ambiguousDeps:
                self._lstress = -.5
            elif allow_ambig and self._nsyll==1 and self._is_ambig:
                self._lstress = -.5
            elif allow_ambig:
                self._lstress = self._stress_num - 1.0
            else:
                self._lstress = self._stress_num_binary - 1.0

            # print(self,self._lstress)
        else:
            for child in self:
                child.set_lstress()
        self.set_label()

    def set_phrasal_peaks(self):
        preterms=list(self.preterminals())
        for i2,w2 in enumerate(preterms):
            w1=preterms[i2-1] if i2 else None
            w3=preterms[i2+1] if (i2+1)<len(preterms) else None
            if np.isnan(w2._pstress): continue
            if w1 and not np.isnan(w1._pstress) and w1._pstress < w2._pstress:
                w1._phrasal_stress_valley=1
                w1._phrasal_stress_peak=0
                w1._pstrength=0.0

                w2._phrasal_stress_peak=1
                w2._phrasal_stress_valley=0
                w2._pstrength=1.0
            if w3 and not np.isnan(w3._pstress) and w3._pstress < w2._pstress:
                w3._phrasal_stress_valley=1
                w3._phrasal_stress_peak=0
                w3._pstrength=0.0

                w2._phrasal_stress_peak=1
                w2._phrasal_stress_valley=0
                w2._pstrength=1.0

    def get_stats(self, arto=False, **kwargs):
        #self.gen_word_info()
        try:
            data = defaultdict(list)
            self.set_lstress()
            self.set_pstress()
            self.set_stress()
            find_phrasal_heads(self)
            self.set_phrasal_peaks()
            
            j = 0
            preterms = list(self.preterminals())
            min1p = float(min([preterm.pstress() for preterm in preterms if not np.isnan(preterm.pstress())]))
            max1p = max([preterm.pstress() for preterm in preterms if not np.isnan(preterm.pstress())]) - min1p
            min1s = float(min([preterm.stress() for preterm in preterms if not np.isnan(preterm.stress())]))
            max1s = max([preterm.stress() for preterm in preterms if not np.isnan(preterm.stress())]) - min1s
            # sent1 = ' '.join([preterm[0] for preterm in preterms])
            # sentlen1 = len(preterms)

            for j,preterm in enumerate(preterms):
                data['word_i'].append(j+1)
                data['word_str'].append(preterm[0])
                # data['mtree_pstress'].append(preterm.pstress())
                data['prom_lstress'].append(preterm.lstress()+1)
                data['prom_pstress'].append((preterm.pstress()-min1p)/max1p if max1p else np.nan)
                data['prom_tstress'].append((preterm.stress()-min1s)/max1s if max1s else np.nan)
                data['prom_pstrength'].append(preterm._pstrength)
                data['mtree_ishead'].append(preterm._phrasal_head)
            return pd.DataFrame(data)
        except ValueError as e:
            # eprint('!!',e,'!!')
            return pd.DataFrame()