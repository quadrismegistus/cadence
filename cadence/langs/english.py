from ..imports import *
from .lexconvert import convert as lexconvert
import nltk





Pyphen = None

# lang specific constants
PATH_LANG_DATA=os.path.join(PATH_DATA,'en')
CMU_DICT_FN=os.path.join(PATH_LANG_DATA,'cmudict.txt')
CMU_DICT={}
CACHE_DICT_FN=os.path.join(PATH_LANG_DATA,'tts-cache.txt')
CACHE_DICT_F=None
CACHE=defaultdict(list)
ORTH_CACHE=defaultdict(list)
CONTRACTIONS={"n't","'ve","'ll","'m","'d","'s","'m","'re"}
SPECIALD={}

def get_special_cases():
    global SPECIALD
    
    if not SPECIALD:

        ufn=os.path.join(PATH_LANG_DATA,'unstressed.txt')
        if os.path.exists(ufn):
            with open(ufn) as f:
                SPECIALD['unstressed']={w.strip().lower() for w in f.read().strip().split()}

        ufn=os.path.join(PATH_LANG_DATA,'maybestressed.txt')
        if os.path.exists(ufn):
            with open(ufn) as f:
                SPECIALD['maybestressed']={w.strip().lower() for w in f.read().strip().split()}

        import nltk
        #SPECIALD['functionwords']=set(nltk.corpus.stopwords.words('english'))
        SPECIALD['functionwords']=SPECIALD['unstressed']
        SPECIALD['functionwords']|=SPECIALD['maybestressed']

    return SPECIALD



"""
The only necessary functions
"""

def scan(line,incl_alt=True,**y):
    o=[
        {
            'word_i':word_i+1,
            **word_dx
        } for word_i,word in enumerate(tokenize(line))
        for word_dx in get(word,incl_alt=incl_alt)
    ]
    return pd.DataFrame(o)

def tokenize(txt,**y): 
    # return txt.split()
    # return tokenize_agnostic(txt,**y)
    return tokenize_nice(txt,**y)

def get_df(token,**kwargs):
    return pd.DataFrame(get(token,**kwargs))

def get(token,config={},toprint=False,incl_alt=True,cache_new=True,**kwargs):
    # not real?
    token_nice=token
    # token = zero_punc(token).lower()
    if not token: return []
    # get ipas
    cache = get_cache()
    # tokenl=token.lower()
    tokenl=to_token(token)
    if token in cache:
        ipas=cache[token]
    elif tokenl in cache:
        ipas=cache[tokenl]
    else:
        ipas=tts(tokenl)
        if ipas:
            cache[tokenl]=ipas
            if cache_new:
                write_to_cache(tokenl,ipas[0])
    ipas = ipas[:1] if not incl_alt else ipas
    sd=get_special_cases()
    if tokenl in sd['maybestressed']:
        if len(ipas)<2:
            ipa=ipas[0]
            ipax="'"+ipa if ipa[0].isalpha() else ipa[1:]
            ipas.append(ipax)
    elif tokenl in sd['unstressed']:
        ipa=ipas[0]
        ipax=ipa if ipa[0].isalpha() else ipa[1:]
        ipas=[ipax]

    is_funcword=tokenl in sd['functionwords']

    # get orths
    results = set()
    results_ld=[]
    for ipa_i,ipa in enumerate(ipas):
        num_sylls=ipa.count('.')+1
        sylls_ipa = ipa.split('.')
        sylls_text = syllabify_orth(token_nice,num_sylls=num_sylls)

        # maxlen=max([len(sylls_ipa), len(sylls_text)])
        
        # sylls_ipa+=['' for n in range(len(sylls_ipa) - maxlen)]
        # sylls_text+=['' for n in range(len(sylls_text) - maxlen)]

        is_funcword_now = int(is_funcword and num_sylls==1 and ipa[0]!="'")

        for si,(syll_ipa,syll_text) in enumerate(zip(sylls_ipa, sylls_text)):
            rdx={
                'word_ipa_i':ipa_i+1,
                'syll_i':si+1,
                # 'word_str':token_nice,
                'word_tok':tokenl,
                'word_ipa':ipa,
                'word_nsyll':num_sylls,
                'syll_ipa':syll_ipa,
                'syll_str':syll_text,
                'word_isfunc':is_funcword_now
            }
            results_ld.append(rdx)
    return results_ld


