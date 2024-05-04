
def get_rank(data):
    if data['usr']==False:
        return False
    fr_year=str(data['fr_year'])[1:]
    fr_month=str(data['fr_month'])
    while len(fr_year)<3:
        fr_year='0'+fr_year
    while len(fr_month)<2:
        fr_month='0'+fr_month

    ans=str(data['usr'])+fr_year+fr_month+str(data['valuation_route'])  ##加法人
    return int(ans)