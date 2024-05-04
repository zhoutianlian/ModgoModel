import math


class GetListTime():

    def __init__(self,equity,ni,E,MV,re,NI,Rev,rev):
        self.WAITTIME=10
        self.equity = equity
        self.ni = ni
        self.E = E
        self.MV = MV
        self.re = re
        self.NI = NI
        self.Rev = Rev
        self.rev = rev

    def get_dlol_re(self):
        time2 = self.getATime(self.ni, self.rev, self.NI, self.Rev)
        return time2

    def get_time(self):
        time1 = self.getNASDAQTime(self.equity, self.ni, self.E, self.MV, self.re, self.NI)
        time2 = self.getATime(self.ni, self.rev, self.NI, self.Rev)
        time3 = self.getSecondBoardTime(self.ni, self.equity, self.NI, self.E)

        time4 = self.getHKATime(self.ni, self.NI, self.MV, self.re)
        time5 = self.getSecondHKTime(self.MV, self.re)
        time6 = self.getNYSETime(self.ni, self.MV, self.NI, self.re)
        self.__h5=[time3,time2,time1]
        MINA=min([time2,time4,time6])
        MINS=min([time1,time3,time5])
        if MINA<self.WAITTIME:
            if time2==MINA:
                self.__ans=['创业板',time2]
            elif time4==MINA:
                self.__ans=['香港主板',time4]
            else:
                self.__ans = ['纽约证券交易所', time6]

        elif MINS<self.WAITTIME:
            if time1==MINS:
                self.__ans=['NASDAQ',time1]
            elif time3==MINS:
                self.__ans=['新三板',time3]
            else:
                self.__ans = ['香港创业板', time5]
        else:
            self.__ans=['',99]

    def get_list_time(self):
        self.get_time()
        return self.__ans

    def get_h5_time(self):
        return self.__h5
    # NASDAQ上市
    ########精细模型需考虑equity并不是逐年递增，即：最大值不在最后一年的情况

    def getNASDAQTime(self,equity, ni, E, MV, re, NI):
        time = 99
        CNYtoUSD = 7
        ###########判断目前是否能够上市
        if equity > 5000000 * CNYtoUSD or (
                equity > 4000000 * CNYtoUSD and (MV > 50000000 * CNYtoUSD or ni > 750000 * CNYtoUSD)):
            time = 0
        ############判断未来是否能够上市
        if time == 99:
            TotalYear = len(E)

            ##########标准1；权益标准
            flag1 = 0
            for e in range(TotalYear):
                if E[e] > 5000000 * CNYtoUSD:
                    flag1 = 1
                    time = e + 1
                    break
            if flag1 == 0:
                if E[-1] == max(E):
                    gr = pow(E[-1] / E[0], 1 / (TotalYear - 1))
                    time = TotalYear + math.log(((5000000 * CNYtoUSD - E[-1]) / E[-1] + 1), gr)

            ######### 标准2：已发行证券市值标准
            flag2 = 0
            if MV > 50000000 * CNYtoUSD:
                temp = 0
            else:
                temp = math.log((50000000 * CNYtoUSD - MV) / MV + 1, 1 + re)
            if temp < time:
                for e in range(TotalYear):
                    if E[e] > 4000000 * CNYtoUSD:
                        flag2 = 1
                        if e + 1 < time:
                            time = e + 1
                        break
                if flag2 == 0:
                    if E[-1] == max(E):
                        gr = pow(E[-1] / E[0], 1 / (TotalYear - 1))
                        time = TotalYear + math.log(((4000000 * CNYtoUSD - E[-1]) / E[-1] + 1), gr)
                time = max(time, temp)
            ##########标准3：净收入标准
            flag3 = 0
            if NI[-1] > 0 and NI[0] > NI[-1]:
                for e in range(TotalYear):
                    if E[e] > 4000000 * CNYtoUSD and NI[e] > 750000 * CNYtoUSD:
                        flag3 = 1
                        if e + 1 < time:
                            time = e + 1
                        break
                if flag3 == 0:
                    if E[-1] == max(E):
                        gr1 = pow(E[-1] / E[0], 1 / (TotalYear - 1))
                        gr2 = pow(NI[-1] / NI[0], 1 / (TotalYear - 1))
                        time = max([TotalYear + math.log(((4000000 * CNYtoUSD - E[-1]) / E[-1] + 1), gr1),
                                    TotalYear + math.log(((750000 * CNYtoUSD - NI[-1]) / NI[-1] + 1), gr2)])

        return round(min(time, 99),2)

    # 主板上市
    # 1.净利润：最近3个会计年度净利润均为正数且累计超过人民币3000万元；
    # 2.收入最近3个会计年度营业收入累计超过人民币3亿元；
    def getATime(self,ni, rev, NI, Rev):
        time = 99
        max_NI = max(NI)
        max_Rev = max(Rev)
        TotalYear = len(NI)
        e = 1

        while e < TotalYear:
            flag1 = 0
            flag2 = 0
            if e == 1:
                if ni > 0 and NI[e] > 0 and NI[e - 1] > 0 and sum([ni, NI[e], NI[e - 1]]) > 30000000:
                    flag1 = 1
                if sum([rev, Rev[e], Rev[e - 1]]) > 300000000:
                    flag2 = 2
                if flag1 == 1 and flag2 == 1:
                    time = e
                    break

            else:
                if NI[e] > 0 and NI[e - 1] > 0 and NI[e - 2] > 0 and sum([NI[e], NI[e - 1], NI[e - 2]]) > 30000000:
                    flag1 = 1
                if sum([Rev[e], Rev[e - 1], Rev[e - 2]]) > 300000000:
                    flag2 = 1
                if flag1 == 1 and flag2 == 1:
                    time = e
                    break
            e += 1
        if time == 99:
            if flag1 == 1:
                if Rev[-1] == max_Rev and sum([Rev[0], Rev[1], Rev[2]]) < sum([Rev[-1], Rev[-2], Rev[-3]]):
                    gr = pow(sum([Rev[-1], Rev[-2], Rev[-3]]) / sum([Rev[0], Rev[1], Rev[2]]), 1 / (TotalYear - 3))
                    time = min(99, TotalYear + math.log(
                        ((300000000 - sum([Rev[-1], Rev[-2], Rev[-3]])) / sum([Rev[-1], Rev[-2], Rev[-3]]) + 1), gr))
            elif flag2 == 1:
                firstThree = sum([NI[0], NI[1], NI[2]])
                lastThree = sum([NI[-1], NI[-2], NI[-3]])

                if NI[-1] == max_NI and firstThree < lastThree:
                    #########前三年是负数,最后三年为正
                    # #########前三年是负数,最后三年为负
                    if firstThree < 0:
                        dif = lastThree - firstThree
                        time = TotalYear + (30000000 - lastThree) / dif * (TotalYear - 3)
                    #########前三年是正数,最后三年也是正数
                    else:
                        gr = pow(lastThree / firstThree, 1 / (TotalYear - 3))
                        time = min(99, TotalYear + math.log(((30000000 - lastThree) / lastThree + 1), gr))

            else:
                firstThree = sum([NI[0], NI[1], NI[2]])
                lastThree = sum([NI[-1], NI[-2], NI[-3]])
                if Rev[-1] == max_Rev and sum([Rev[0], Rev[1], Rev[2]]) < sum([Rev[-1], Rev[-2], Rev[-3]]) and NI[
                    -1] == max(
                        NI) and firstThree < lastThree:
                    gr = pow(sum([Rev[-1], Rev[-2], Rev[-3]]) / sum([Rev[0], Rev[1], Rev[2]]), 1 / (TotalYear - 3))
                    time1 = TotalYear + math.log(
                        ((300000000 - sum([Rev[-1], Rev[-2], Rev[-3]])) / sum([Rev[-1], Rev[-2], Rev[-3]]) + 1), gr)
                    if firstThree < 0:
                        dif = lastThree - firstThree
                        time2 = TotalYear + (30000000 - lastThree) / dif * (TotalYear - 3)
                    #########前三年是正数,最后三年也是正数
                    else:
                        gr = pow(lastThree / firstThree, 1 / (TotalYear - 3))
                        time2 = TotalYear + math.log(((30000000 - lastThree) / lastThree + 1), gr)
                    time = max(time1, time2)

        return round(min(time, 99),2)

    # 创业板上市
    # 净利润最近两年连续盈利，最近两年净利润累计不少于一千万元；
    # 或者最近一年盈利，且净利润不少于五百万元。
    # 资产：最近一期末(净资产)股权不少于2000万元；
    def getSecondBoardTime(self,ni, equity, NI, E):
        time = 99
        if ni > 5000000 and equity > 20000000:
            time = 0
        if time == 99:
            TotalYear = len(NI)
            for e in range(TotalYear):
                flag1 = 0
                flag2 = 0
                if E[e] > 20000000:
                    flag2 = 1
                if NI[e] > 5000000:
                    flag1 = 1
                elif e != 0 and NI[e] > 0 and NI[e - 1] > 0 and NI[e] + NI[e - 1] > 10000000:
                    flag1 = 1
                if flag1 == 1 and flag2 == 1:
                    time = e + 1
                    break
            if time == 99:
                if flag1 == 1:
                    if E[-1] == max(E):
                        if E[-1] > 0:
                            gr = pow(E[-1] / E[0], 1 / (TotalYear - 1))
                            time = TotalYear + math.log(((20000000 - E[-1]) / E[-1] + 1), gr)
                        else:
                            dif = E[-1] - E[0]
                            time = TotalYear + (20000000 - E[-1]) / dif * (TotalYear - 1)
                elif flag2 == 1:
                    if NI[-1] == max(NI):
                        if NI[-1] > 0:
                            if NI[0] / NI[-1] > 0:
                                gr = pow(round(NI[-1] / NI[0], 2), 1 / (TotalYear - 1))
                            elif NI[-2] / NI[-1] > 0:
                                gr = NI[-1] / NI[-2]
                            else:
                                gr = 0.01

                            oldNI = NI[-1]
                            count = 1
                            while True:
                                newNI = oldNI * gr
                                if newNI > 5000000 or newNI + oldNI > 10000000:
                                    time = TotalYear + count
                                    break
                                count += 1
                                if count+TotalYear > 99:
                                    break
                                oldNI=newNI

                        else:
                            dif = (abs(NI[-1] - NI[0])) / (TotalYear - 1)
                            oldNI = NI[-1]
                            count = 1
                            while True:
                                newNI = oldNI + dif
                                if newNI > 5000000 or newNI + oldNI > 10000000:
                                    time = count + TotalYear
                                    break

                                count += 1
                                if count > 99:
                                    break
                                oldNI = newNI

        return round(min(time, 99),2)

    # 香港主板
    # 市值大于1亿港
    # 盈利（净利润）近一年2000w港，在之前两年3000w港
    def getHKATime(self,ni, NI, MV, re):
        CNYtoHKD = 0.9
        time = 99
        TotalYear = len(NI)
        if MV > 100000000 * CNYtoHKD:
            temp = 0
        else:
            temp = math.log((100000000 * CNYtoHKD - MV) / MV + 1, 1 + re)
        #########未来两年是否能够上市
        if (ni + NI[0]) > 30000000 * CNYtoHKD and NI[1] > 20000000 * CNYtoHKD:
            time = 2
        #########十年内是否能够上市
        if time == 99:
            e = 2
            while e < TotalYear:
                if (NI[e - 2] + NI[e - 1]) > 30000000 * CNYtoHKD and NI[e] > 20000000 * CNYtoHKD:
                    time = e + 1
                    break
                e += 1
            #######十年外上市
            if time == 99:
                if max(NI) == NI[-1]:
                    if NI[-1] > 0:
                        if NI[0]/NI[-1]>0:
                            gr = pow(round(NI[-1] / NI[0],2), 1 / (TotalYear - 1))
                        elif NI[-2]/NI[-1]>0:
                            gr= NI[-1] / NI[-2]
                        else:
                            gr=0.01

                        oldNI = [NI[-3], NI[-2], NI[-1]]
                        count = 1
                        while True:
                            newNI = oldNI[-1] * gr
                            if oldNI[-1] + oldNI[-2] > 30000000 * CNYtoHKD and newNI > 20000000 * CNYtoHKD:
                                time = TotalYear + count
                                break
                            count += 1
                            if count>99:
                                break
                            oldNI.append(newNI)
                    else:
                        dif = (abs(NI[-1] - NI[0]) )/ (TotalYear - 1)
                        oldNI = [NI[-3], NI[-2], NI[-1]]
                        count = 1
                        while True:
                            newNI = oldNI[-1] + dif
                            if oldNI[-1] + oldNI[-2] > 30000000 * CNYtoHKD and newNI > 20000000 * CNYtoHKD:
                                time = TotalYear + count
                                break

                            count += 1
                            if count>99:
                                break
                            oldNI.append(newNI)

        return round(min(99, max(temp, time)),2)

    # 香港创业板
    ##市值不能小于4600w港
    def getSecondHKTime(self,MV, re):
        CNYtoHKD = 0.9

        if MV > 46000000 * CNYtoHKD:
            time = 0
        else:
            time = math.log((46000000 * CNYtoHKD - MV) / MV + 1, 1 + re)
        return round(min(time, 99),2)

    # 纽交所
    ##市值不小于1亿美元
    ##公司必须在最近3个财政年度里连续赢利，且在最后一年不少于250万美元、前两年每年不少于200万美元
    # 或在最后一年不少于450万美元，3年累计不少于650万美元；
    def getNYSETime(self,ni, MV, NI, re):
        CNYtoUSD = 7
        time = 99
        TotalYear = len(NI)
        if MV > 100000000 * CNYtoUSD:
            temp = 0
        else:
            temp = math.log((100000000 * CNYtoUSD - MV) / MV + 1, 1 + re)
        #########未来两年是否能够上市
        if (ni > 2000000 * CNYtoUSD and NI[0] > 2000000 * CNYtoUSD and NI[1] > 25000000 * CNYtoUSD) \
                or (ni + NI[0] + NI[1] > 6500000 * CNYtoUSD and NI[1] > 4500000 * CNYtoUSD):
            time = 2
        #########十年内是否能够上市
        if time == 99:
            e = 2
            while e < TotalYear:
                if (NI[e - 2] > 2000000 * CNYtoUSD and NI[e - 1] > 2000000 * CNYtoUSD and NI[e] > 25000000 * CNYtoUSD) \
                        or (NI[e - 2] + NI[e - 1] + NI[e] > 6500000 * CNYtoUSD and NI[e] > 4500000 * CNYtoUSD):
                    time = e + 1
                    break
                e += 1
            #######十年外上市
            if time == 99:
                if max(NI) == NI[-1]:
                    if NI[-1] > 0:
                        if NI[0]/NI[-1]>0:
                            gr = pow(round(NI[-1] / NI[0],2), 1 / (TotalYear - 1))
                        elif NI[-2]/NI[-1]>0:
                            gr= NI[-1] / NI[-2]
                        else:
                            gr=0.01
                        oldNI = [NI[-3], NI[-2], NI[-1]]
                        count = 1
                        while True:
                            newNI = oldNI[-1] * gr
                            if (oldNI[-1] > 2000000 * CNYtoUSD and oldNI[
                                -2] > 2000000 * CNYtoUSD and newNI > 25000000 * CNYtoUSD) \
                                    or (oldNI[-1] + oldNI[-2] + oldNI[-3] > 6500000 * CNYtoUSD and oldNI[
                                -1] > 4500000 * CNYtoUSD):
                                time = TotalYear + count
                                break

                            count += 1
                            if count>99:
                                break
                            oldNI.append(newNI)
                    else:
                        dif = abs(NI[-1] - NI[0]) / (TotalYear - 1)
                        oldNI = [NI[-3], NI[-2], NI[-1]]
                        count = 1
                        while True:
                            newNI = oldNI[-1] + dif
                            if (oldNI[-1] > 2000000 * CNYtoUSD and oldNI[
                                -2] > 2000000 * CNYtoUSD and newNI > 25000000 * CNYtoUSD) \
                                    or (oldNI[-1] + oldNI[-2] + oldNI[-3] > 6500000 * CNYtoUSD and oldNI[
                                -1] > 4500000 * CNYtoUSD):
                                time = TotalYear + count
                                break

                            count += 1
                            if count>99:
                                break
                            oldNI.append(newNI)

        return round(min(99, max(temp, time)),2)