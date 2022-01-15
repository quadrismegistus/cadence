from ..imports import *

"""
All constraints take the entire dataframe
"""

def w_stressed(df, is_s):
    return (1-is_s) * np.array([1.0 if x>0.0 else 0.0 for x in df.prom_stress])
def w_stressed_l(df, is_s):
    return (1-is_s) * np.array([1.0 if x>0.0 else 0.0 for x in df.prom_lstress])
def w_stressed_p(df, is_s):
    return (1-is_s) * np.array([1.0 if x>0.0 else 0.0 for x in df.prom_pstress])
def w_stressed_t(df, is_s):
    return (1-is_s) * np.array([1.0 if x>0.0 else 0.0 for x in df.prom_tstress])

def s_unstressed(df, is_s):
    return is_s * np.array([1.0 if x==0.0 else 0.0 for x in df.prom_stress])
def s_unstressed_l(df, is_s):
    return is_s * np.array([1.0 if x==0.0 else 0.0 for x in df.prom_lstress])
def s_unstressed_p(df, is_s):
    return is_s * np.array([1.0 if x==0.0 else 0.0 for x in df.prom_pstress])
def s_unstressed_t(df, is_s):
    return is_s * np.array([1.0 if x==0.0 else 0.0 for x in df.prom_tstress])


def w_peak(df, is_s):
    return (1-is_s) * df.prom_strength.values
def w_peak_p(df, is_s):
    return (1-is_s) * df.prom_pstrength.values
def s_trough(df, is_s):
    return is_s * (1-df.prom_strength.values)
def s_trough_p(df, is_s):
    return is_s * (1-df.prom_pstrength.values)


def is_disyllab_pos(is_s):
    return np.array([
        float(is_s[i] and ((i and is_s[i-1]) or (i+1<len(is_s) and is_s[i+1])))
        for i in range(len(is_s))
    ])

def unres_across(df,is_s):
    o=[np.nan] # need to start with non-viol since this applies only to second position of disyllab
    for i in range(1,len(df)):
        # for every 2 consecutive sylls...
        s1=is_s[i-1]
        s2=is_s[i]
        if s1!=s2:
            # not disyllabic
            o.append(np.nan)
        else:
            row1,row2=df.iloc[i-1],df.iloc[i]
            if (row1.sent_i, row1.word_i) == (row2.sent_i, row2.word_i):
                # disyllabic position is within not across words
                o.append(np.nan)
            else:
                if s1 and s2:
                    # disyllabic strong position immediately violates
                    # o[-1]=1.0  # prev position too?
                    o.append(1.0)
                    
                else:
                    if not row1.word_isfunc or not row2.word_isfunc:
                        # o[-1]=1.0  # prev position too?
                        o.append(1.0)
                    else:
                        o.append(0.0)
    return o

def unres_within(df,is_s):
    o=[np.nan] # need to start with non-viol since this applies only to second position of disyllab
    for i in range(1,len(df)):
        # for every 2 consecutive sylls...
        s1=is_s[i-1]
        s2=is_s[i]
        if s1!=s2:
            # not disyllabic
            o.append(np.nan)
        else:
            row1,row2=df.iloc[i-1],df.iloc[i]
            if (row1.sent_i, row1.word_i) != (row2.sent_i, row2.word_i):
                # disyllabic position is across not wihtin words
                o.append(np.nan)
            else:
                # disyllabic position within word
                # first position mist be light and stressed
                if not (row1.prom_weight==0 and row1.prom_stress>0):
                    # o[-1]=1.0  # prev position too?
                    o.append(1.0)
                else:
                    o.append(0.0)
    return o



def bad_window(s,badwindow=(1,1)):
    wlen=len(badwindow)
    l=[]
    window=[]
    for x in s:
        window.append(x)
        l.append(int(tuple(window)==badwindow))
        if len(window)>=wlen:window.pop(0)
    return l

def clash(df, is_s):
    is_stressed=[int(x>0) for x in df.prom_stress]
    return no_window(is_stressed,badwindow=(1,1))
def lapse(df, is_s):
    is_stressed=[int(x>0) for x in df.prom_stress]
    return bad_window(is_stressed,badwindow=(0,0,0))





CONSTRAINTL = [
    w_stressed,
    w_stressed_l,
    w_stressed_p,
    w_stressed_t,
    
    s_unstressed,
    s_unstressed_l,
    s_unstressed_p,
    s_unstressed_t,

    w_peak,
    w_peak_p,

    s_trough,
    s_trough_p,
    
    unres_across,
    unres_within,

    clash,
    lapse
]

CONSTRAINTD=dict((func.__name__,func) for func in CONSTRAINTL)