def get_cache(source_paths=[CMU_DICT_FN,CACHE_DICT_FN]):
# def get_cache(source_paths=[CMU_DICT_FN]):
    if not CACHE:
        for sfn in source_paths:
            if not os.path.exists(sfn): continue
            with open(sfn, encoding='utf-8') as f:
                for ln in f:
                    ln=ln.strip()
                    if not ln: continue
                    if ln.startswith('#'): continue
                    if not '\t' in ln: continue
                    word,ipa=[x.strip() for x in ln.strip().split('\t',1)]
                    if ipa not in set(CACHE[word]):
                        CACHE[word].append(ipa)
    return CACHE



def tts(token):
    espeak_ipa=espeak2ipa(token)
    if espeak_ipa is None: return []
    cmu=espeak2cmu(espeak_ipa)
    cmu_sylls = syllabify_cmu(cmu)
    ipa = cmusylls2ipa(cmu_sylls)
    return [ipa] if ipa else []




def write_to_cache(token,ipa):
    with open(CACHE_DICT_FN,'a+',encoding='utf-8') as of:
        of.write(f'{token}\t{ipa}\n')


def add_elisions(_ipa):
    """
    Add alternative pronunciations: those that have elided syllables
    """
    replace={}

    # -OWER
    # e.g. tower, hour, bower, etc
    replace['aʊ.ɛː']='aʊr'


    # -INOUS
    # e.g. ominous, etc
    replace['ə.nəs']='nəs'

    # -EROUS
    # e.g. ponderous, adventurous
    replace['ɛː.əs']='rəs'

    # -IA-
    # e.g. plutonian, indian, assyrian, idea, etc
    replace['iː.ə']='jə'
    # -IOUS
    # e.g. studious, tedious, etc
    #replace[u'iː.əs']=u'iːəs'


    # -IER
    # e.g. happier
    replace['iː.ɛː']='ɪr'

    # -ERING
    # e.g. scattering, wondering, watering
    replace['ɛː.ɪŋ']='rɪŋ'

    # -ERY
    # e.g. memory
    # QUESTIONABLE
    #replace[u'ɛː.iː']=u'riː'

    # -ENING
    # e.g. opening
    replace['ə.nɪŋ']='nɪŋ'

    # -ENER
    # e.g. gardener
    replace['ə.nɛː']='nɛː'

    # -EL- (-ELLER, -ELLING, -ELLY)
    # e.g. traveller, dangling, gravelly
    # QUESTIONABLE
    #replace[u'ə.l']=u'l'

    # -IRE-
    # e.g. fire, fiery, attire, hired
    replace['ɪ.ɛː']='ɪr'

    # -EL, -UAL
    # e.g. jewel
    replace['uː.əl']='uːl'

    # -EVN
    # e.g. heaven, seven
    replace['ɛ.vən']='ɛvn'

    # -IOUS, -EER
    # e.g. sincerest, dear, incommodiously
    # QUESTIONABLE
    #replace[u'.ʌ.']=u'ʌ.'
    replace['eɪ.ʌ']='eɪʌ'

    new=[_ipa]
    for k,v in list(replace.items()):
        if k in _ipa:
            new+=[_ipa.replace(k,v)]
    return new




import shutil
ERROR_SHOWN=False
ERROR_MSG="""
[cadence] A word unknown to the pronunciation dictionary ("{{WORD}}") cannot be syllabified because espeak text-to-speech software is not installed. It is highly recommend you install this software.

To install:

    * On Linux, type into the terminal:
        apt-get install espeak
    
    * On Mac:
        (1) Install homebrew if not already installed. Paste into Terminal app:
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        (2) Type into the Terminal app:
            brew install espeak
    
    * On Windows:
        Download and install from http://espeak.sourceforge.net/download.html.
"""

def espeak2ipa(token):
    global ERROR_SHOWN
    if not shutil.which('espeak'):
        eprint(ERROR_MSG.replace('{{WORD}}',token))
        ERROR_SHOWN=True
        return None
    
    token=''.join(x for x in token if x.isalpha())
    CMD=f'espeak -q -x {token}'
    try:
        res=subprocess.check_output(CMD.split()).strip()
        return res.decode("utf-8")
    except (OSError,subprocess.CalledProcessError) as e:
        return None

