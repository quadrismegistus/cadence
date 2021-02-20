"""
All constraints take the entire dataframe
"""

def no_stressed_weaks(df_mcombo):
    return [
        1 if ((parse=="w") and (stress>0)) else 0
        for parse,stress in zip(df_mcombo.parse,df_mcombo.syll_stress)
    ]

def no_unstressed_strongs(df_mcombo):
    return [
        1 if ((parse=="s") and (stress==0)) else 0
        for parse,stress in zip(df_mcombo.parse,df_mcombo.syll_stress)
    ]

def no_weak_peaks(df_mcombo):
    return [
        1 if ((parse=="w") and strength) else 0
        for parse,strength in zip(df_mcombo.parse,df_mcombo.syll_strength)
    ]

def w_resolution(df_mcombo): pass
def f_resolution(df_mcombo): pass