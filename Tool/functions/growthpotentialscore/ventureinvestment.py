import math
def get_growth_potential_pscore(summary_result,re):
    ans=80
    sum=0
    for e in summary_result.values():
        if type(e)!=list :
            sum+=e
            if  e <0:
                ans-=10
    if sum<0:
        ans-=10

    multip=1/(1+pow(math.e,-re))*1.25
    ans*=multip

    return ans