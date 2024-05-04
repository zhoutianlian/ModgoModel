# -*- coding: utf-8 -*-：
# 分数越高，毛利率越高，60为基准分


def process_data_gross_profit_ratio_coef(data, flag, financial_report_data):
    score = {}

    # 招聘倾向
    s = 0
    if data['recruit_position_type_trend'] == '0':
        s = 70
    elif data['recruit_position_type_trend'] == '1':
        s = 80
    elif data['recruit_position_type_trend'] == '2':
        s = 85
    elif data['recruit_position_type_trend'] == '3':
        s = 45
    score['recruit_position_type_trend'] = s * 0.03

    # 企业家管理年限
    if 0 < data['entrepreneur_management_duration'] <= 5:
        s = 30
    elif 5 < data['entrepreneur_management_duration'] <= 10:
        s = 50
    elif 10 < data['entrepreneur_management_duration'] <= 20:
        s = 80
    elif 20 < data['entrepreneur_management_duration']:
        s = 65
    score['entrepreneur_management_duration'] = s * 0.035

    # 战略规划来源
    if data['strategy_planning_source'] == '0':
        s = 45
    elif data['strategy_planning_source'] == '1':
        s = 75
    elif data['strategy_planning_source'] == '2':
        s = 70
    score['strategy_planning_source'] = s * 0.04

    # 实用新型专利数量
    if 0 <= data['authorization_utility_model_number'] <= 5:
        s = 30
    elif 5 < data['authorization_utility_model_number'] <= 10:
        s = 60
    elif 10 < data['authorization_utility_model_number'] <= 30:
        s = 70
    else:
        s = 80
    score['authorization_utility_model_number'] = s * 0.01

    # 发明专利数量
    if data['authorization_patents_number'] == 0:
        s = 20
    elif data['authorization_patents_number'] == 1:
        s = 60
    elif data['authorization_patents_number'] == 2:
        s = 65
    elif data['authorization_patents_number'] == 3:
        s = 70
    elif data['authorization_patents_number'] > 3:
        s = 80
    score['authorization_patents_number'] = s * 0.05

    # 软著数量
    if 0 <= data['authorization_software_copyright_number'] <= 5:
        s = 30
    elif 5 < data['authorization_software_copyright_number'] <= 10:
        s = 60
    elif 10 < data['authorization_software_copyright_number'] <= 30:
        s = 70
    else:
        s = 80
    score['authorization_software_copyright_number'] = s * 0.01

    # 研发支出占总成本
    if 0 <= data['research_expense_percent_to_total_cost'] < 10:
        s = 20
    elif 10 <= data['research_expense_percent_to_total_cost'] < 20:
        s = 30
    elif 20 <= data['research_expense_percent_to_total_cost'] < 30:
        s = 45
    elif 30 <= data['research_expense_percent_to_total_cost'] < 40:
        s = 65
    elif 40 <= data['research_expense_percent_to_total_cost'] < 50:
        s = 75
    elif 50 <= data['research_expense_percent_to_total_cost'] < 60:
        s = 80
    elif 60 <= data['research_expense_percent_to_total_cost'] < 70:
        s = 60
    elif 70 <= data['research_expense_percent_to_total_cost'] < 80:
        s = 40
    elif 80 <= data['research_expense_percent_to_total_cost'] < 90:
        s = 30
    elif 90 <= data['research_expense_percent_to_total_cost'] < 100:
        s = 20
    score['research_expense_percent_to_total_cost'] = s * 0.05

    # 采购自外国供应商的成本占总支出
    if data['fremdness_supplier_cost_percent'] == 0:
        s = 50
    elif 0 < data['fremdness_supplier_cost_percent'] <= 10:
        s = 60
    elif 10 < data['fremdness_supplier_cost_percent'] <= 30:
        s = 75
    elif 30 < data['fremdness_supplier_cost_percent'] <= 80:
        s = 65
    elif 80 < data['fremdness_supplier_cost_percent']:
        s = 30
    score['fremdness_supplier_cost_percent'] = s * 0.035

    # 来源于外国客户的收入占总收入
    if data['fremdness_client_revenue_percent'] == 0:
        s = 50
    elif 0 < data['fremdness_client_revenue_percent'] <= 10:
        s = 60
    elif 10 < data['fremdness_client_revenue_percent'] <= 30:
        s = 65
    elif 30 < data['fremdness_client_revenue_percent'] <= 50:
        s = 60
    elif 50 < data['fremdness_client_revenue_percent'] <= 75:
        s = 50
    elif 75 < data['fremdness_client_revenue_percent'] <= 90:
        s = 40
    elif 90 < data['fremdness_client_revenue_percent'] <= 100:
        s = 30
    score['fremdness_client_revenue_percent'] = s * 0.04

    # 基本竞争策略
    if data['genericcompetitivestrategy'] == '0':
        s = 85
    elif data['genericcompetitivestrategy'] == '1':
        s = 65
    elif data['genericcompetitivestrategy'] == '2':
        s = 90
    score['genericcompetitivestrategy'] = s * 0.05

    # 产业链位置
    if data['industry_chain_position'] == '0':
        s = 85
    elif data['industry_chain_position'] == '1':
        s = 40
    elif data['industry_chain_position'] == '2':
        s = 90
    score['industry_chain_position'] = s * 0.04

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
            s = 40
        elif 3 < mc <= 4:
            s = 60
        elif 4 < mc <= 5:
            s = 70
        elif 5 < mc <= 6:
            s = 75
        elif 6 < mc <= 7:
            s = 60
        elif 7 < mc:
            s = 50
        score['marketingchannel_type'] = s * 0.05

    # 收入类型
    rm = 0
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
        if 0 < rm <= 2:
            s = 30
        elif 2 < rm <= 4:
            s = 60
        elif 4 < rm <= 7:
            s = 70
        elif 7 < rm <= 9:
            s = 80
        else:
            s = 85
        score['revenue_mode'] = s * 0.05

    # 平均每年人员扩张速度（目前总员工人数/公司成立年数）
    eepy = data['current_employee_number'] / data['company_operation_duration']
    if 0 < eepy <= 20:
        s = 30
    elif 20 < eepy <= 50:
        s = 60
    elif 50 < eepy <= 100:
        s = 75
    elif 100 < eepy:
        s = 80
    score['employee_expansion_per_year'] = s * 0.02

    # 平均每年知识产权获授权数量（已获授权知识产权数量/公司成立年数）
    ipr = data['authorization_utility_model_number'] + 6 * data['authorization_patents_number'] \
        + data['authorization_software_copyright_number']
    iprpy = ipr / data['company_operation_duration']
    if iprpy == 0:
        s = 20
    elif 0 < iprpy <= 3:
        s = 30
    elif 3 < iprpy <= 5:
        s = 35
    elif 5 < iprpy <= 10:
        s = 40
    elif 10 < iprpy <= 20:
        s = 60
    elif 20 < iprpy <= 50:
        s = 75
    elif 50 < iprpy:
        s = 80
    score['intellectual_property_number_per_year'] = s * 0.035

    # 研发团队人均产出知识产权数量（已获授权知识产权数量/研发团队员工人数）
    if data['research_team_employee_number'] == 0:
        score['intellectual_property_per_research_team_employee_number'] = 20 * 0.035
    else:
        iprprt = ipr / data['research_team_employee_number']
        if 0 < iprprt <= 5:
            s = 30
        elif 5 < iprprt <= 10:
            s = 60
        elif 10 < iprprt <= 20:
            s = 65
        elif 20 < iprprt <= 30:
            s = 75
        else:
            s = 90
        score['intellectual_property_per_research_team_employee_number'] = s * 0.035

    # 销售员工占总员工比例（销售团队员工人数/目前总员工人数）
    saleper = data['sale_team_member_number'] / data['current_employee_number']
    if 0 <= saleper <= 0.3:
        s = 30
    elif 0.3 < saleper <= 0.4:
        s = 60
    elif 0.4 < saleper <= 0.5:
        s = 70
    elif 0.5 < saleper <= 0.6:
        s = 75
    elif 0.6 < saleper <= 1:
        s = 60
    score['sale_employee_percent'] = s * 0.05

    # 研发员工占总员工比例（研发团队员工人数/目前总员工人数）
    rdper = data['research_team_employee_number'] / data['current_employee_number']
    if 0 <= rdper <= 0.3:
        s = 30
    elif 0.3 < rdper <= 0.4:
        s = 65
    elif 0.4 < rdper <= 0.5:
        s = 75
    elif 0.5 < rdper <= 0.6:
        s = 80
    elif 0.6 < rdper <= 1:
        s = 70
    score['research_employee_percent'] = s * 0.04

    # 未来一年人员扩张速度（未来一年新增员工人数/目前总员工人数）
    eepoy = data['post_one_year_new_employee_number'] / data['current_employee_number']
    if 0 <= eepoy <= 0.2:
        s = 40
    elif 0.2 < eepoy <= 0.3:
        s = 60
    elif 0.3 < eepoy <= 0.4:
        s = 65
    elif 0.4 < eepoy <= 0.5:
        s = 75
    elif 0.5 < eepoy <= 1:
        s = 80
    else:
        s = 65
    score['employee_expansion_post_one_year'] = s * 0.03

    # 企业家创业前的管理年限（企业家管理经验年限-企业经营年限）
    enmdb = data['entrepreneur_management_duration'] - data['company_operation_duration']
    if enmdb <= 0:
        s = 40
    elif 0 < enmdb <= 5:
        s = 50
    elif 5 < enmdb <= 10:
        s = 65
    elif 10 < enmdb <= 20:
        s = 80
    elif 20 < enmdb <= 30:
        s = 75
    elif 30 < enmdb:
        s = 65
    score['entrepreneur_management_duration_before'] = s * 0.025

    # 总人均研发支出（目前总员工人数&研发支出占总支出比例&总支出）
    # if data['is_operatingcosts'] == 0:
    #     score['research_expense_per_employee'] = 60 * 0.02
    # else:
    #     tcost = data['is_operatingcosts'] \
    #             + data['is_businesstaxesnsurcharges'] \
    #             + data['is_sellingndistributionexpenses'] \
    #             + data['is_generalnadministrativeexpenses'] \
    #             + data['is_financialexpenses']
    repe = data['research_expense_percent_to_total_cost'] / 100 \
        * financial_report_data['Totalcost'] / data['current_employee_number']
    if repe == 0:
        s = 20
    elif 0 < repe <= 5e4:
        s = 30
    elif 5e4 < repe <= 1e5:
        s = 45
    elif 1e5 < repe <= 2e5:
        s = 60
    elif 2e5 < repe <= 3e5:
        s = 70
    elif 3e5 < repe <= 5e5:
        s = 80
    elif 5e5 < repe <= 1e6:
        s = 85
    elif 1e6 < repe:
        s = 75
    score['research_expense_per_employee'] = s * 0.03

    # 研发团队人均研发支出（研发团队员工人数&研发支出占总支出比例&总支出）
    # if data['research_team_employee_number'] == 0:
    #     score['research_expense_per_research_employee'] = 0
    # elif data['is_operatingcosts'] == 0:
    #     score['research_expense_per_research_employee'] = 60 * 0.02
    # else:
    if data['research_team_employee_number'] == 0:
        score['research_expense_per_research_employee'] = 20 * 0.035
    else:
        repre = data['research_expense_percent_to_total_cost'] / 100 \
            * financial_report_data['Totalcost'] / data['research_team_employee_number']
        if repre == 0:
            s = 20
        elif 0 < repre <= 5e4:
            s = 30
        elif 5e4 < repre <= 1e5:
            s = 45
        elif 1e5 < repre <= 2e5:
            s = 55
        elif 2e5 < repre <= 3e5:
            s = 65
        elif 3e5 < repre <= 5e5:
            s = 75
        elif 5e5 < repre <= 1e6:
            s = 80
        elif 1e6 < repre:
            s = 70
        score['research_expense_per_research_employee'] = s * 0.035

    # 知识产权平均成本（已获授权知识产权数量&研发支出占总支出比例&总支出）
    # if ipr == 0:
    #     score['avg_cost_per_intellectual_property'] = 0
    # elif data['is_operatingcosts'] == 0:
    #     score['avg_cost_per_intellectual_property'] = 60 * 0.02
    # else:
    if ipr == 0:
        score['avg_cost_per_intellectual_property'] = 20 * 0.07
    else:
        acpip = data['research_expense_percent_to_total_cost'] / 100 \
            * financial_report_data['Totalcost'] / ipr
        if acpip == 0:
            s = 20
        elif 0 < acpip <= 5e4:
            s = 30
        elif 5e4 < acpip <= 2e5:
            s = 60
        elif 2e5 < acpip <= 3e5:
            s = 65
        elif 3e5 < acpip <= 5e5:
            s = 70
        elif 5e5 < acpip <= 1e6:
            s = 75
        elif 1e6 < acpip:
            s = 65
        score['avg_cost_per_intellectual_property'] = s * 0.07

    # 人均净利润（净利润/目前总员工人数）
    # if data['netprofit'] == 0:
    #     netprofit_pe = data['is_netprofits'] / data['current_employee_number']
    # else:
    #     netprofit_pe = data['netprofit'] / data['current_employee_number']
    netprofit_pe = financial_report_data['NI'] / data['current_employee_number']
    if netprofit_pe <= 0:
        s = 10
    elif 0 < netprofit_pe <= 5e4:
        s = 30
    elif 5e4 < netprofit_pe <= 1e5:
        s = 40
    elif 1e5 < netprofit_pe <= 2e5:
        s = 60
    elif 2e5 < netprofit_pe <= 5e5:
        s = 70
    elif 5e5 < netprofit_pe <= 1e6:
        s = 85
    elif 1e6 < netprofit_pe:
        s = 95
    score['netprofit_per_employee'] = s * 0.04

    # 人均营业收入（营业收入/目前总员工人数）
    # if data['current_operatingrevenue'] == 0:
    #     or_pe = data['is_totaloperatingrevenue'] / data['current_employee_number']
    # else:
    #     or_pe = data['current_operatingrevenue'] / data['current_employee_number']
    or_pe = financial_report_data['Rev'] / data['current_employee_number']
    if 0 < or_pe <= 1e5:
        s = 30
    elif 1e5 < or_pe <= 2e5:
        s = 40
    elif 2e5 < or_pe <= 5e5:
        s = 50
    elif 5e5 < or_pe <= 1e6:
        s = 60
    elif 1e6 < or_pe <= 2e6:
        s = 65
    elif 2e6 < or_pe <= 3e6:
        s = 70
    elif 3e6 < or_pe:
        s = 75
    score['operation_revenue_per_employee'] = s * 0.05

    # 销售团队人均销售额（营业收入 / 销售团队员工人数）
    # if data['current_operatingrevenue'] == 0:
    #     sale_pse = data['is_totaloperatingrevenue'] / data['sale_team_member_number']
    # else:
    #     sale_pse = data['current_operatingrevenue'] / data['sale_team_member_number']
    if data['sale_team_menber_number'] == 0:
        score['sale_per_sale_employee'] = 10 * 0.05
    else:
        sale_pse = financial_report_data['Rev'] / data['sale_team_member_number']
        if 0 < sale_pse <= 1e5:
            s = 30
        elif 1e5 < sale_pse <= 2e5:
            s = 40
        elif 2e5 < sale_pse <= 5e5:
            s = 60
        elif 5e5 < sale_pse <= 1e6:
            s = 70
        elif 1e6 < sale_pse <= 2e6:
            s = 75
        elif 2e6 < sale_pse <= 3e6:
            s = 80
        elif 3e6 < sale_pse:
            s = 85
        score['sale_per_sale_employee'] = s * 0.05

    bm_score = 0
    for value in score.values():
        bm_score += value
    return round(bm_score, 2)
