# -*- coding: utf-8 -*-：


def perpetuity_g(perpetuity_g_basic,year=10):
    A=[]
    B=[]
    C=[]
    c=0.0
    b=perpetuity_g_basic
    a=perpetuity_g_basic*2
    for y in range(year+1):
        A.append(a)
        B.append(b)
        C.append(c)
        c=0.0
        b=b*0.9
        a=b*2
    return [A,B,C]
