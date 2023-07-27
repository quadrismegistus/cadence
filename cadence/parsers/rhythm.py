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
    #pos =graphviz_layout(G, prog='dot')
    pos = hierarchy_pos(G)
    
    node_labels=nx.get_node_attributes(G,'label')
    node_ws=[d['obj'].ws for n,d in G.nodes(data=True)]

    def to_color(lbl):
        if lbl=='w': return 'lightblue'
        if lbl=='s': return 'orange'
        return 'silver'
    
    node_colors = [to_color(x) for x in node_ws]
    edge_weights = [2 if d['prom'] else 1 for a,b,d in G.edges(data=True)]
    edge_colors = [to_color(d['label']) for a,b,d in G.edges(data=True)]

    nx.draw(
        G,
        pos, 
        with_labels=True,
        labels=node_labels, 
        width=edge_weights, 
        edge_color=edge_colors,
        node_size=1000, 
        node_color=node_colors,
        alpha=1.0
    )
    
    lbls = nx.get_edge_attributes(G,'label')
    nx.draw_networkx_edge_labels(
        G, 
        pos, 
        edge_labels = lbls,
        font_size = 12
    )
    plt.show()



class BinaryTree:
    def __init__(
            self,
            # label=None,
            root=None,
            left=None, 
            right=None,
            parent=None,
            prom=None):
        self.root = root
        self.label = root.label if root and hasattr(root,'label') else '?'
        self.left = None
        self.right = None
        self.parent = parent
        self.prom = prom

        self.set_left(left)
        self.set_right(right)

    def _repr_html_(self):
        return self.draw()
    
    def set_child(self, obj, prom=None):
        if not obj: return
        o=BinaryTree(obj) if type(obj)!=BinaryTree else obj
        o.parent = self
        o.prom = prom
        return o

    def set_left(self, obj, prom=None):
        self.left = self.set_child(obj, prom=prom)
    def set_right(self, obj, prom=None):
        self.right = self.set_child(obj, prom=prom)

    @property
    def ws(self):
        if self.prom is None:
            return ''
        return 's' if self.prom else 'w'
    
    def __repr__(self):
        if self.is_branching():
            return f'({self.left}|{self.label}|{self.right})'
        else:
            return self.label
        # return f'{self.left}'

    def root_graph(self, G=None):
        if G is None: G=nx.DiGraph()
        node = f'{G.order() + 1} {self.label}'
        G.add_node(
            node,
            obj=self,
            label=self.label
        )

        for obj in [self.left, self.right]:
            if obj:
                onode, G = obj.root_graph(G=G)
                G.add_edge(
                    node, 
                    onode,
                    prom=obj.prom,
                    label=obj.ws,
                )

        return node, G
    
    def graph(self):
        self.decide_prom()
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


    def is_phrase(self):
        return self.label in {'VP','ROOT','S'}
    def is_lexical(): passs
    def is_branching(self):
        return bool(self.left) and bool(self.right)
    def is_leaf(self):
        return self.left is None and self.right is None

    def decide_prom(self):
        """
        (8) In a configuration [cA Bc]:

        a. NSR: If C is a phrasal category, B is strong.

        b. CSR: If C is a lexical category, B is strong iff it branches.
        """
        if self.is_branching():
            if self.is_phrase() or self.right.is_branching():
                self.left.prom = False
                self.right.prom = True
            else:
                self.left.prom = True
                self.right.prom = False
        
        if self.left: self.left.decide_prom()
        if self.right: self.right.decide_prom()


    def iter_nodes(self):
        yield self
        if self.left: yield from self.left.iter_nodes()
        if self.right: yield from self.right.iter_nodes()

    def iter_leaves(self):
        for node in self.iter_nodes():
            if node.is_leaf():
                yield node

    def num_leaves(self):
        return len(list(self.iter_leaves()))

    
    def iter_ancestry(self):
        yield self
        if self.parent:
            yield from self.parent.iter_ancestry()

    def get_nested_proms(self, ws=True):
        return [
            obj.ws if ws else obj.prom 
            for obj in self.iter_ancestry() 
            if obj.prom is not None
        ]

    def get_sum_prom(self):
        """
        (12) If a terminalnode t is labelled w, its stress number is equal to the number of nodes that dominate it, plus one. If a terminalnode t is labelled s, its stress number is equal to the number of nodes that dominate the lowest w dominating t, plus one.
        """
        if self.prom is None: self=self.parent
        proms = self.get_nested_proms()
        if self.prom is False:
            return sum(1 for x in proms if x is False) + 1
        
        elif self.prom is True: # if labeled 's'
            for parent in self.iter_ancestry():
                # find lowest w dominating t
                if parent.prom is False:
                    return parent.get_sum_prom()
        
        return 1
        

        





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