def tts2ipa(token,TTS_ENGINE=None):
    if TTS_ENGINE=='espeak':
        return espeak2ipa(token)
    elif TTS_ENGINE=='openmary':
        return openmary2ipa(token)
    else:
        #raise Exception("No TTS engine specified. Please select 'espeak' or 'openmary' in config.txt.")
        return None

def espeak2cmu(tok):
    return lexconvert(str(tok),'espeak','cmu')

def ipa2cmu(tok):
    return lexconvert(str(tok),'unicode-ipa','cmu')

def cmu2ipa(tok):
    res=lexconvert(str(tok),'cmu','unicode-ipa')

    ## BUG FIXES
    if tok.endswith(' T') and not res.endswith('t'): res=res+'t'
    return res

def syllabify_cmu(cmu_token):
    cmu_token=cmu_token.replace(' 2','2').replace(' 1','1') # fix prim/sec stress markings for syllabify
    sylls = syllabify(English, cmu_token)
    return sylls



def cmusylls2ipa1(sylls):
    new_cmu=[]
    for syl in sylls:
        stress, onset, nucleus, coda = syl
        """if not stress:
            stress_str=""
        elif stress==1:
            stress_str="'"
            stress_str=str(stress)
        else:
            stress_str="`"
            stress_str=str(stress)
        """
        if stress:
            nucleus = [nucleus[0]+" "+str(stress)] + nucleus[1:]

        _newcmu = " ".join(onset+nucleus+coda).strip().replace("  "," ")
        new_cmu+=[_newcmu]
    new_cmu =" 0 ".join(new_cmu)
    #print new_cmu
    print(new_cmu)

    ## ipa
    ipa=cmu2ipa(new_cmu)
    print(ipa)
    #print ipa
    # clean
    ipa_sylls = ipa.split('.')
    for i,syl in enumerate(ipa_sylls):
        if "ˈ" in syl:
            syl="'"+syl.replace("ˈ","")
        if "ˌ" in syl:
            syl="`"+syl.replace("ˌ","")
        ipa_sylls[i]=syl
    ipa=".".join(ipa_sylls)
    print(ipa)
    return ipa

def cmusylls2ipa(sylls):
    new_cmu=[]
    new_ipa=[]
    for syl in sylls:
        stress, onset, nucleus, coda = syl
        if stress:
            nucleus = [nucleus[0]+" "+str(stress)] + nucleus[1:]

        _newcmu = " ".join(onset+nucleus+coda).strip().replace("  "," ")
        _newipa=cmu2ipa(_newcmu)
        new_ipa+=[_newipa]
        new_cmu+=[_newcmu]
    new_cmu =" 0 ".join(new_cmu)
    #print new_cmu
    #print(new_cmu)

    ## ipa
    ipa=cmu2ipa(new_cmu)
    #print(ipa)
    #print ipa
    # clean
    #ipa_sylls = ipa.split('.')
    ipa_sylls = new_ipa
    for i,syl in enumerate(ipa_sylls):
        if "ˈ" in syl:
            syl="'"+syl.replace("ˈ","")
        if "ˌ" in syl:
            syl="`"+syl.replace("ˌ","")
        ipa_sylls[i]=syl
    ipa=".".join(ipa_sylls)
    #print(ipa)
    return ipa


def syllabify_orth_with_hyphenate(token,num_sylls=None):
    from hyphenate import hyphenate_word
    return hyphenate_word(token)
    return l
nltk_ssp=None
def syllabify_orth_with_nltk(token,num_sylls=None):
    global nltk_ssp
    if not nltk_ssp:
        from nltk.tokenize import SyllableTokenizer
        nltk_ssp = SyllableTokenizer()
    tokenl=token.lower()
    l = nltk_ssp.tokenize(tokenl)
    if tokenl!=token:
        o=[]
        i=0
        for x in l:
            xlen=len(x)
            o+=[token[i:i+xlen]]
            i+=xlen
        l=o
    return l

