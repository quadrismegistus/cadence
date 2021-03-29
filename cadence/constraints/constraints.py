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

    firstsyll_islight=df_mpos.iloc[0].is_syll
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

def no_clash(df_mpos):
    return no_window(df_mpos.is_stressed,badwindow=(1,1))
def no_lapse(df_mpos):
    return no_window(df_mpos.is_stressed,badwindow=(0,0))



# default constraints
DEFAULT_CONSTRAINTS = {
    'w/peak':no_weak_peaks,
    'w/stressed':no_stressed_weaks,
    's/unstressed':no_unstressed_strongs,
    # 's/trough':no_strong_troughs,
    'clash':no_clash,
    'lapse':no_lapse,
    'f-res':f_resolution,
    'w-res':w_resolution,
}



def apply_constraints(mpos_window,constraints=DEFAULT_CONSTRAINTS):
    total=None
    assert len(set(mpos_window.parse_pos_i))==1
    dfc=pd.DataFrame(index=mpos_window.index)
    for cname,cfunc in constraints.items():
        cvals=cfunc(mpos_window)
        dfc['*'+cname]=cvals
    dfc['*total']=dfc.sum(axis=1)
    return dfc