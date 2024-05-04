# -*- coding: utf-8 -*-：
# 获取风投模型上市时间

import math


class GetListTime():

    def __init__(self, equity, MV, re):
        WAITTIME = 10
        time1 = self.getNASDAQTime(equity, MV, re)

        time4 = self.getHKATime(MV, re)
        time5 = self.getSecondHKTime(MV, re)
        time6 = self.getNYSETime(MV, re)

        self.__h5=[time5, time4, time1]
        MINA=min([time4, time6])
        MINS=min([time1, time5])
        if MINA < WAITTIME:
            if time4 == MINA:
                self.__ans = ['HKEX',time4]
            else:
                self.__ans = ['NYSE1', time6]

        elif MINS<WAITTIME:
            if time1==MINS:
                self.__ans=['NASDAQ',time1]
            else:
                self.__ans = ['HKGEM', time5]
        else:
            self.__ans=['',99]

    def get_list_time(self):
        return self.__ans

    def get_h5_time(self):
        return self.__h5
    # NASDAQ上市
    ########精细模型需考虑equity并不是逐年递增，即：最大值不在最后一年的情况
    def getNASDAQTime(self,equity, MV,re):
        time = 99
        CNYtoUSD = 7
        MV_target= 50000000
        equity_target1 = 5000000
        equity_target2 = 4000000
        ###########判断目前是否能够上市
        if equity > equity_target1 * CNYtoUSD or (
                equity > equity_target2 * CNYtoUSD and (MV[0][0] > MV_target * CNYtoUSD )):
            time = 0
        ############判断未来是否能够上市
        if time == 99:
            ######### 标准2：已发行证券市值标准
            e=1
            while e<len(MV):
                if MV[e][0]> MV_target * CNYtoUSD:
                    time=MV[e][1]
                    break
                elif MV[e][3]> MV_target * CNYtoUSD:
                    time=MV[e][4]
                    break
                e+=1

        if MV[-1][-2] > 0:
            time = min(99, MV[-1][-1] + math.log(MV_target * CNYtoUSD / MV[-1][-2], 1 + re))
        else:
            time = 99

        return round(time, 2)


    # 香港主板
    # 市值大于1亿港
    # 盈利（净利润）近一年2000w港，在之前两年3000w港
    def getHKATime(self, MV, re):
        CNYtoHKD = 0.9
        time = 99
        MV_target = 100000000
        if MV[0][0] > MV_target * CNYtoHKD:
            time = 0
        ############判断未来是否能够上市
        if time == 99:
            e = 1
            while e < len(MV):
                if MV[e][0] > MV_target * CNYtoHKD:
                    time = MV[e][1]
                    break
                elif MV[e][3] > MV_target * CNYtoHKD:
                    time = MV[e][4]
                    break
                e += 1

        if MV[-1][-2] > 0:
            time = min(99, MV[-1][-1] + math.log(MV_target * CNYtoHKD / MV[-1][-2], 1 + re))
        else:
            time = 99

        return round(time, 2)

    # 香港创业板
    ##市值不能小于4600w港
    def getSecondHKTime(self,MV, re):
        CNYtoHKD = 0.9
        MV_target=46000000
        time = 99
        if MV[0][0] > MV_target * CNYtoHKD:
            time = 0
        ############判断未来是否能够上市
        if time == 99:
            e = 1
            while e < len(MV):
                if MV[e][0] > MV_target * CNYtoHKD:
                    time = MV[e][1]
                    break
                elif MV[e][3] > MV_target * CNYtoHKD:
                    time = MV[e][4]
                    break
                e += 1

        if MV[-1][-2] > 0:
            time = min(99, MV[-1][-1] + math.log(MV_target * CNYtoHKD / MV[-1][-2], 1 + re))
        else:
            time = 99

        return round(time,2)

    # 纽交所
    ##市值不小于1亿美元
    ##公司必须在最近3个财政年度里连续赢利，且在最后一年不少于250万美元、前两年每年不少于200万美元
    # 或在最后一年不少于450万美元，3年累计不少于650万美元；
    def getNYSETime(self, MV ,re):
        CNYtoUSD = 7
        time = 99
        MV_target=100000000
        if MV[0][0] > MV_target * CNYtoUSD:
            time = 0
        ############判断未来是否能够上市
        if time == 99:
            e = 1
            while e < len(MV):
                if MV[e][0] > MV_target * CNYtoUSD:
                    time = MV[e][1]
                    break
                elif MV[e][3] > MV_target * CNYtoUSD:
                    time = MV[e][4]
                    break
                e += 1
        if time == 99:
            if MV[-1][-2] > 0:
                time = min(99, MV[-1][-1] + math.log(MV_target * CNYtoUSD / MV[-1][-2], 1 + re))
            else:
                time = 99

        return round(time,2)