def syllabify_orth_with_pyphen(token,num_sylls=None):
    global Pyphen
    if not Pyphen:
        import pyphen
        Pyphen=pyphen.Pyphen(lang='en_US')
    sylls = Pyphen.inserted(token,hyphen='||||').split('||||')
    return sylls

# def syllabify_orth(token,num_sylls=None, func=syllabify_orth_with_pyphen):
def syllabify_orth(token,num_sylls=None, func=syllabify_orth_with_nltk):
    key=(token,num_sylls)
    if not key in ORTH_CACHE:
        pref,tok,suf = split_punct(token)
        l=func(tok,num_sylls=num_sylls) if num_sylls>1 else [tok]
        while len(l)<num_sylls:
            lastsyll=l[-1]
            lastsyll_len_half=len(lastsyll)//2
            lastsyll_a,lastsyll_b=lastsyll[:lastsyll_len_half],lastsyll[lastsyll_len_half:]
            l=[sx for sx in l[:-1]] + [lastsyll_a, lastsyll_b]
        while len(l)>num_sylls:
            l2=l[:-1]
            l2[-1]+=l[-1]
            l=l2

        l[0]=pref+l[0]
        l[-1]+=suf

        ORTH_CACHE[key]=l
    return ORTH_CACHE[key]


















# This is the P2TK automated syllabifier. Given a string of phonemes,
# it automatically divides the phonemes into syllables.
#
# By Joshua Tauberer, based on code originally written by Charles Yang.
#
# The syllabifier requires a language configuration which specifies
# the set of phonemes which are consonants and vowels (syllable nuclei),
# as well as the set of permissible onsets.
#
# Then call syllabify with a language configuration object and a word
# represented as a string (or list) of phonemes.
#
# Returned is a data structure representing the syllabification.
# What you get is a list of syllables. Each syllable is a tuple
# of (stress, onset, nucleus, coda). stress is None or an integer stress
# level attached to the nucleus phoneme on input. onset, nucleus,
# and coda are lists of phonemes.
#
# Example:
#
# import syllabifier
# language = syllabifier.English # or: syllabifier.loadLanguage("english.cfg")
# syllables = syllabifier.syllabify(language, "AO2 R G AH0 N AH0 Z EY1 SH AH0 N Z")
#
# The syllables variable then holds the following:
# [ (2, [],     ['AO'], ['R']),
#   (0, ['G'],  ['AH'], []),
#   (0, ['N'],  ['AH'], []),
#   (1, ['Z'],  ['EY'], []),
#   (0, ['SH'], ['AH'], ['N', 'Z'])]
#
# You could process that result with this type of loop:
#
# for stress, onset, nucleus, coda in syllables :
#   print " ".join(onset), " ".join(nucleus), " ".join(coda)
#
# You can also pass the result to stringify to get a nice printable
# representation of the syllables, with periods separating syllables:
#
# print syllabify.stringify(syllables)
#
#########################################################################

English = {
    'consonants': ['B', 'CH', 'D', 'DH', 'F', 'G', 'HH', 'JH', 'K', 'L', 'M', 'N', 
    'NG', 'P', 'R', 'S', 'SH', 'T', 'TH', 'V', 'W', 'Y', 'Z', 'ZH'],
    'vowels': [ 'AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW'],
    'onsets': ['P', 'T', 'K', 'B', 'D', 'G', 'F', 'V', 'TH', 'DH', 'S', 'Z', 'SH', 'CH', 'JH', 'M',
    'N', 'R', 'L', 'HH', 'W', 'Y', 'P R', 'T R', 'K R', 'B R', 'D R', 'G R', 'F R',
    'TH R', 'SH R', 'P L', 'K L', 'B L', 'G L', 'F L', 'S L', 'T W', 'K W', 'D W', 
    'S W', 'S P', 'S T', 'S K', 'S F', 'S M', 'S N', 'G W', 'SH W', 'S P R', 'S P L',
    'S T R', 'S K R', 'S K W', 'S K L', 'TH W', 'ZH', 'P Y', 'K Y', 'B Y', 'F Y', 
    'HH Y', 'V Y', 'TH Y', 'M Y', 'S P Y', 'S K Y', 'G Y', 'HH W', '']
    }

