import datetime

def isthisweek(targettime):
    ans=True
    if datetime.datetime.today().isocalendar()[0]!=targettime.isocalendar()[0] or\
        datetime.datetime.today().isocalendar()[1]!=targettime.isocalendar()[1]:
        ans=False
    return ans

