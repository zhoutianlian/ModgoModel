# -*- coding: utf-8 -*-：
##ZXW
def get_FutureGR(MGR,year):
    ans=[]
    beg=MGR

    for e in range(year):
        ans.append(beg)
        beg=((beg-0.01)*0.85+0.01)

    return ans

