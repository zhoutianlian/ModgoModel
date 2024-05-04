# -*- coding: utf-8 -*-：

import pandas as pd


def process_data_risk_premium_coef(data, flag, financial_report_data, main_industry):
    score = {}

    # 是否3年

    if data['company_operation_duration'] <= 3:
        above3years = 0
    else:
        above3years = 1


    # 公司年限得分
    if data['company_operation_duration'] <= 3:
        s = 10
    elif data['company_operation_duration'] <= 5:
        s = 40
    else:
        s = 70
    score['company_operation_duration'] = s

    # 未来一年新增员工百分比
    new_employee_portion = data['post_one_year_new_employee_number'] / data['current_employee_number']
    if new_employee_portion <= 0.3:
        s1 = 80
        s2 = 50
    elif new_employee_portion <= 0.5:
        s1 = 70
        s2 = 40
    else:
        s1 = 60
        s2 = 30
    score['new_employee_portion'] = s1 * (1 - above3years) + s2 * above3years

    # 招聘倾向
    if data['recruit_position_type_trend'] == '0':
        s1 = 60
        s2 = 80
    elif data['recruit_position_type_trend'] == '1':
        s1 = 30
        s2 = 40
    elif data['recruit_position_type_trend'] == '2':
        s1 = 50
        s2 = 70
    elif data['recruit_position_type_trend'] == '3':
        s1 = 40
        s2 = 50
    score['recruit_position_type_trend'] =  s1 * (1 - above3years) + s2 * above3years

    # 企业家管理年限
    if data['entrepreneur_management_duration'] <= 3:
        s1 = 40
        s2 = 50
    elif data['entrepreneur_management_duration'] <= 5:
        s1 = 60
        s2 = 65
    elif data['entrepreneur_management_duration'] <= 10:
        s1 = 70
        s2 = 75
    elif data['entrepreneur_management_duration'] <= 20:
        s1 = 75
        s2 = 80
    else:
        s1 = 65
        s2 = 70
    score['entrepreneur_management_duration'] = s1 * (1 - above3years) + s2 * above3years


    # 实控人持股比例
    if data['actual_controller_shareholding_percent'] <= 34:
        s1 = 20
        s2 = 50
    elif data['actual_controller_shareholding_percent'] <= 50:
        s1 = 60
        s2 = 70
    elif data['actual_controller_shareholding_percent'] <= 67:
        s1 = 90
        s2 = 80
    else:
        s1 = 60
        s2 = 40
    score['actual_controller_shareholding_percent'] = s1 * (1 - above3years) + s2 * above3years

    # 当前融资轮次
    current_finance_round = int(data['current_finance_round'])
    if current_finance_round == 0:
        s1 = 50
        s2 = 40
    elif current_finance_round <= 1:
        s1 = 80
        s2 = 70
    elif current_finance_round <= 3:
        s1 = 90
        s2 = 90
    else:
        s1 = 100
        s2 = 100
    score['current_finance_round'] = s1 * (1 - above3years) + s2 * above3years

    # 上市所在市场
    if data['capital_market'] == '0':
        s1 = 100
        s2 = 100
    elif data['capital_market'] == '1':
        s1 = 95
        s2 = 90
    elif data['capital_market'] == '2':
        s1 = 90
        s2 = 90
    elif data['capital_market'] == '3':
        s1 = 100
        s2 = 90
    elif data['capital_market'] == '4':
        s1 = 90
        s2 = 85
    else:
        s1 = 70
        s2 = 60
    score['capital_market'] = s1 * (1 - above3years) + s2 * above3years

    # 已信息化模块
    goodinfosystem = ['0','1','2','3','4','5','11']
    informatization_part = data['informatization_part'].split(',')

    countgoodinfosystem = len(set(goodinfosystem).intersection(set(informatization_part)))

    if countgoodinfosystem == 0:
        s1 = 50
        s2 = 40
    elif countgoodinfosystem == 1:
        s1 = 60
        s2 = 60
    elif countgoodinfosystem <= 3:
        s1 = 90
        s2 = 80
    elif countgoodinfosystem <= 6:
        s1 = 100
        s2 = 90
    else:
        s1 = 100
        s2 = 100

    score['informatization_part'] = s1 * (1 - above3years) + s2 * above3years

    #信息化匹配

    # MES/PLM/WMS/SCM/QMS系统是否匹配行业
    pi_list = [1010, 1510, 2010, 2510, 2520, 3020, 3030, 3510, 3520, 4520, 4530]
    warehouse_list = [1010, 1510, 2010, 2510, 2520, 2550, 3010, 3020, 3030, 4520, 4530]
    logistics_list = [1010, 1510, 2010, 2030, 2510, 2520, 2550, 3010, 3020, 3030, 4520, 4530]

    pi_software_list = ['6', '8', '10']
    warehouse_software_list = ['7']
    logistics_software_list = ['9']

    n = 0
    if int(main_industry[:4]) in pi_list:
        list1 = 1
        n += 3
    else:
        list1 = 0
    if int(main_industry[:4]) in warehouse_list:
        list2 = 1
        n += 1
    else:
        list2 = 0
    if int(main_industry[:4]) in logistics_list:
        list3 = 1
        n += 1
    else:
        list3 = 0

    n1 = len(set(informatization_part).intersection(set(pi_software_list)))
    n2 = len(set(informatization_part).intersection(set(warehouse_software_list)))
    n3 = len(set(informatization_part).intersection(set(logistics_software_list)))
    score['inforpart_match_industry'] = 100 / n * (list1 * n1 + list2 * n2 + list3 * n3)

    # 战略规划来源
    if data['strategy_planning_source'] == '0':
        s1 = 60
        s2 = 70
    elif data['strategy_planning_source'] == '1':
        s1 = 95
        s2 = 80
    elif data['strategy_planning_source'] == '2':
        s1 = 100
        s2 = 90
    score['strategy_planning_source'] = s1 * (1 - above3years) + s2 * above3years



    # 研发员工占总员工比例（研发团队员工人数/目前总员工人数）
    rdemployeeportion = data['research_team_employee_number'] / data['current_employee_number']

    if rdemployeeportion <= 0.4:
        s1 = 60
        s2 = 100
    elif rdemployeeportion <= 0.8:
        s1 = 100
        s2 = 100
    else:
        s1 = 60
        s2 = 40
    score['research_employee_percent'] = s1 * (1 - above3years) + s2 * above3years


    # 研发支出占总成本
    if data['research_expense_percent_to_total_cost'] <= 30:
        s1 = 80
        s2 = 80
    elif data['research_expense_percent_to_total_cost'] <= 40:
        s1 = 70
        s2 = 60
    elif data['research_expense_percent_to_total_cost'] <= 60:
        s1 = 60
        s2 = 40
    elif data['research_expense_percent_to_total_cost'] <= 80:
        s1 = 50
        s2 = 30
    else:
        s1 = 40
        s2 = 20
    score['research_expense_percent_to_total_cost'] = s1 * (1 - above3years) + s2 * above3years



    # 所得税率
    if 25 <= data['income_tax_rate'] <= 40:
        s1 = 60
        s2 = 50
    elif 20 <= data['income_tax_rate'] < 25:
        s1 = 70
        s2 = 60
    elif 15 <= data['income_tax_rate'] < 20:
        s1 = 80
        s2 = 70
    elif 10 <= data['income_tax_rate'] < 15:
        s1 = 90
        s2 = 80
    else:
        s1 = 100
        s2 = 90
    score['income_tax_rate'] = s1 * (1 - above3years) + s2 * above3years



    # 采购自外国供应商的成本占总支出
    if data['fremdness_supplier_cost_percent'] <= 10:
        s = 60
    elif 0 < data['fremdness_supplier_cost_percent'] <= 30:
        s = 50
    elif 10 < data['fremdness_supplier_cost_percent'] <= 50:
        s = 40
    elif 30 < data['fremdness_supplier_cost_percent'] <= 70:
        s = 30
    else:
        s = 20
    score['fremdness_supplier_cost_percent'] = s



    # 来源于外国客户的收入占总收入
    if data['fremdness_client_revenue_percent'] <= 10:
        s = 60
    elif 0 < data['fremdness_client_revenue_percent'] <= 30:
        s = 50
    elif 10 < data['fremdness_client_revenue_percent'] <= 50:
        s = 40
    elif 30 < data['fremdness_client_revenue_percent'] <= 70:
        s = 30
    else:
        s = 20
    score['fremdness_client_revenue_percent'] = s


    # 基本竞争策略
    if data['genericcompetitivestrategy'] == '0':
        s1 = 100
        s2 = 60
    elif data['genericcompetitivestrategy'] == '2':
        s1 = 40
        s2 = 100
    else:
        s1 = 60
        s2 = 50
    score['genericcompetitivestrategy'] = s1 * (1 - above3years) + s2 * above3years


    # 产业链位置
    if data['industry_chain_position'] == '0':
        s = 100
    elif data['industry_chain_position'] == '1':
        s = 50
    elif data['industry_chain_position'] == '2':
        s = 100
    score['industry_chain_position'] = s



    # 销售渠道
    mc = 0
    if '0' in data['marketingchannel_type']:
        mc += 1
    if '1' in data['marketingchannel_type']:
        mc += 0.6
    if '2' in data['marketingchannel_type']:
        mc += 0.8
    if '3' in data['marketingchannel_type']:
        mc += 0.7
    if '4' in data['marketingchannel_type']:
        mc += 1.2
    if '5' in data['marketingchannel_type']:
        mc += 0.8
    if '6' in data['marketingchannel_type']:
        mc += 0.7
    if '7' in data['marketingchannel_type']:
        mc += 0.7
    if '8' in data['marketingchannel_type']:
        mc += 0.8
        if  mc <= 1:
            s1 = 60
            s2 = 40
        elif mc <= 3:
            s1 = 80
            s2 = 60
        elif mc <= 5:
            s1 = 90
            s2 = 80
        elif mc <= 7:
            s1 = 100
            s2 = 90
        else:
            s1 = 100
            s2 = 100
    score['marketingchannel_type'] = s1 * (1 - above3years) + s2 * above3years



    # 收入模式
    revenue_mode = len(data['revenue_mode'].split(','))
    if revenue_mode <= 1:
        s1 = 50
        s2 = 40
    elif revenue_mode <= 2:
        s1 = 60
        s2 = 50
    elif revenue_mode <= 3:
        s1 = 70
        s2 = 60
    elif revenue_mode <= 5:
        s1 = 80
        s2 = 80
    elif revenue_mode <= 7:
        s1 = 90
        s2 = 90
    else:
        s1 = 100
        s2 = 100

    score['revenue_mode'] = s1 * (1 - above3years) + s2 * above3years


    #人均营业收入（营业收入/目前总员工人数）
    if flag == 2 or data['company_operation_duration'] <= 3:
        score['operation_revenue_per_employee'] = 60
    or_pe = financial_report_data['Rev'] / data['current_employee_number']
    if 0 < or_pe <= 1e5:
        s = 30
    else:
        s = 100
    score['operation_revenue_per_employee'] = s


    weight_list = [0.05, 0.05, 0.05, 0.1,0.1,0.02,0.02,0.02,0.02,0.01,0.03,0.1,0.05,0.1,0.1,0.05,0.04,0.03,0.04,0.02]

    score_data_frame = pd.DataFrame(columns = ['name', 'score', 'weight'])

    score_data_frame['name'] = list(score)
    score_data_frame['score'] = list(score.values())
    score_data_frame['weight'] = weight_list
    score_data_frame['weighted_score'] = score_data_frame['score'] * score_data_frame['weight']

    risk_premium_score = score_data_frame['weighted_score'].sum()

    return round(float(risk_premium_score),2)