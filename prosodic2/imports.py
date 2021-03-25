

# sys imports
import os,sys
from tqdm import tqdm
import pandas as pd,numpy as np,random,json,pickle
from collections import defaultdict,Counter
import subprocess

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

# local imports
from .tools import *
from .langs import *
from .constraints import *
from .parsers import *
from .prosodic2 import *

