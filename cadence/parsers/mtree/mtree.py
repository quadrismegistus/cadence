from ...imports import *

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

def get_mtree(sent):
    tree_str=get_treeparse_str(sent)
    dtree=MetricalTree.fromstring(tree_str)
    return dtree



#=============================================================
def get_stats(self, generator, arto=False,format_pandas=False):
    """"""

    data = defaultdict(list)
    i = 0
    for t in generator:
        i += 1
        ambig1 = t.ambiguity(stress_polysyll=False)
        ambig2 = t.ambiguity(stress_polysyll=True)
        tree1 = t.max_stress_disambiguate()[0]
        tree1.set_pstress()
        tree1.set_stress()
        tree2a = t.min_stress_disambiguate(stress_polysyll=True)[0]
        tree2a.set_pstress()
        tree2a.set_stress()
        tree2b = t.min_stress_disambiguate(stress_polysyll=False)[0]
        tree2b.set_pstress()
        tree2b.set_stress()

        j = 0
        preterms1 = list(tree1.preterminals())
        min1 = float(min([preterm.stress() for preterm in preterms1 if not np.isnan(preterm.stress())]))
        max1 = max([preterm.stress() for preterm in preterms1 if not np.isnan(preterm.stress())]) - min1
        preterms2a = list(tree2a.preterminals())
        min2a = float(min([preterm.stress() for preterm in preterms2a if not np.isnan(preterm.stress())]))
        max2a = max([preterm.stress() for preterm in preterms2a if not np.isnan(preterm.stress())]) - min2a
        preterms2b = list(tree2b.preterminals())
        min2b = float(min([preterm.stress() for preterm in preterms2b if not np.isnan(preterm.stress())]))
        max2b = max([preterm.stress() for preterm in preterms2b if not np.isnan(preterm.stress())]) - min2b
        preterms_raw = list(t.preterminals())
        minmean = float(min([np.mean([preterm1.stress(), preterm2a.stress(), preterm2b.stress()]) for preterm1, preterm2a, preterm2b in zip(preterms1, preterms2a, preterms2b) if not np.isnan(preterm1.stress())]))
        maxmean = max([np.mean([preterm1.stress(), preterm2a.stress(), preterm2b.stress()]) for preterm1, preterm2a, preterm2b in zip(preterms1, preterms2a, preterms2b) if not np.isnan(preterm1.stress())]) - minmean
        sent = ' '.join([preterm[0] for preterm in preterms_raw])
        sentlen = len(preterms_raw)
        for preterm1, preterm2a, preterm2b, preterm_raw in zip(preterms1, preterms2a, preterms2b, preterms_raw):
            j += 1
            data['widx'].append(j)
            data['norm_widx'].append(float(j) / sentlen if sentlen else np.nan)
            data['word'].append(preterm1[0])
            if preterm_raw._lstress == 0:
                data['lexstress'].append('yes')
            elif preterm_raw._lstress == -.5:
                data['lexstress'].append('ambig')
            elif preterm_raw._lstress == -1:
                data['lexstress'].append('no')
            else:
                data['lexstress'].append('???')
            data['seg'].append(' '.join(preterm1.seg()))
            data['nseg'].append(preterm1.nseg())
            data['nsyll'].append(preterm1.nsyll())
            data['nstress'].append(preterm1.nstress())
            data['pos'].append(preterm1.category())
            data['dep'].append(preterm1.dependency())
            if arto:
                data['m1'].append(-(preterm1.stress()-1))
                data['m2a'].append(-(preterm2a.stress()-1))
                data['m2b'].append(-(preterm2b.stress()-1))
                data['mean'].append(-(np.mean([preterm1.stress(), preterm2a.stress(), preterm2b.stress()])-1))
            else:
                data['m1'].append(preterm1.stress())
                data['m2a'].append(preterm2a.stress())
                data['m2b'].append(preterm2b.stress())
                data['mean'].append(np.mean([preterm1.stress(), preterm2a.stress(), preterm2b.stress()]))
            data['norm_m1'].append((preterm1.stress()-min1)/max1 if max1 else np.nan)
            data['norm_m2a'].append((preterm2a.stress()-min2a)/max2a if max2a else np.nan)
            data['norm_m2b'].append((preterm2b.stress()-min2b)/max2b if max2b else np.nan)
            data['norm_mean'].append((np.mean([preterm1.stress(), preterm2a.stress(), preterm2b.stress()])-minmean)/maxmean if maxmean else np.nan)
            data['sidx'].append(i)
            data['sent'].append(sent)
            data['ambig_words'].append(ambig1)
            data['ambig_monosyll'].append(ambig2)
        data['contour'].extend([' '.join(str(x) for x in data['mean'][-(j):])]*j)

    if format_pandas:
        for k, v in data.items():
            data[k] = pd.Series(v)
        df=pd.DataFrame(data, columns=['widx', 'norm_widx', 'word', 'seg', 'lexstress',
                                            'nseg', 'nsyll', 'nstress',
                                            'pos', 'dep',
                                            'm1', 'm2a', 'm2b', 'mean',
                                            'norm_m1', 'norm_m2a', 'norm_m2b', 'norm_mean',
                                            'sidx', 'sent', 'ambig_words', 'ambig_monosyll',
                                            'contour'])
        return df

    keys=list(data.keys())
    old=[]
    num_rows=len(data[keys[0]])
    for i_row in range(num_rows):
        dx={}
        for k in keys:
            dx[k]=data[k][i_row]
        old+=[dx]

    return old