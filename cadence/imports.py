

# sys imports
import os,sys
sys.path.append('/home/ryan/github/prosodic')
import warnings
warnings.filterwarnings('ignore')
import prosodic as p

from tqdm import tqdm
import pandas as pd,numpy as np,random,json,pickle,shutil
from collections import defaultdict,Counter
import subprocess,multiprocessing as mp
mp.set_start_method('fork')
from pprint import pprint
from itertools import product
pd.options.display.max_columns=False
import re,nltk
from sqlitedict import SqliteDict
import logging
logging.Logger.manager.loggerDict['sqlitedict'].disabled=True

from parmapper import parmap
from functools import partial


# constants
ENGINE_PROSODIC='prosodic'
ENGINE_CADENCE='cadence'
ENGINE=ENGINE_PROSODIC

MIN_WORDS_IN_PHRASE=2
DEFAULT_LANG='en'
PATH_HERE=os.path.abspath(os.path.dirname(__file__))
PATH_CODE=PATH_HERE
PATH_REPO=os.path.abspath(os.path.join(PATH_CODE,'..'))
PATH_HOME=os.path.join(os.path.expanduser('~'),'.cadence')
PATH_DATA=os.path.join(PATH_HOME,'data')
# PATH_DATA=os.path.join(PATH_REPO,'data')
DATA_URL='https://www.dropbox.com/s/fywmqrlpemjf43c/data_cadence.zip?dl=1'


PATH_NOTEBOOKS=os.path.join(PATH_REPO,'notebooks')
PATH_IPA_FEATS=os.path.join(PATH_DATA,'data.feats.ipa.csv')
INCL_ALT=True
DEFAULT_NUM_PROC=1
#mp.cpu_count()//2# - 1

KEEP_BEST=1
SBY=csby=['combo_i','word_i','syll_i']
PARSERANKCOL='parse_rank'

LINEKEY=[
    'stanza_i',
    'line_i',
    'line_str',
    'linepart_i',#'linepart_str',
    'linepart_str',
    'linepart_end_str',
    
    
    PARSERANKCOL,
    #'parse_str',
    'is_troch',
    'parse_i',
    'parse',
    # 'combo_stress',
    'parse_str',

    
    'combo_stress',
    'combo_ipa',
    'combo_i',
#     'combo_i','combo_stress','combo_ipa',
    'parse_is_bounded','parse_bounded_by',
    'parse_pos_i','parse_pos',
    'word_i','word_str','word_ipa_i','word_ipa',
    'syll_i','combo_syll_i','syll_str','syll_ipa','syll_stress','syll_weight',
    'parse_syll_i','parse_syll',
]
PARSELINEKEY = LINEKEY[:LINEKEY.index('parse_pos_i')]
PARSESYLLKEY=LINEKEY
TOTALCOL='*total'

DEFAULT_CONSTRAINTS = {
    '*w/peak',
    '*w/stressed',
    # '*s/unstressed',
    '*f-res',
    '*w-res'
}

NUM_BOUNDED_TO_STORE = 10

constraint_names_in_prosodic = {
    '*f-res':'footmin-f-resolution',
    '*s/unstressed':'stress.s=>-u',
    '*w-res':'footmin-w-resolution',
    '*w/peak':'strength.w=>-p',
    '*w/stressed':'stress.w=>-p',
    '*s/trough':'strength.s=>-u',
}
constraint_names_from_prosodic = dict((v,k) for k,v in constraint_names_in_prosodic.items())


txt="""In Xanadu did Kubla Khan
A stately pleasure-dome decree:
Where Alph, the sacred river, ran
Through caverns measureless to man
   Down to a sunless sea.
"""
line=txt.split('\n')[0]

APPLY_POSTHOC_CONSTRAINTS=False


# local imports
from .tools import *
from .langs import *
from .constraints import *
from .parsers import *
from .cadence import *


# check
check_basic_config()