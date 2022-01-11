

# sys imports
import os,sys
sys.path.append('/home/ryan/github/prosodic')
import warnings
warnings.filterwarnings('ignore')
import prosodic as p
from string import punctuation

from tqdm import tqdm
import pandas as pd,numpy as np,random,json,pickle,shutil
from collections import defaultdict,Counter
import subprocess,multiprocessing as mp
# mp.set_start_method('spawn')
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
import diskcache as dc
import requests

# constants
ENGINE_PROSODIC='prosodic'
ENGINE_CADENCE='cadence'
ENGINE=ENGINE_PROSODIC
DEFAULT_PARSE_MAXSEC=30
DEFAULT_LINE_LIM=None
DEFAULT_PROCESSORS={'tokenize':'combined'}

MIN_WORDS_IN_PHRASE=2
MAX_WORDS_IN_PHRASE=15
SEPS_PHRASE=set(',:;–—()[].!?"“”’‘')
SEP_STANZA='\n\n'
SEP_PARA='\n\n'
SEP_LINE='\n'
DEFAULT_LANG='en'
PATH_HERE=os.path.abspath(os.path.dirname(__file__))
PATH_CODE=PATH_HERE
PATH_REPO=os.path.abspath(os.path.join(PATH_CODE,'..'))
PATH_HOME=os.path.join(os.path.expanduser('~'),'cadence_data')
PATH_DATA=os.path.join(PATH_HOME,'data')
PATH_TXTS=os.path.join(PATH_HOME,'txts')
if not os.path.exists(PATH_DATA): os.makedirs(PATH_DATA)
if not os.path.exists(PATH_TXTS): os.makedirs(PATH_TXTS)
PATH_DB_SYLLABIFY=os.path.join(PATH_DATA,'syllabified.dc')
# PATH_DATA=os.path.join(PATH_REPO,'data')
DATA_URL='https://www.dropbox.com/s/fywmqrlpemjf43c/data_cadence.zip?dl=1'


PATH_NOTEBOOKS=os.path.join(PATH_REPO,'notebooks')
PATH_IPA_FEATS=os.path.join(PATH_DATA,'data.feats.ipa.csv')
PATH_DB_SCAN=os.path.join(PATH_DATA,'db_scan.dc')
PATH_DB_PARSE=os.path.join(PATH_DATA,'db_parse.dc')
PATH_DB=os.path.join(PATH_DATA,'db.dc')
DBSEP='____'

INCL_ALT=True
DEFAULT_NUM_PROC=1
#mp.cpu_count()//2# - 1

DEFAULT_METER='default_english'
COLS_JOINER=['para_i','sent_i','word_i']

KEEP_BEST=1
SBY=csby=['combo_i','word_i','syll_i']
PARSERANKCOL='parse_rank'

LINEKEY=[
    'id_author',
    'id',
    'para_i','stanza_i',
    'para_start_char','para_end_char',
    'sent_i'] + [
        f'sent_depth{i}' for i in range(1,10)
    ] + [
        # 'word_i',
    'sentpart_i',
    'linepart_i','linepart_str','linepart_end_str',

    'line_i','line_str',
    
    PARSERANKCOL,'is_troch','parse_i','parse','parse_str',

    
    'combo_stress','combo_ipa','combo_i',
    
    'parse_is_bounded','parse_bounded_by',
    'parse_pos_i','parse_pos',
    
    'word_i',
    'word_pref','word_str','word_tok','word_ipa_i','word_ipa',
    'word_lemma','word_upos','word_xpos','word_deprel','word_head',
    'word_constituency',
    'word_start_char','word_end_char',
    
    'syll_i','combo_syll_i','syll_str','syll_ipa','syll_stress','syll_weight',
    
    'parse_syll_i','parse_syll',


]
PARSELINEKEY = LINEKEY[:LINEKEY.index('parse_pos_i')]
PARSESYLLKEY=LINEKEY
TOTALCOL='*total'

DEFAULT_CONSTRAINTS = {
    '*w/peak',
    '*w/stressed',
    '*s/unstressed',
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
WORD_TOKDF={}


URLS=dict(
    prideprej='https://www.gutenberg.org/files/1342/1342-0.txt'
)

NLP_PARSE_POSTAG=True
NLP_PARSE_TOKENIZE=True
NLP_PARSE_CONSTITUENCY=True
NLP_PARSE_DEPPARSE=True
SHUFFLE_PARAS=False
LIM_PARAS=None

joyce_path = os.path.join(PATH_TXTS,'joyce_oxen.txt')
joyce_s = s = 'Stately, plump Buck Mulligan came from the stairhead, bearing a bowl of lather on which a mirror and a razor lay crossed.'
joyce_para="""
Valuing himself not a little upon his elegance, being indeed a proper man of his person, this talkative now applied himself to his dress with animadversions of some heat upon the sudden whimsy of the atmospherics while the company lavished their encomiums upon the project he had advanced. The young gentleman, his friend, overjoyed as he was at a passage that had befallen him, could not forbear to tell it his nearest neighbour. Mr Mulligan, now perceiving the table, asked for whom were those loaves and fishes and, seeing the stranger, he made him a civil 290bow and said, Pray, sir, was you in need of any professional assistance we could give? Who, upon his offer, thanked him very heartily, though preserving his proper distance, and replied that he was come there about a lady, now an inmate of Horne's house, that was in an interesting condition, poor lady, from woman's woe (and here he fetched a deep sigh) to know if her happiness had yet taken place. Mr Dixon, to turn the table, took on to ask of Mr Mulligan himself whether his incipient ventripotence, upon which he rallied him, betokened an ovoblastic gestation in the prostatic utricle or male womb or was due, as with the noted physician, 403Mr Austin Meldon, to a wolf in the stomach. For answer Mr Mulligan, in a gale of laughter at his 384smalls, smote himself bravely below the diaphragm, exclaiming with an admirable droll mimic of Mother Grogan (the most excellent creature of her sex though 'tis pity she's a trollop): There's a belly that never bore a bastard. This was so happy a conceit that it renewed the storms of mirth and threw the whole room into the most violent agitations of delight. The spry rattle had run on in the same vein of mimicry but for some larum in the antechamber.
"""


# local imports
from .tools import *
from .langs import *
from .constraints import *
from .parsers import *
from .cadence import *


# check
check_basic_config()

