

# sys imports
import os,sys
from tqdm import tqdm
import pandas as pd,numpy as np,random,json,pickle
from collections import defaultdict,Counter
import subprocess,multiprocessing as mp
from pprint import pprint
from itertools import product
pd.options.display.max_columns=False

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
DEFAULT_NUM_PROC=mp.cpu_count() - 1
KEEP_BEST=1
SBY=csby=['combo_i','word_i','syll_i']
PARSERANKCOL='parse_rank'

LINEKEY=[
    'stanza_i',
    'line_i','line_str',
    PARSERANKCOL,
    'combo_i','combo_stress','combo_ipa',
    'parse_i','parse','parse_str',
    'parse_pos_i','parse_pos',
    'word_i','word_str','word_ipa_i','word_ipa',
    'syll_i','combo_syll_i','syll_str','syll_ipa','syll_stress',
    'parse_syll_i','parse_syll',
]
PARSELINEKEY = LINEKEY[:LINEKEY.index('parse_pos_i')]
PARSESYLLKEY=LINEKEY
TOTALCOL='*total'



# local imports
from .tools import *
from .langs import *
from .constraints import *
from .parsers import *
from .cadence import *

