import math


def get_growth_potential_pscore(gr):
    ans=0
    for i in range(len(gr)):
        ans+=gr[i]
    ans/=len(gr)
    #转换ans适应sigmoid ans(-1,1)
    ans-=0.02
    ans*=4
    ans=round(1/(1+pow(math.e,-ans))*100)
    return ans
