#!/usr/bin/env python # -*- coding: utf-8 -*-
#8/31/15: 1200-1600
#9/06/15: 1330-1945
#9/08/15: 1130-1430
#9/15 3:30-6:30 <- taken care of?
#11/25 eh, like 30 mins

import os
from collections import defaultdict
import pickle as pkl
import numpy as np
#import pandas as pd
#import matplotlib.pyplot as plt
import codecs
import nltk
from nltk import compat
from nltk.tree import Tree
import nltk.data
from .deptree import DependencyTree#, DependencyTreeParser
import re,time


DIR_ROOT = '.'
sylcmu = {}

INFO_DO_NOT_STORE = ['contour','sent','nsyll','nseg','seg','nstress','word']



#***********************************************************************
# Metrical Tree class
class MetricalTree(DependencyTree):
    """"""

    _unstressedWords = ('it',)
    _unstressedTags  = ('CC', 'PRP$', 'TO', 'UH', 'DT')
    _unstressedDeps  = ('det', 'expl', 'cc', 'mark')
    _ambiguousWords = ('this', 'that', 'these', 'those')
    _ambiguousTags  = ('MD', 'IN', 'PRP', 'WP$', 'PDT', 'WDT', 'WP', 'WRB')
    _ambiguousDeps  = ('cop', 'neg', 'aux', 'auxpass')
    _stressedWords = tuple()

    #=====================================================================
    # Initialize
    def __init__(self, node, children, dep=None, lstress=0, pstress=np.nan, stress=np.nan):
        """"""

        self._lstress = lstress
        self._pstress = pstress
        self._stress = stress
        super(MetricalTree, self).__init__(node, children, dep)
        self.set_label()
        if self._preterm:
            if self[0].lower() in sylcmu:
                syll_info = sylcmu[self[0].lower()]
                self._seg = syll_info[0]
                self._nsyll = len(syll_info[1])
                self._nstress = len([x for x in syll_info[1] if x[1] in ('P', 'S')])
            else:
                self._seg = None
                self._nsyll = np.nan
                self._nstress = np.nan

    #=====================================================================
    # Get the lexical stress of the node
    def lstress(self):
        """"""

        return self._lstress

    #=====================================================================
    # Get the phrasal stress of the node
    def pstress(self):
        """"""

        return self._pstress

    #=====================================================================
    # Get the stress of the node
    def stress(self):
        """"""

        return self._stress

    #=====================================================================
    # Get the segments
    def seg(self):
        """"""

        return self._seg if self._seg is not None else []

    #=====================================================================
    # Get the number of segments
    def nseg(self):
        """"""

        return len(self._seg) if self._seg is not None else np.nan

    #=====================================================================
    # Get the number of syllables
    def nsyll(self):
        """"""

        return self._nsyll

    #=====================================================================
    # Get the number of stresses
    def nstress(self):
        """"""

        return self._nstress

    #=====================================================================
    # Get the lexical stress of the leaf nodes
    def lstresses(self, leaves=True):
        """"""

        for preterminal in self.preterminals(leaves=True):
            if leaves:
                yield (preterminal._lstress, preterminal[0])
            else:
                yield preterminal._lstress

    #=====================================================================
    # Get the phrasal stress of the leaf nodes
    def pstresses(self, leaves=True):
        """"""

        for preterminal in self.preterminals(leaves=True):
            if leaves:
                yield (preterminal._pstress, preterminal[0])
            else:
                yield preterminal._pstress

    #=====================================================================
    # Get the lexical stress of the leaf nodes
    def stresses(self, leaves=True, arto=False):
        """"""

        for preterminal in self.preterminals(leaves=True):
            if leaves:
                if arto:
                    if preterminal._stress is None:
                        yield (None, preterminal[0])
                    elif preterminal._lstress == -1:
                        yield (0, preterminal[0])
                    else:
                        yield (-(preterminal._stress-1), preterminal[0])
                else:
                    yield (preterminal._stress, preterminal[0])
            else:
                if arto:
                    if preterminal._stress is None:
                        yield None
                    elif preterminal._lstress == -1:
                        yield 0
                    else:
                        yield -(preterminal._stress-1)
                else:
                    yield preterminal._stress

    #=====================================================================
    # Get the number of syllables of the leaf nodes
    def nsylls(self, leaves=True):
        """"""

        for preterminal in self.preterminals(leaves=True):
            if leaves:
                yield (preterminal._nsyll, preterminal[0])
            else:
                yield preterminal._nsyll

    #=====================================================================
    # Set the lexical stress of the node
    def set_lstress(self):
        """"""

        if self._preterm:
            if self[0].lower() in super(MetricalTree, self)._contractables:
                self._lstress = np.nan
            elif self._cat in super(MetricalTree, self)._punctTags:
                self._lstress = np.nan

            elif self[0].lower() in MetricalTree._unstressedWords:
                self._lstress = -1
            elif self[0].lower() in MetricalTree._ambiguousWords:
                self._lstress = -.5
            elif self[0].lower() in MetricalTree._stressedWords:
                self._lstress = 0

            elif self._cat in MetricalTree._unstressedTags:
                self._lstress = -1
            elif self._cat in MetricalTree._ambiguousTags:
                self._lstress = -.5

            elif self._dep in MetricalTree._unstressedDeps:
                self._lstress = -1
            elif self._dep in MetricalTree._ambiguousDeps:
                self._lstress = -.5

            else:
                self._lstress = 0

            if self[0].lower() == 'that' and (self._cat == 'DT' or self._dep == 'det'):
                self._lstress = -.5
        else:
            for child in self:
                child.set_lstress()
        self.set_label()

    #=====================================================================
    # Set the phrasal stress of the tree
    def set_pstress(self):
        """"""

        # Basis
        if self._preterm:
            try: assert self._lstress != -.5
            except: raise ValueError('The tree must be disambiguated before assigning phrasal stress')
            self._pstress = self._lstress
        else:
            # Recurse
            for child in self:
                child.set_pstress()
            assigned = False
            # Noun compounds (look for sequences of N*)
            if self._cat == 'NP':
                skipIdx = None
                i = len(self)
                for child in self[::-1]:
                    i -= 1
                    if child._cat.startswith('NN'):
                        if not assigned and skipIdx is None:
                            skipIdx = i
                            child._pstress = -1
                            child.set_label()
                        elif not assigned:
                            child._pstress = 0
                            child.set_label()
                            assigned = True
                        else:
                            child._pstress = -1
                            child.set_label()
                    elif assigned:
                        child._pstress = -1
                        child.set_label()
                    else:
                        if not assigned and skipIdx is not None:
                            self[skipIdx]._pstress = 0
                            self[skipIdx].set_label()
                            assigned = True
                            child._pstress = -1
                            child.set_label()
                        else:
                            break
                if not assigned and skipIdx is not None:
                    self[skipIdx]._pstress = 0
                    self[skipIdx].set_label()
                    assigned = True
            # Everything else
            if not assigned:
                for child in self[::-1]:
                    if not assigned and child._pstress == 0:
                        assigned = True
                    elif not np.isnan(child._pstress):
                        child._pstress = -1
                        child.set_label()
            if not assigned:
                self._pstress = -1
            else:
                self._pstress = 0
        self.set_label()

    #=====================================================================
    # Set the total of the tree
    def set_stress(self, stress=0):
        """"""

        self._stress = self._lstress + self._pstress + stress
        if not self._preterm:
            for child in self:
                child.set_stress(self._stress)
        self.set_label()

    #=====================================================================
    # Reset the label of the node (cat < dep < lstress < pstress < stress
    def set_label(self):
        """"""

        if self._stress is not np.nan:
            self._label = '%s/%s' % (self._cat, self._stress)
        elif self._pstress is not np.nan:
            self._label = '%s/%s' % (self._cat, self._pstress)
        elif self._lstress is not np.nan:
            self._label = '%s/%s' % (self._cat, self._lstress)
        elif self._dep is not None:
            self._label = '%s/%s' % (self._cat, self._dep)
        else:
            self._label = '%s' % self._cat

    #=====================================================================
    # Convert between different subtypes of Metrical Trees
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
            if isinstance(tree, MetricalTree):
                return cls(tree._cat, children, tree._dep, tree._lstress)
            elif isinstance(tree, DependencyTree):
                return cls(tree._cat, children, tree._dep)
            else:
                return cls(tree._label, children)
        else:
            return tree

    #=====================================================================
    # Approximate the number of ambiguous parses
    def ambiguity(self, stress_polysyll=False):
        """"""

        nambig = 0
        for preterminal in self.preterminals():
            if preterminal.lstress() == -.5:
                if not stress_polysyll or (preterminal.nsyll() == 1):
                    nambig += 1
        return nambig

    #=====================================================================
    # Generate all possible trees
    # Syll=True sets all polysyllabic words to stressed
    def ambiguate(self, stress_polysyll=False):
        """"""

        if self._preterm:
            if self._lstress != -.5:
                return [self.copy()]
            else:
                alts = []
                if not stress_polysyll or self._nsyll == 1:
                    self._lstress = -1
                    alts.append(self.copy())
                self._lstress = 0
                alts.append(self.copy())
                self._lstress = -.5
                return alts
        else:
            alts = [[]]
            for child in self:
                child_alts = child.disambiguate(syll)
                for i in range(len(alts)):
                    alt = alts.pop(0)
                    for child_alt in child_alts:
                        alts.append(alt + [child_alt])
            return [MetricalTree(self._cat, alt, self._dep) for alt in alts]

    #=====================================================================
    # Disambiguate a tree with the maximal stressed pattern
    def max_stress_disambiguate(self):
        """"""

        if self._preterm:
            if self._lstress != -.5:
                return [self.copy()]
            else:
                alts = []
                self._lstress = 0
                alts.append(self.copy())
                self._lstress = -.5
                return alts
        else:
            alts = [[]]
            for child in self:
                child_alts = child.max_stress_disambiguate()
                for i in range(len(alts)):
                    alt = alts.pop(0)
                    for child_alt in child_alts:
                        alts.append(alt + [child_alt])
            return [MetricalTree(self._cat, alt, self._dep) for alt in alts]

    #=====================================================================
    # Disambiguate a tree with the minimal stressed pattern
    def min_stress_disambiguate(self, stress_polysyll=False):
        """"""

        if self._preterm:
            if self._lstress != -.5:
                return [self.copy()]
            else:
                alts = []
                if not stress_polysyll or self._nsyll == 1:
                    self._lstress = -1
                else:
                    self._lstress = 0

                alts.append(self.copy())
                self._lstress = -.5
                return alts
        else:
            alts = [[]]
            for child in self:
                child_alts = child.min_stress_disambiguate(stress_polysyll)
                for i in range(len(alts)):
                    alt = alts.pop(0)
                    for child_alt in child_alts:
                        alts.append(alt + [child_alt])
            return [MetricalTree(self._cat, alt, self._dep) for alt in alts]

    #=====================================================================
    # Copy the tree
    def copy(self, deep=False):
        """"""

        if not deep:
            return type(self)(self._cat, self, dep=self._dep, lstress=self._lstress)
        else:
            return type(self).convert(self)
