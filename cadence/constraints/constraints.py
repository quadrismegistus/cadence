from ..imports import *

"""
All constraints take the entire dataframe
"""

def no_stressed_weaks(df_mpos):
    return np.multiply(df_mpos.is_w , df_mpos.is_stressed)

def no_unstressed_strongs(df_mpos):
    return np.multiply(df_mpos.is_s, df_mpos.is_unstressed)
    
def no_weak_peaks(df_mpos):
    return np.multiply(df_mpos.is_w, df_mpos.is_peak)
def no_strong_troughs(df_mpos):
    return np.multiply(df_mpos.is_s, df_mpos.is_trough)

def w_resolution(df_mpos,weight=1):
    if len(set(df_mpos.word_i))<2: return np.nan # only applies to word-boundaries    
    # does this apply to weak positions?
    if df_mpos.parse_syll.iloc[0]=='w': return np.nan # cannot apply to strong positions

    firstsyll_islight=df_mpos.iloc[0].is_light
    firstsyll_isstressed=df_mpos.iloc[0].is_stressed
    if not (firstsyll_islight and firstsyll_isstressed): return weight
    return 0

def f_resolution(df_mpos,weight=1):
    if len(set(df_mpos.word_i))<2: return np.nan # only applies to word-boundaries
    if df_mpos.parse_pos.iloc[0]=='ss': return weight # cannot apply to strong positions
    if sum(df_mpos.is_funcword)!=len(df_mpos): return weight
    return 0


def no_window(s,badwindow=(1,1)):
    wlen=len(badwindow)
    l=[]
    window=[]
    for x in s:
        window.append(x)
        l.append(int(tuple(window)==badwindow))
        if len(window)>=wlen:window.pop(0)
    return l

def no_clash(dfparse):
    return no_window(dfparse.is_stressed,badwindow=(1,1))
def no_lapse(dfparse):
    return no_window(dfparse.is_stressed,badwindow=(0,0,0))
def no_nonalt(dfparse):
    ww=no_window(dfparse.is_w,badwindow=(1,1))
    ss=no_window(dfparse.is_s,badwindow=(1,1))
    return [1 if x or y else 0 for x,y in zip(ww,ss)]
def no_trochsub(dfparse):
    x=int(dfparse.is_s.iloc[0]==1)
    return [x]+[0 for y in range(len(dfparse)-1)]

def apply_posthoc_constraints(dfparse):
    dfparse['*clash']=[
        x
        for pi,pdf in dfparse.groupby('parse_i')
        for x in no_clash(pdf)
    ]
    dfparse['*lapse']=[
        x
        for pi,pdf in dfparse.groupby('parse_i')
        for x in no_lapse(pdf)
    ]
    dfparse['*nonalt']=[
        x
        for pi,pdf in dfparse.groupby('parse_i')
        for x in no_nonalt(pdf)
    ]


    dfparse[TOTALCOL]=dfparse[[col for col in dfparse.columns if col.startswith('*') and col!=TOTALCOL]].sum(axis=1)

