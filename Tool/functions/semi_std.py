# -*- coding: utf-8 -*-
##########[上半方差，下半方差】
def semi_std(data,target):
    upSumSQ=0
    upcount=0
    downSumSQ=0
    downcount=0
    for e in data:
        if e > target:
            upSumSQ+=(e-target)**2
            upcount+=1
        else:
            downSumSQ+=(target-e)**2
            downcount+=1
    return [pow(upSumSQ/upcount,0.5),pow(downSumSQ/downcount,0.5)]