def loadLanguage(filename) :
    '''This function loads up a language configuration file and returns
    the configuration to be passed to the syllabify function.'''

    L = { "consonants" : [], "vowels" : [], "onsets" : [] }

    f = open(filename, "r")
    section = None
    for line in f :
        line = line.strip()
        if line in ("[consonants]", "[vowels]", "[onsets]") :
            section = line[1:-1]
        elif section == None :
            raise ValueError("File must start with a section header such as [consonants].")
        elif not section in L :
            raise ValueError("Invalid section: " + section)
        else :
            L[section].append(line)

    for section in "consonants", "vowels", "onsets" :
        if len(L[section]) == 0 :
            raise ValueError("File does not contain any consonants, vowels, or onsets.")

    return L

def syllabify(language, word) :
    '''Syllabifies the word, given a language configuration loaded with loadLanguage.
       word is either a string of phonemes from the CMU pronouncing dictionary set
       (with optional stress numbers after vowels), or a Python list of phonemes,
       e.g. "B AE1 T" or ["B", "AE1", "T"]'''

    if type(word) == str :
        word = word.split()

    syllables = [] # This is the returned data structure.

    internuclei = [] # This maintains a list of phonemes between nuclei.

    for phoneme in word :

        phoneme = phoneme.strip()
        if phoneme == "" :
            continue
        stress = None
        if phoneme[-1].isdigit() :
            stress = int(phoneme[-1])
            phoneme = phoneme[0:-1]

        if phoneme in language["vowels"] :
            # Split the consonants seen since the last nucleus into coda and onset.

            coda = None
            onset = None

            # If there is a period in the input, split there.
            if "." in internuclei :
                period = internuclei.index(".")
                coda = internuclei[:period]
                onset = internuclei[period+1:]

            else :
                # Make the largest onset we can. The 'split' variable marks the break point.
                for split in range(0, len(internuclei)+1) :
                    coda = internuclei[:split]
                    onset = internuclei[split:]

                    # If we are looking at a valid onset, or if we're at the start of the word
                    # (in which case an invalid onset is better than a coda that doesn't follow
                    # a nucleus), or if we've gone through all of the onsets and we didn't find
                    # any that are valid, then split the nonvowels we've seen at this location.
                    if " ".join(onset) in language["onsets"] \
                       or len(syllables) == 0 \
                       or len(onset) == 0 :
                       break

            # Tack the coda onto the coda of the last syllable. Can't do it if this
            # is the first syllable.
            if len(syllables) > 0 :
                syllables[-1][3].extend(coda)

            # Make a new syllable out of the onset and nucleus.
            syllables.append( (stress, onset, [phoneme], []) )

            # At this point we've processed the internuclei list.
            internuclei = []

        elif not phoneme in language["consonants"] and phoneme != "." :
            raise ValueError("Invalid phoneme: " + phoneme)

        else : # a consonant
            internuclei.append(phoneme)

    # Done looping through phonemes. We may have consonants left at the end.
    # We may have even not found a nucleus.
    if len(internuclei) > 0 :
        if len(syllables) == 0 :
            syllables.append( (None, internuclei, [], []) )
        else :
            syllables[-1][3].extend(internuclei)

    return syllables

def stringify(syllables) :
    '''This function takes a syllabification returned by syllabify and
       turns it into a string, with phonemes spearated by spaces and
       syllables spearated by periods.'''
    ret = []
    for syl in syllables :
        stress, onset, nucleus, coda = syl
        if stress != None and len(nucleus) != 0 :
            nucleus[0] += str(stress)
        ret.append(" ".join(onset + nucleus + coda))
    return " . ".join(ret)


# If this module was run directly, syllabify the words on standard input
# into standard output. Hashed lines are printed back untouched.
if __name__ == "__main__" :
    import sys
    if len(sys.argv) != 2 :
        print("Usage: python syllabifier.py english.cfg < textfile.txt > outfile.txt")
    else :
        L = loadLanguage(sys.argv[1])
        for line in sys.stdin :
            if line[0] == "#" :
                sys.stdout.write(line)
                continue
            line = line.strip()
            s = stringify(syllabify(L, line))
            sys.stdout.write(s + "\n")