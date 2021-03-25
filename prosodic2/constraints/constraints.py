from ..imports import *

"""
All constraints take the entire dataframe
"""

def no_stressed_weaks(df_mcombo):
    return np.multiply(df_mcombo.is_w , df_mcombo.is_stressed)

def no_unstressed_strongs(df_mcombo):
    return np.multiply(df_mcombo.is_s, df_mcombo.is_unstressed)
    
def no_weak_peaks(df_mcombo):
    return np.multiply(df_mcombo.is_w, df_mcombo.is_peak)

def w_resolution(df_mcombo): pass
def f_resolution(df_mcombo): pass

def no_window(s,badwindow=(1,1)):
    wlen=len(badwindow)
    l=[]
    window=[]
    for x in s:
        window.append(x)
        l.append(int(tuple(window)==badwindow))
        if len(window)>=wlen:window.pop(0)
    return l

def no_clash(df_mcombo):
    return no_window(df_mcombo.is_stressed,badwindow=(1,1))
def no_lapse(df_mcombo):
    return no_window(df_mcombo.is_stressed,badwindow=(0,0,0))



# default constraints
DEFAULT_CONSTRAINTS = {
    # 'w/stressed':no_stressed_weaks,
    # 's/unstressed':no_unstressed_strongs,
    'w/peak':no_weak_peaks,
    # 'clash':no_clash,
    # 'lapse':no_lapse,
}



def apply_constraints(df_mcombo,constraints=DEFAULT_CONSTRAINTS):
    dfc=pd.DataFrame(df_mcombo)
    # dfc['parse']=df_mcombo['parse']
    total=None
    for cname,cfunc in constraints.items():
        cvals=cfunc(df_mcombo)
        cvals=pd.to_numeric(cvals,errors='coerce')
        if total is None: total=cvals
        else: total+=cvals
        dfc['*'+cname]=cvals
    dfc['*total']=total
    return dfc