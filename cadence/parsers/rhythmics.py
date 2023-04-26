from ..imports import *

import networkx as nx
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import matplotlib.pyplot as plt


## Am I a lexical or a phrasal category?
def is_leaf(root):
    return root.label != root.label.upper()

def is_lexical(root):
    if is_leaf(root): return True
    if root.label in {'ROOT','S','VP'}: return False
    if root.children and is_leaf(root.children[0]): return True
    return False



def NSR(root):
    # Assign [1 stress] to the rightmost vowel bearing [1 stress]
    words = root.leaf_labels()
    sylls_df = Text(' '.join(words)).sylls()

    sylls_df['prom_NSR'] = [
        
    ]
    return sylls_df

def CSR(root):
    # "skip over the rightmost word, and then assign [1 stress] to the right-most remaining[1 stress] vowel; 
    # if there is no [1 stress] to the left of the rightmost word, then try again without skipping the word."
    pass



def draw_graph(G):
    plt.rcParams["figure.figsize"] = [10.,5.]
    pos =graphviz_layout(G, prog='dot')
    
    node_labels=nx.get_node_attributes(G,'label')
    nx.draw(G,pos, with_labels=True,labels=node_labels, width=2, node_size=1000, node_color="orange",alpha=1.0)
    lbls = nx.get_edge_attributes(G,'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels = lbls)
    plt.show()




class BinaryTree:
    def __init__(
            self,
            label=None, 
            left=None, 
            right=None,
            left_prom=None):
        self.label = label
        self.left = None
        self.right = None
        self.left_prom = left_prom

        self.set_left(left)
        self.set_right(right)

    def _repr_html_(self):
        return self.draw()

    def set_left(self, left, prom=None):
        if left:
            self.left = BinaryTree(left) if type(left)!=BinaryTree else left
        if prom is not None: self.left_prom = prom
    def set_right(self, right, prom = None):
        if right:
            self.right = BinaryTree(right) if type(right)!=BinaryTree else right
        if prom is not None: self.left_prom = not prom

    @property
    def left_ws(self): return ('' if self.left_prom is None else ('s' if self.left_prom else 'w'))
    @property
    def right_ws(self): return ('' if self.left_prom is None else ('s' if not self.left_prom else 'w'))

    def __repr__(self):
        return f'({self.left}-L-{self.label}-R-{self.right})' if self.left or self.right else f'{self.label}'

    def root_graph(self, G=None):
        if G is None: G=nx.DiGraph()
        node = f'{G.order() + 1} {self.label}'
        # node = G.order() + 1
        G.add_node(node, label=self.label)
        
        if self.left: 
            left_node, G = self.left.root_graph(G=G)
            G.add_edge(node, left_node, label=self.left_ws)

        if self.right: 
            right_node, G = self.right.root_graph(G=G)
            G.add_edge(node, right_node, label=self.right_ws)

        return node, G
    
    def graph(self):
        n, G = self.root_graph()
        return G

    def draw(self):
        return draw_graph(self.graph())
    
    def ascii(self, size=15, **kwargs):
        from structout import gprint
        G = self.graph()
        pos=graphviz_layout(G, prog='dot')
        for n in pos: pos[n] = (pos[n][0], -pos[n][1])
        gprint(G,pos=pos,size=size,**kwargs)



class DivorcedParent:
    def __init__(self, label, children):
        self.label = label+'x'
        self.children = children

def prom_tree(root):
    if not root: return
    btree = BinaryTree(root.label)
    numchild = len(root.children)
    a,b = None,None
    if numchild==1:
        a = root.children[0]
    elif numchild > 1:
        print(root.label, is_lexical(root), root)
        if is_lexical(root):
            a,b = root.children[0], DivorcedParent(root.label, root.children[1:]) if len(root.children)>2 else root.children[1]
            btree.left_prom = True
        else:
            a,b = DivorcedParent(root.label, root.children[:-1]) if len(root.children)>2 else root.children[0], root.children[-1]
            btree.left_prom = False

    btree.set_left(prom_tree(a))
    btree.set_right(prom_tree(b))

    return btree
