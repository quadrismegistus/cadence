#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Natural Language Toolkit: Updated interface to the Stanford Parser
#
# Copyright (C) 2015 Tim Dozat
# Author: Tim Dozat <tdozat@stanford.edu>
# Author of the Stanford Parser nltk code: Steven Xu <xxu@student.unimelb.edu.au>
#
# For license information, see LICENSE.TXT




import tempfile
import os
import re
from subprocess import PIPE

import nltk
import nltk.data
from nltk import compat
from nltk import Tree
from nltk.internals import find_jar, find_jar_iter, config_java, java, _java_options

from nltk.parse.api import ParserI

_stanford_url = 'http://nlp.stanford.edu/software/lex-parser.shtml'

#***********************************************************************
# Dependency-augmented syntactic tree class
class DependencyTree(Tree):
    """"""

    _contractables = ("m", "s", "ll", "d", "nt", "re", "ve", "'m", "'s", "'ll", "'d", "n't", "'re", "'ve")
    _punctTags = ('.', ',', ':')

    #=====================================================================
    # Initialize
    def __init__(self, node, children=None, dep=None):
        """"""

        self._cat = node
        self._dep = dep
        self._preterm = False
        self._label = None
        super(DependencyTree, self).__init__(node, children)
        if len(self) == 1 and isinstance(self[0], str):
            self._preterm = True
        self.set_label()

    #=====================================================================
    # Get the preterminal value of the node
    def preterminal(self):
        """"""

        return self._preterm

    #=====================================================================
    # Get the categorial value of the node
    def category(self):
        """"""

        return self._cat

    #=====================================================================
    # Get the dependency label of the node
    def dependency(self):
        """"""

        return self._dep

    #=====================================================================
    # Get the dependency labels of the leaf nodes
    def preterminals(self, leaves=True):
        """"""

        if self._preterm:
            if leaves:
                yield self
            else:
                yield self._label
        else:
            for child in self:
                for preterminal in child.preterminals(leaves=leaves):
                    yield preterminal

    #=====================================================================
    # Get the category labels of the leaf nodes
    def categories(self, leaves=True):
        """"""

        for preterminal in self.preterminals(leaves=True):
            if leaves:
                yield (preterminal._cat, preterminal[0])
            else:
                yield preterminal._cat

    #=====================================================================
    # Get the dependency labels of the leaf nodes
    def dependencies(self, leaves=True):
        """"""

        for preterminal in self.preterminals(leaves=True):
            if leaves:
                yield (preterminal._dep, preterminal[0])
            else:
                yield preterminal._dep

    #=====================================================================
    # Reset the label of the node
    def set_label(self):
        """"""

        if self._dep is None:
            self._label = self._cat
        else:
            self._label = '%s/%s' % (self._cat, self._dep)

    #=====================================================================
    # Set the category of the node
    def set_category(self, cat):
        """"""

        self._cat = cat
        self.set_label()

    #=====================================================================
    # Set the dependency of this node
    def set_dep(self, dep):
        """"""

        self._dep = dep
        self.set_label()

    #=====================================================================
    # Set the dependency labels of all the leaf nodes
    def set_deps(self, deps):
        """"""

        preterminals = self.preterminals()
        for preterminal in preterminals:
            if re.match('\w', preterminal._cat[0]):
                preterminal.set_dep(deps.pop(0))

    #=====================================================================
    # Create a list of tuples from the preterminals
    def to_tuples(self):
        """"""

        for preterminal in self.preterminals():
            yield (preterminal[0], preterminal.category(), preterminal.dependency())

    #=====================================================================
    # Get the last preterminal
    def _get_last_preterm(self):
        """"""

        if self._preterm:
            return self
        else:
            return self[-1]._get_last_preterm()

    #=====================================================================
    # Pop the first contractables
    def _pop_first_contractable(self):
        """"""

        if self._preterm:
            if self[0] in _contractables:
                return self
            else:
                return None
        else:
            first_contractable = self[0]._pop_first_contractable()
            if self[0] == first_contractable or len(self[0]) == 0:
                self.children.pop(0)
                self.pop(0)
            return first_contractable

    #=====================================================================
    # Merge contractables
    def contract(self):
        """"""

        for child in self:
            if isinstance(child, DependencyTree):
                child.contract()
        i = len(self) - 2
        while i >= 0:
            child = self[i]
            last_preterm = child._get_last_preterm()
            j = i + 1
            while j < len(self):
                next_child = self[j]
                first_contractable = next_child._pop_first_contractable()
                if first_contractable is not None:
                    # Merge their cats/leaves
                    last_preterm._cat += '+'+first_contractable.category()
                    last_preterm[0] += first_goeswith[0]
                    last_preterm.children[0] += first_goeswith.children[0]
                    # Disown empty children
                    if len(next_child) == 0:
                        self.pop(j)
                    else:
                        break
                else:
                    break
            i -= 1

    #=====================================================================
    # Basically, read the output of the stanford parser
    @classmethod
    def fromstring(cls, s):
        """"""

        cTree, dGraph = s.split('\n\n')
        dTree = Tree.fromstring(cTree)
        dTree = DependencyTree.convert(dTree)
        deps = []
        dGraph = dGraph.split('\n')
        lastWord = ''
        for dep in dGraph:
            try:
                dep, thisWord = re.match('(.+?)\(.*?, (.*?)\)', dep).groups()
                if thisWord != lastWord:
                    deps.append(dep)
                    lastWord = thisWord
            except:
                print('')
        dTree.set_deps(deps)
        return dTree

    #=====================================================================
    # Convert between different subtypes of Dependency Trees
    @classmethod
    def convert(cls, tree):
        """
        Convert a tree between different subtypes of Tree.  ``cls`` determines
        which class will be used to encode the new tree.

        :type tree: Tree
        :param tree: The tree that should be converted.
        :return: The new Tree.
        """

        if isinstance(tree, Tree):
            children = [cls.convert(child) for child in tree]
            if isinstance(tree, DependencyTree):
                return cls(tree._cat, children, tree._dep)
            else:
                return cls(tree._label, children)
        else:
            return tree

    #=====================================================================
    # Copy the tree
    def copy(self, deep=False):
        """"""

        if not deep:
            return type(self)(self._cat, self, dep=self._dep)
        else:
            return type(self).convert(self)
