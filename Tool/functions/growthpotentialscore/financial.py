
import math
def get_growth_potential_pscore(assets):
    ans=0
    lens=len(assets)-1
    for i in range(lens):
        ans+=assets[i]/assets[i+1]-1
    ans/=lens
    #转换ans适应sigmoid ans(-1,1)
    ans-=0.02
    ans*=4
    ans=round(1/(1+pow(math.e,-ans))*100)
    return ans
