

# sys imports
import os,sys
from tqdm import tqdm
import pandas as pd,numpy as np,random,json,pickle
from collections import defaultdict,Counter
import subprocess
from pprint import pprint

# constants
MIN_WORDS_IN_PHRASE=2
DEFAULT_LANG='en'
PATH_HERE=os.path.abspath(os.path.dirname(__file__))
PATH_CODE=PATH_HERE
PATH_REPO=os.path.abspath(os.path.join(PATH_CODE,'..'))
PATH_DATA=os.path.join(PATH_REPO,'data')
PATH_NOTEBOOKS=os.path.join(PATH_REPO,'notebooks')
PATH_IPA_FEATS=os.path.join(PATH_DATA,'data.feats.ipa.csv')
INCL_ALT=True
DEFAULT_NUM_PROC=1
KEEP_BEST=1
SBY=csby=['combo_i','word_i','syll_i']
LINEKEY=[
    'stanza_i','line_i',
    'line','line_str',
    'line_parse','line_stress','line_ipa',
    'stress',
    'parse_combo_i',
    'parse_i',
    'parse',
    'combo_i','combo_ii',
    
    
    'word_i','word_str','word_ipa_i','word_ipa',
    'parse_ii',
    'syll_i','syll_str','syll_ipa',    
    'syll_parse',
    'line_ii',
    'window_ii',
    'mpos_parse',
    'window_key','window_i','window_ii',
]

PARSELINEKEY=[
'stanza_i','line_i',
'combo_parse_i',
'line_str',
'line_ipa',
'meter',
'stress'
]




# local imports
from .tools import *
from .langs import *
from .constraints import *
from .parsers import *
from .prosodic2 import *

