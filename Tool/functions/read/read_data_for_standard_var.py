# -*- coding: utf-8 -*-：
import datetime

from Tool.functions.read.get_something import get_ins, get_para, get_hypothesis
from Report.Log import logger


def get_cplx_data(PID):
    [adinfo_data, year_FR, month_FR,fr_year,fr_month]=get_FR(PID)
    [pc_A, pc_3, pc_pbp, pc_pep, pc_evsp, exitY, bestY, exitYpc, TVpc, perpetuity_g_basic, perpetuity_eva_pc,
     perpetuity_ri_pc, M_pc, perpetuity_g_pc, perpetuity_ed_pc] = get_para(PID)
    indus_code=get_ins(PID)
    CS, re, riskfree_rate = get_hypothesis(indus_code)
    usr_identity = get_usr_identity(PID)

    return [adinfo_data, year_FR, month_FR,indus_code,CS,re,pc_A, pc_3, pc_pbp, pc_pep, pc_evsp, exitY, bestY, exitYpc,
            TVpc, perpetuity_g_basic, perpetuity_eva_pc,perpetuity_ri_pc, M_pc, perpetuity_g_pc, perpetuity_ed_pc,
            fr_year,fr_month,usr_identity,riskfree_rate]

def get_FR(PID):

    month_FR = {}
    year_FR={}
    addinfo={}
    NAME_BS = ['货币资金', '短期金融投资', '应收票据', '应收账款', '预付款项', '其他应收款', '存货', '流动资产合计', 
            '长期金融投资', '长期股权投资', '投资性房地产', '固定资产',
            '在建工程', '无形资产', '开发支出', '商誉', '长期待摊费用', '递延所得税资产', '非流动资产合计', 
            '短期借款', '短期金融负债', '应付票据', '应付账款', '预收款项',
            '应付职工薪酬', '应交税费', '其他应付款', '一年以内到期的非流动负债', '流动负债合计', '长期借款', 
            '应付债券', '递延所得税负债', '非流动负债合计', '股本', '资本公积',
            '母公司股东的权益合计']
    NAME_IS = ['营业总收入', '营业成本', '营业税金及附加', '销售费用', '管理费用', '财务费用',
    '营业利润', '利润总额', '净利润', '归属于母公司股东的净利润']
    NAME_EXP =['利息支出', '利息收入', '当期固定资产折旧', '当期无形资产摊销', '当期长期待摊费用摊销']

    NAME_ADD =['plan5_fixExp','plan5_ingExp','plan5_efIncome','plan5_dcExp','plan5_debtIncome',
               'plan5_debtExp','plan5_gr','plan5_mpr','plan5_OptExpM','plan5_TaxRate','plan5_invday',
               'plan5_arday','plan5_apday','debtRate','re']
    #初始化年报，月报
    for e in NAME_BS:
        month_FR[e]=[]
        year_FR[e]=[]
    for e in NAME_IS:
        month_FR[e]=[]
        year_FR[e]=[]
    for e in NAME_EXP:
        month_FR[e]=[]
        year_FR[e]=[]

    month_FR['year'] = []
    month_FR['end_month'] = []


    SQL_NAME_EXP=['ed_interestexpense',
                'ed_interestrevenue',
                'ed_current_fixassets_depreciation',
                'ed_current_intangibleassets_amortization',
                'ed_current_longterm_deferredexpenses'
                ]
    db = connect_mysql_fuyoubank_security()
    cursor = db.cursor()
    current_year=datetime.datetime.today().year

    sql_bs = '''select a_cash,
                            a_shortterm_financialinvestment,
                            a_notesreceivable,
                            a_accountsreceivable,
                            a_prepayment,
                            a_otherreceivable,
                            a_inventory,
                            a_totalcurrentassets,
                            a_longterm_financialinvestment,
                            a_longterm_equityinvestment,
                            a_investmentproperties,
                            a_fixedassets,
                            a_constructioninprogress,
                            a_intangibleassets,
                            a_developmentcosts,
                            a_goodwill,
                            a_longterm_prepaidexpenses,
                            a_defferredtaxassets,
                            a_totalnoncurrentassets,
                            l_shortterm_borrowings,
                            l_shortterm_financialliabilities,
                            l_notespayable,
                            l_accountspayable,
                            l_advancesfromcustomers,
                            l_employeeremunerationspayable,
                            l_taxespayable,
                            l_otherpayable,
                            l1year_noncurrentliabilities,
                            l_totalcurrentliabilities,
                            l_longterm_borrowings,
                            l_bondspayable,
                            l_deferredtaxliabilities,
                            l_totalnoncurrentliabilities,
                            e_sharecapital,
                            e_capitalreserve,
                            e_totalequityattributabletoparent,bs_excel_date from valuation_detail_model_bs_input where pid=''' + str(
        PID) + ' and useful=0'
    try:
        cursor.execute(sql_bs)
    except Exception as e:
        logger(e)
        cursor.close()
        db.close()
    bs_data = list(cursor.fetchall())


    sql_is = '''select is_totaloperatingrevenue,
                            is_operatingcosts,
                            is_businesstaxesnsurcharges,
                            is_sellingndistributionexpenses,
                            is_generalnadministrativeexpenses,
                            is_financialexpenses,
                            is_operatingprofits,
                            is_totalprofit,
                            is_netprofits,
                            is_netprofitsattributabletoshareholdersofparent,is_excel_date from valuation_detail_model_is_input where pid=''' + str(
        PID) + ' and useful=0'
    try:
        cursor.execute(sql_is)
    except Exception as e:
        logger(e)
        cursor.close()
        db.close()
    is_data = list(cursor.fetchall())

    sql_exp = '''select ed_interestexpense,
                            ed_interestrevenue,
                            ed_current_fixassets_depreciation,
                            ed_current_intangibleassets_amortization,
                            ed_current_longterm_deferredexpenses,ed_date from valuation_detail_model_expense_input where pid=''' + str(
        PID) + ' and useful=0'
    try:
        cursor.execute(sql_exp)
    except Exception as e:
        logger(e)
        cursor.close()
        db.close()
    exp_data = list(cursor.fetchall())

    sql_addinfo_find='select count(*) from valuation_detail_model_otherinfo_input where pid ='+str(PID)
    try:
        cursor.execute(sql_addinfo_find)
    except Exception as e:
        logger(e)
        cursor.close()
        db.close()
    find = list(cursor.fetchall())[0][0]
    if int(find) == 0:
        for e in range(len(NAME_ADD)):
            addinfo[NAME_ADD[e]] = [None]
    else:
        sql_addinfo = '''select post_fiveyear_fixassets_expense,
        post_fiveyear_intangibleassets_expense,
        post_fiveyear_finance_acquisition_amount,
        post_fiveyear_cash_dividend_expense,
        post_fiveyear_debt_bond_acquisition_amount,
        post_fiveyear_debt_bond_expense_amount,
        post_fiveyear_compound_growth_rate,
        post_fiveyear_grossprofit_tendency,
        post_fiveyear_operation_expense_rate_tendency,
        post_fiveyear_company_incometax_tendency,
        post_fiveyear_company_inventory_turnover_day_tendency,
        post_fiveyear_accountsreceivable_duration_tendency,
        post_fiveyear_accountspayable_duration_tendency,
        avg_debt_rate,
        shareholder_requiredrateofreturn from valuation_detail_model_otherinfo_input where pid =''' + str(PID)
        try:
            cursor.execute(sql_addinfo)
        except Exception as e:
            logger(e)
            cursor.close()
            db.close()
        adinfo_data = list(cursor.fetchall())[0]
        for e in range(len(NAME_ADD)):
            addinfo[NAME_ADD[e]] = [adinfo_data[e]]

    cursor.close()
    db.close()

    #获得最新财报年月：
    fr_year=0
    fr_month=0
    for e in bs_data:
        if int(e[-1][:4])>fr_year:
            fr_year=int(e[-1][:4])
            if e[-1][5:7]!= '12':
                if e[-1][6]=='月':
                    fr_month=int(e[-1][5:6])
                else:
                    fr_month=int(e[-1][5:7])
            else:
                fr_month=12

    #读bs
    index=0
    temp_year=1
    while bs_data!=[]:
        e=bs_data[index]
        # 读月报
        if e[-1][5:7] != '12':
            if int(str(e[-1][:4])) == current_year - 1:
                month_FR['year'].insert(0, current_year-1)
                if e[-1][6]=='月':
                    month_FR['end_month'].insert(0, int(e[-1][5:6]))
                else:
                    month_FR['end_month'].insert(0, int(e[-1][5:7]))
                for ele in range(len(NAME_BS)):
                    month_FR[NAME_BS[ele]].insert(0, float(e[ele]))
            else:
                month_FR['year'].append( current_year)
                if e[-1][6] == '月':
                    month_FR['end_month'].append(int(e[-1][5:6]))
                else:
                    month_FR['end_month'].append(int(e[-1][5:7]))
                for ele in range(len(NAME_BS)):
                    month_FR[NAME_BS[ele]].append(float(e[ele]))
            bs_data.remove(bs_data[index])
            index=0
        #读年报
        else:
            if int(e[-1][:4])==current_year-temp_year:
                for ele in range(len(NAME_BS)):
                    year_FR[NAME_BS[ele]].insert(0, float(e[ele]))
                temp_year+=1
                bs_data.remove(bs_data[index])
                index=0
            else:
                index+=1

    index = 0
    temp_year = 1
    while is_data!=[]:
        e=is_data[index]
        #读月报
        if str(e[-1])[15:17] != '12':
            if int(str(e[-1][10:14])) == current_year - 1:
                for ele in range(len(NAME_IS)):
                    month_FR[NAME_IS[ele]].insert(0, float(e[ele]))
            else:
                for ele in range(len(NAME_IS)):
                    month_FR[NAME_IS[ele]].append(float(e[ele]))
            is_data.remove(e)
        # 读年报
        else:
            if int(e[-1][:4]) == current_year - temp_year:
                for ele in range(len(NAME_IS)):
                    year_FR[NAME_IS[ele]].insert(0, float(e[ele]))
                temp_year += 1
                is_data.remove(is_data[index])
                index = 0
            else:
                index += 1



    index = 0
    temp_year = 1
    while exp_data!=[]:
        e=exp_data[index]
        if str(e[-1])[15:17] != '12':
            if int(str(e[-1][10:14])) == current_year - 1:
                for ele in range(len(NAME_EXP)):
                    month_FR[NAME_EXP[ele]].insert(0, float(e[ele]))
            else:

                for ele in range(len(NAME_EXP)):
                    month_FR[NAME_EXP[ele]].append(float(e[ele]))
            exp_data.remove(e)
        else:
            if int(e[-1][:4]) == current_year - temp_year:
                for ele in range(len(NAME_EXP)):
                    year_FR[NAME_EXP[ele]].insert(0, float(e[ele]))
                temp_year += 1
                exp_data.remove(exp_data[index])
                index = 0
            else:
                index += 1


    return [addinfo,year_FR,month_FR,fr_year,fr_month]


