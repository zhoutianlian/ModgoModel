# -*- coding: utf-8 -*-：
# 分数越高，费用率越低，60为基准值


def process_data_expense_ratio_coef(data, financial_report_data):
    score = {}

    # 招聘倾向
    s = 0
    if data['recruit_position_type_trend'] == '0':
        s = 50
    elif data['recruit_position_type_trend'] == '1':
        s = 55
    elif data['recruit_position_type_trend'] == '2':
        s = 40
    elif data['recruit_position_type_trend'] == '3':
        s = 60
    score['recruit_position_type_trend'] = s * 0.05

    # 已信息化模块
    ip = 0
    if '0' in data['informatization_part']:
        ip += 1
    if '1' in data['informatization_part']:
        ip += 1
    if '2' in data['informatization_part']:
        ip += 1
    if '3' in data['informatization_part']:
        ip += 1
    if '4' in data['informatization_part']:
        ip += 1
    if '5' in data['informatization_part']:
        ip += 1
    if '11' in data['informatization_part']:
        ip += 1
        if ip == 0:
            s = 60
        elif ip == 1:
            s = 65
        elif 2 <= ip <= 3:
            s = 75
        elif 4 <= ip <= 5:
            s = 50
        elif 6 <= ip <= 7:
            s = 40
        score['informatization_part'] = s * 0.05

    # 战略规划来源
    if data['strategy_planning_source'] == '0':
        s = 60
    elif data['strategy_planning_source'] == '1':
        s = 70
    elif data['strategy_planning_source'] == '2':
        s = 40
    score['strategy_planning_source'] = s * 0.03

    # 实用新型专利数量
    if 0 <= data['authorization_utility_model_number'] <= 5:
        s = 60
    elif 5 < data['authorization_utility_model_number'] <= 10:
        s = 65
    elif 10 < data['authorization_utility_model_number']:
        s = 50
    score['authorization_utility_model_number'] = s * 0.02

    # 发明专利数量
    if data['authorization_patents_number'] == 0:
        s = 60
    elif 1 <= data['authorization_patents_number'] <= 3:
        s = 70
    elif 3 < data['authorization_patents_number']:
        s = 50
    score['authorization_patents_number'] = s * 0.04

    # 软著数量
    if 0 <= data['authorization_software_copyright_number'] <= 5:
        s = 60
    elif 5 < data['authorization_software_copyright_number'] <= 10:
        s = 65
    elif 10 < data['authorization_software_copyright_number']:
        s = 50
    score['authorization_software_copyright_number'] = s * 0.02

    # 研发支出占总成本
    if 0 <= data['research_expense_percent_to_total_cost'] < 10:
        s = 45
    elif 10 <= data['research_expense_percent_to_total_cost'] < 20:
        s = 50
    elif 20 <= data['research_expense_percent_to_total_cost'] < 30:
        s = 60
    elif 30 <= data['research_expense_percent_to_total_cost'] < 40:
        s = 65
    elif 40 <= data['research_expense_percent_to_total_cost'] < 50:
        s = 70
    elif 50 <= data['research_expense_percent_to_total_cost'] < 60:
        s = 75
    elif 60 <= data['research_expense_percent_to_total_cost'] < 70:
        s = 60
    elif 70 <= data['research_expense_percent_to_total_cost'] < 80:
        s = 50
    elif 80 <= data['research_expense_percent_to_total_cost'] < 90:
        s = 40
    elif 90 <= data['research_expense_percent_to_total_cost'] < 100:
        s = 30
    score['research_expense_percent_to_total_cost'] = s * 0.04

    # 来源于外国客户的收入占总收入
    if data['fremdness_client_revenue_percent'] == 0:
        s = 60
    elif 0 < data['fremdness_client_revenue_percent'] <= 10:
        s = 65
    elif 10 < data['fremdness_client_revenue_percent'] <= 30:
        s = 70
    elif 30 < data['fremdness_client_revenue_percent'] <= 50:
        s = 55
    elif 50 < data['fremdness_client_revenue_percent'] <= 75:
        s = 50
    elif 75 < data['fremdness_client_revenue_percent'] <= 90:
        s = 45
    elif 90 < data['fremdness_client_revenue_percent'] <= 100:
        s = 40
    score['fremdness_client_revenue_percent'] = s * 0.05

    # 基本竞争策略
    if data['genericcompetitivestrategy'] == '0':
        s = 60
    elif data['genericcompetitivestrategy'] == '1':
        s = 70
    elif data['genericcompetitivestrategy'] == '2':
        s = 30
    score['genericcompetitivestrategy'] = s * 0.06

    # 产业链位置
    if data['industry_chain_position'] == '0':
        s = 40
    elif data['industry_chain_position'] == '1':
        s = 60
    elif data['industry_chain_position'] == '2':
        s = 40
    score['industry_chain_position'] = s * 0.05

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
        mc += 0.8
    if '8' in data['marketingchannel_type']:
        mc += 0.7
        if 0 < mc <= 3:
            s = 60
        elif 5 < mc <= 6:
            s = 55
        elif 6 < mc <= 7:
            s = 45
        elif 7 < mc:
            s = 35
        score['marketingchannel_type'] = s * 0.05

    # 收入类型
    rm = (len(data['revenue_mode']) + 1) / 2
    if '0' in data['revenue_mode']:
        rm += 1
    if '1' in data['revenue_mode']:
        rm += 1
    if '2' in data['revenue_mode']:
        rm += 1
    if '3' in data['revenue_mode']:
        rm += 1
    if '4' in data['revenue_mode']:
        rm += 1
    if '5' in data['revenue_mode']:
        rm += 1
    if '6' in data['revenue_mode']:
        rm += 1
    if '7' in data['revenue_mode']:
        rm += 1
    if '8' in data['revenue_mode']:
        rm += 1
    if '9' in data['revenue_mode']:
        rm += 1
    if 0 < rm <= 3:
        s = 65
    elif 3 < rm <= 5:
        s = 60
    elif 5 < rm <= 7:
        s = 55
    elif 7 < rm <= 9:
        s = 45
    else:
        s = 30
    score['revenue_mode'] = s * 0.03

    # 平均每年人员扩张速度（目前总员工人数/公司成立年数）
    eepy = data['current_employee_number'] / data['company_operation_duration']
    if 0 < eepy <= 100:
        s = 60
    elif 100 < eepy:
        s = 40
    score['employee_expansion_per_year'] = s * 0.03

    # 平均每年知识产权获授权数量（已获授权知识产权数量/公司成立年数）
    ipr = data['authorization_utility_model_number'] + 6 * data['authorization_patents_number'] \
        + data['authorization_software_copyright_number']
    iprpy = ipr / data['company_operation_duration']
    if iprpy == 0:
        s = 30
    elif 0 < iprpy <= 5:
        s = 50
    elif 5 < iprpy <= 10:
        s = 70
    elif 10 < iprpy <= 20:
        s = 65
    elif 20 < iprpy <= 50:
        s = 50
    elif 50 < iprpy:
        s = 45
    score['intellectual_property_number_per_year'] = s * 0.06

     # 销售员工占总员工比例（销售团队员工人数/目前总员工人数）
    saleper = data['sale_team_member_number'] / data['current_employee_number']
    if 0 <= saleper <= 0.3:
        s = 75
    elif 0.3 < saleper <= 0.4:
        s = 70
    elif 0.4 < saleper <= 0.5:
        s = 60
    elif 0.5 < saleper <= 0.6:
        s = 50
    elif 0.6 < saleper <= 1:
        s = 40
    score['sale_employee_percent'] = s * 0.06

    # 研发员工占总员工比例（研发团队员工人数/目前总员工人数）
    rdper = data['research_team_employee_number'] / data['current_employee_number']
    if 0 <= rdper <= 0.3:
        s = 70
    elif 0.3 < rdper <= 0.4:
        s = 65
    elif 0.4 < rdper <= 0.5:
        s = 60
    elif 0.5 < rdper <= 0.6:
        s = 55
    elif 0.6 < rdper <= 1:
        s = 50
    score['research_employee_percent'] = s * 0.05

    # 未来一年人员扩张速度（未来一年新增员工人数/目前总员工人数）
    eepoy = data['post_one_year_new_employee_number'] / data['current_employee_number']
    if 0 <= eepoy <= 0.3:
        s = 60
    elif 0.3 < eepoy <= 0.5:
        s = 70
    elif 0.5 < eepoy <= 1:
        s = 50
    else:
        s = 40
    score['employee_expansion_post_one_year'] = s * 0.05

    # 总人均研发支出（目前总员工人数&研发支出占总支出比例&总支出）
    repe = data['research_expense_percent_to_total_cost'] / 100 \
        * financial_report_data['Totalcost'] / data['current_employee_number']
    if repe == 0:
        s = 20
    elif 0 < repe <= 1e5:
        s = 60
    elif 1e5 < repe <= 5e5:
        s = 65
    elif 5e5 < repe <= 1e6:
        s = 75
    elif 1e6 < repe:
        s = 45
    score['research_expense_per_employee'] = s * 0.07

    # 研发团队人均研发支出（研发团队员工人数&研发支出占总支出比例&总支出）
    if data['research_team_employee_number'] == 0:
        score['research_expense_per_research_employee'] = 20 * 0.05
    else:
        repre = data['research_expense_percent_to_total_cost'] / 100 \
                * financial_report_data['Totalcost'] / data['research_team_employee_number']
        if repre == 0:
            s = 20
        elif 0 < repre <= 1e5:
            s = 60
        elif 1e5 < repre <= 5e5:
            s = 65
        elif 5e5 < repre <= 1e6:
            s = 70
        elif 1e6 < repre:
            s = 50
        score['research_expense_per_research_employee'] = s * 0.05

    # 知识产权平均成本（已获授权知识产权数量&研发支出占总支出比例&总支出）
    if ipr == 0:
        score['avg_cost_per_intellectual_property'] = 20 * 0.06
    else:
        acpip = data['research_expense_percent_to_total_cost'] / 100 \
                * financial_report_data['Totalcost'] / ipr
        if acpip == 0:
            s = 20
        elif 0 < acpip <= 1e5:
            s = 60
        elif 1e5 < acpip <= 5e5:
            s = 65
        elif 5e5 < acpip <= 1e6:
            s = 70
        elif 1e6 < acpip:
            s = 50
        score['avg_cost_per_intellectual_property'] = s * 0.06

    # 销售团队人均销售费用（销售费用/销售团队员工人数）
    # if data['is_sellingndistributionexpenses'] == 0:
    #     score['research_expense_per_employee'] = 60 * 0.02
    # else:
    # #     saleexp_pse = data['is_sellingndistributionexpenses'] / data['sale_team_member_number']
    # if flag == 0:
    #     score['sale_expense_per_sale_employee'] = 60 * 0.02
    # elif flag == 1:
    if data['sale_team_menber_number'] == 0:
        score['sale_expense_per_sale_employee'] = 20 * 0.08
    else:
        saleexp_pse = financial_report_data['saleexp'] / data['sale_team_member_number']
        if 0 <= saleexp_pse < 2e5:
            s = 60
        elif 2e5 <= saleexp_pse < 3e5:
            s = 55
        elif 3e5 <= saleexp_pse < 5e5:
            s = 45
        elif 5e5 <= saleexp_pse < 1e6:
            s = 30
        elif 1e6 <= saleexp_pse:
            s = 20
        score['sale_expense_per_sale_employee'] = s * 0.08

    bm_score = 0
    for value in score.values():
        bm_score += value
    return round(bm_score, 2)