def to_binary_tree(root, right_branching=True, is_root=True):
    if not root: return
    btree = BinaryTree(root)
    
    # no children? good enough
    if not root.children:
        return btree
    
    # one child?
    elif len(root.children)==1:
        a=root.children[0]
        b=None
    
    # two?
    elif len(root.children)==2:
        a=root.children[0]
        b=root.children[1]
    
    # three or more?
    # if right branching...
    elif right_branching:
        a=root.children[0]
        b=DivorcedParent(root.label, root.children[1:])
    
    # left branching
    else:
        a=DivorcedParent(root.label, root.children[:-1])
        b=root.children[-1]

    btree.set_left(to_binary_tree(a, is_root=False))
    btree.set_right(to_binary_tree(b, is_root=False))

    if is_root:
        # decide proms..
        btree.decide_prom()

    return btree














def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, leaf_vs_root_factor = 0.5):

    '''
    If the graph is a tree this will return the positions to plot this in a 
    hierarchical layout.
    
    Based on Joel's answer at https://stackoverflow.com/a/29597209/2966723,
    but with some modifications.  

    We include this because it may be useful for plotting transmission trees,
    and there is currently no networkx equivalent (though it may be coming soon).
    
    There are two basic approaches we think of to allocate the horizontal 
    location of a node.  
    
    - Top down: we allocate horizontal space to a node.  Then its ``k`` 
      descendants split up that horizontal space equally.  This tends to result
      in overlapping nodes when some have many descendants.
    - Bottom up: we allocate horizontal space to each leaf node.  A node at a 
      higher level gets the entire space allocated to its descendant leaves.
      Based on this, leaf nodes at higher levels get the same space as leaf
      nodes very deep in the tree.  
      
    We use use both of these approaches simultaneously with ``leaf_vs_root_factor`` 
    determining how much of the horizontal space is based on the bottom up 
    or top down approaches.  ``0`` gives pure bottom up, while 1 gives pure top
    down.   
    
    
    :Arguments: 
    
    **G** the graph (must be a tree)

    **root** the root node of the tree 
    - if the tree is directed and this is not given, the root will be found and used
    - if the tree is directed and this is given, then the positions will be 
      just for the descendants of this node.
    - if the tree is undirected and not given, then a random choice will be used.

    **width** horizontal space allocated for this branch - avoids overlap with other branches

    **vert_gap** gap between levels of hierarchy

    **vert_loc** vertical location of root
    
    **leaf_vs_root_factor**

    xcenter: horizontal location of root
    '''
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, leftmost, width, leafdx = 0.2, vert_gap = 0.2, vert_loc = 0, 
                    xcenter = 0.5, rootpos = None, 
                    leafpos = None, parent = None):
        '''
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        '''

        if rootpos is None:
            rootpos = {root:(xcenter,vert_loc)}
        else:
            rootpos[root] = (xcenter, vert_loc)
        if leafpos is None:
            leafpos = {}
        children = list(G.neighbors(root))
        leaf_count = 0
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)  
        if len(children)!=0:
            rootdx = width/len(children)
            nextx = xcenter - width/2 - rootdx/2
            for child in children:
                nextx += rootdx
                rootpos, leafpos, newleaves = _hierarchy_pos(G,child, leftmost+leaf_count*leafdx, 
                                    width=rootdx, leafdx=leafdx,
                                    vert_gap = vert_gap, vert_loc = vert_loc-vert_gap, 
                                    xcenter=nextx, rootpos=rootpos, leafpos=leafpos, parent = root)
                leaf_count += newleaves

            leftmostchild = min((x for x,y in [leafpos[child] for child in children]))
            rightmostchild = max((x for x,y in [leafpos[child] for child in children]))
            leafpos[root] = ((leftmostchild+rightmostchild)/2, vert_loc)
        else:
            leaf_count = 1
            leafpos[root]  = (leftmost, vert_loc)
#        pos[root] = (leftmost + (leaf_count-1)*dx/2., vert_loc)
#        print(leaf_count)
        return rootpos, leafpos, leaf_count

    xcenter = width/2.
    if isinstance(G, nx.DiGraph):
        leafcount = len([node for node in nx.descendants(G, root) if G.out_degree(node)==0])
    elif isinstance(G, nx.Graph):
        leafcount = len([node for node in nx.node_connected_component(G, root) if G.degree(node)==1 and node != root])
    rootpos, leafpos, leaf_count = _hierarchy_pos(G, root, 0, width, 
                                                    leafdx=width*1./leafcount, 
                                                    vert_gap=vert_gap, 
                                                    vert_loc = vert_loc, 
                                                    xcenter = xcenter)
    pos = {}
    for node in rootpos:
        pos[node] = (leaf_vs_root_factor*leafpos[node][0] + (1-leaf_vs_root_factor)*rootpos[node][0], leafpos[node][1]) 
#    pos = {node:(leaf_vs_root_factor*x1+(1-leaf_vs_root_factor)*x2, y1) for ((x1,y1), (x2,y2)) in (leafpos[node], rootpos[node]) for node in rootpos}
    xmax = max(x for x,y in pos.values())
    for node in pos:
        pos[node]= (pos[node][0]*width/xmax, pos[node][1])
    return pos