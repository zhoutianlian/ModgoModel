# -*- coding: utf-8 -*-：


# data = {'informatization_part': ['企业资源管理（ERP）', '人力资源管理（HR）'],
#         'recruit_position_type_trend': '管理人员',
#         'entrepreneur_management_duration': 12,
#         'actual_controller_shareholding_percent': 80,
#         'current_finance_round': 'B轮',
#         'capital_market': '未上市/挂牌',
#         'strategy_planning_source': '专业咨询公司',
#         'authorization_utility_model_number': 4,
#         'authorization_patents_number': 1,
#         'authorization_software_copyright_number': 12,
#         'research_expense_percent_to_total_cost': 50,
#         'income_tax_rate': 25,
#         'fremdness_supplier_cost_percent': 40,
#         'fremdness_client_revenue_percent': 60,
#         'genericcompetitivestrategy': '差异化',
#         'industry_chain_position': '上游',
#         'marketingchannel_type': ['个人直销', '新媒体'],
#         'revenue_mode': ['实物商品销售', '知识产权授权费', '广告费'],
#         'current_employee_number': 62,
#         'company_operation_duration': 2,
#         'research_team_employee_number': 26,
#         'sale_team_member_number': 24,
#         'post_one_year_new_employee_number': 120,
#
#         }


# 三年及以下公司
def process_data_under3(data, main_industry):
    score = {}
    # 招聘倾向
    if data['recruit_position_type_trend'] == '0':
        score['recruit_position_type_trend'] = 80 * 0.02
    elif data['recruit_position_type_trend'] == '1':
        score['recruit_position_type_trend'] = 100 * 0.02
    elif data['recruit_position_type_trend'] == '2':
        score['recruit_position_type_trend'] = 90 * 0.02
    elif data['recruit_position_type_trend'] == '3':
        score['recruit_position_type_trend'] = 60 * 0.02
    # 企业家管理年限
    if 0 < data['entrepreneur_management_duration'] <= 1:
        score['entrepreneur_management_duration'] = 0
    elif 1 < data['entrepreneur_management_duration'] <= 3:
        score['entrepreneur_management_duration'] = 15 * 0.03
    elif 3 < data['entrepreneur_management_duration'] <= 5:
        score['entrepreneur_management_duration'] = 35 * 0.03
    elif 5 < data['entrepreneur_management_duration'] <= 10:
        score['entrepreneur_management_duration'] = 70 * 0.03
    elif 10 < data['entrepreneur_management_duration'] <= 15:
        score['entrepreneur_management_duration'] = 85 * 0.03
    elif 15 < data['entrepreneur_management_duration'] <= 20:
        score['entrepreneur_management_duration'] = 95 * 0.03
    elif 20 < data['entrepreneur_management_duration'] <= 25:
        score['entrepreneur_management_duration'] = 100 * 0.03
    elif 25 < data['entrepreneur_management_duration'] <= 30:
        score['entrepreneur_management_duration'] = 90 * 0.03
    elif 30 < data['entrepreneur_management_duration']:
        score['entrepreneur_management_duration'] = 80 * 0.03
    # 实控人持股比例
    if 0 < data['actual_controller_shareholding_percent'] <= 10:
        score['actual_controller_shareholding_percent'] = 10 * 0.07
    elif 10 < data['actual_controller_shareholding_percent'] <= 20:
        score['actual_controller_shareholding_percent'] = 20 * 0.07
    elif 20 < data['actual_controller_shareholding_percent'] <= 33:
        score['actual_controller_shareholding_percent'] = 30 * 0.07
    elif 33 < data['actual_controller_shareholding_percent'] <= 40:
        score['actual_controller_shareholding_percent'] = 65 * 0.07
    elif 40 < data['actual_controller_shareholding_percent'] <= 50:
        score['actual_controller_shareholding_percent'] = 80 * 0.07
    elif 50 < data['actual_controller_shareholding_percent'] <= 67:
        score['actual_controller_shareholding_percent'] = 100 * 0.07
    elif 67 < data['actual_controller_shareholding_percent']:
        score['actual_controller_shareholding_percent'] = 75 * 0.07
    # 当前融资轮次
    if data['current_finance_round'] == '0':
        score['current_finance_round'] = 0
    elif data['current_finance_round'] == '1':
        score['current_finance_round'] = 50 * 0.04
    elif data['current_finance_round'] == '2':
        score['current_finance_round'] = 70 * 0.04
    elif data['current_finance_round'] == '3':
        score['current_finance_round'] = 85 * 0.04
    elif data['current_finance_round'] == '4':
        score['current_finance_round'] = 90 * 0.04
    elif data['current_finance_round'] == '5':
        score['current_finance_round'] = 95 * 0.04
    elif data['current_finance_round'] == '6':
        score['current_finance_round'] = 100 * 0.04
    # 上市所在市场
    if data['capital_market'] == '0':
        score['capital_market'] = 100 * 0.02
    elif data['capital_market'] == '1':
        score['capital_market'] = 70 * 0.02
    elif data['capital_market'] == '2':
        score['capital_market'] = 50 * 0.02
    elif data['capital_market'] == '3':
        score['capital_market'] = 100 * 0.02
    elif data['capital_market'] == '4':
        score['capital_market'] = 60 * 0.02
    elif data['capital_market'] == '5':
        score['capital_market'] = 0

    # 已信息化模块
    ip = 0
    info_list = data['informatization_part'].split(',')
    if '0' in info_list:
        ip += 1
    if '1' in info_list:
        ip += 1
    if '2' in info_list:
        ip += 1
    if '3' in info_list:
        ip += 1
    if '4' in info_list:
        ip += 1
    if '5' in info_list:
        ip += 1
    if '11' in info_list:
        ip += 1
        if ip == 0:
            score['informatization_part'] = 0
        elif ip == 1:
            score['informatization_part'] = 30 * 0.02
        elif 2 <= ip <= 3:
            score['informatization_part'] = 60 * 0.02
        elif 4 <= ip <= 5:
            score['informatization_part'] = 75 * 0.02
        elif 6 <= ip <= 7:
            score['informatization_part'] = 90 * 0.02

    # 战略规划来源
    if data['strategy_planning_source'] == '0':
        score['strategy_planning_source'] = 60 * 0.03
    elif data['strategy_planning_source'] == '1':
        score['strategy_planning_source'] = 75 * 0.03
    elif data['strategy_planning_source'] == '2':
        score['strategy_planning_source'] = 100 * 0.03

    # 实用新型专利数量
    if data['authorization_utility_model_number'] == 0:
        score['authorization_utility_model_number'] = 0
    elif 1 <= data['authorization_utility_model_number'] <= 2:
        score['authorization_utility_model_number'] = 40 * 0.02
    elif 3 <= data['authorization_utility_model_number'] <= 4:
        score['authorization_utility_model_number'] = 60 * 0.02
    elif 5 <= data['authorization_utility_model_number'] <= 10:
        score['authorization_utility_model_number'] = 90 * 0.02
    elif 10 < data['authorization_utility_model_number']:
        score['authorization_utility_model_number'] = 100 * 0.02

    # 发明专利数量
    if data['authorization_patents_number'] == 0:
        score['authorization_patents_number'] = 0
    elif data['authorization_patents_number'] == 1:
        score['authorization_patents_number'] = 60 * 0.10
    elif data['authorization_patents_number'] == 2:
        score['authorization_patents_number'] = 80 * 0.10
    elif data['authorization_patents_number'] == 3:
        score['authorization_patents_number'] = 90 * 0.10
    elif data['authorization_patents_number'] > 3:
        score['authorization_patents_number'] = 100 * 0.10

    # 软著数量
    if data['authorization_software_copyright_number'] == 0:
        score['authorization_software_copyright_number'] = 0
    elif 1 <= data['authorization_software_copyright_number'] <= 2:
        score['authorization_software_copyright_number'] = 40 * 0.02
    elif 3 <= data['authorization_software_copyright_number'] <= 4:
        score['authorization_software_copyright_number'] = 60 * 0.02
    elif 5 <= data['authorization_software_copyright_number'] <= 10:
        score['authorization_software_copyright_number'] = 90 * 0.02
    elif 10 < data['authorization_software_copyright_number']:
        score['authorization_software_copyright_number'] = 100 * 0.02

    # 研发支出占总成本
    if 0 <= data['research_expense_percent_to_total_cost'] < 10:
        score['research_expense_percent_to_total_cost'] = 0
    elif 10 <= data['research_expense_percent_to_total_cost'] < 20:
        score['research_expense_percent_to_total_cost'] = 30 * 0.05
    elif 20 <= data['research_expense_percent_to_total_cost'] < 30:
        score['research_expense_percent_to_total_cost'] = 60 * 0.05
    elif 30 <= data['research_expense_percent_to_total_cost'] < 40:
        score['research_expense_percent_to_total_cost'] = 80 * 0.05
    elif 40 <= data['research_expense_percent_to_total_cost'] < 50:
        score['research_expense_percent_to_total_cost'] = 90 * 0.05
    elif 50 <= data['research_expense_percent_to_total_cost'] < 60:
        score['research_expense_percent_to_total_cost'] = 100 * 0.05
    elif 60 <= data['research_expense_percent_to_total_cost'] < 70:
        score['research_expense_percent_to_total_cost'] = 85 * 0.05
    elif 70 <= data['research_expense_percent_to_total_cost'] < 80:
        score['research_expense_percent_to_total_cost'] = 75 * 0.05
    elif 80 <= data['research_expense_percent_to_total_cost'] < 90:
        score['research_expense_percent_to_total_cost'] = 70 * 0.05
    elif 90 <= data['research_expense_percent_to_total_cost'] < 100:
        score['research_expense_percent_to_total_cost'] = 50 * 0.05

    # 所得税率
    # if data['income_tax_rate'] == 25:
    #     score['income_tax_rate'] = 60 * 0.03
    # elif data['income_tax_rate'] == 20:
    #     score['income_tax_rate'] = 75 * 0.03
    # elif data['income_tax_rate'] == 15:
    #     score['income_tax_rate'] = 100 * 0.03
    # elif data['income_tax_rate'] == 10:
    #     score['income_tax_rate'] = 95 * 0.03
    # elif data['income_tax_rate'] == 0:
    #     score['income_tax_rate'] = 85 * 0.03
    if 25 <= data['income_tax_rate'] <= 40:
        score['income_tax_rate'] = 60 * 0.03
    elif 20 <= data['income_tax_rate'] < 25:
        score['income_tax_rate'] = 75 * 0.03
    elif 15 <= data['income_tax_rate'] < 20:
        score['income_tax_rate'] = 100 * 0.03
    elif 10 <= data['income_tax_rate'] < 15:
        score['income_tax_rate'] = 95 * 0.03
    elif 0 <= data['income_tax_rate'] < 10:
        score['income_tax_rate'] = 85 * 0.03

    # 采购自外国供应商的成本占总支出
    if data['fremdness_supplier_cost_percent'] == 0:
        score['fremdness_supplier_cost_percent'] = 30 * 0.02
    elif 0 < data['fremdness_supplier_cost_percent'] <= 10:
        score['fremdness_supplier_cost_percent'] = 100 * 0.02
    elif 10 < data['fremdness_supplier_cost_percent'] <= 30:
        score['fremdness_supplier_cost_percent'] = 90 * 0.02
    elif 30 < data['fremdness_supplier_cost_percent'] <= 50:
        score['fremdness_supplier_cost_percent'] = 75 * 0.02
    elif 50 < data['fremdness_supplier_cost_percent'] <= 75:
        score['fremdness_supplier_cost_percent'] = 55 * 0.02
    elif 75 < data['fremdness_supplier_cost_percent'] <= 90:
        score['fremdness_supplier_cost_percent'] = 30 * 0.02
    elif 90 < data['fremdness_supplier_cost_percent'] <= 100:
        score['fremdness_supplier_cost_percent'] = 10 * 0.02

    # 来源于外国客户的收入占总收入
    if data['fremdness_client_revenue_percent'] == 0:
        score['fremdness_client_revenue_percent'] = 10 * 0.03
    elif 0 < data['fremdness_client_revenue_percent'] <= 10:
        score['fremdness_client_revenue_percent'] = 60 * 0.03
    elif 10 < data['fremdness_client_revenue_percent'] <= 30:
        score['fremdness_client_revenue_percent'] = 100 * 0.03
    elif 30 < data['fremdness_client_revenue_percent'] <= 50:
        score['fremdness_client_revenue_percent'] = 85 * 0.03
    elif 50 < data['fremdness_client_revenue_percent'] <= 75:
        score['fremdness_client_revenue_percent'] = 80 * 0.03
    elif 75 < data['fremdness_client_revenue_percent'] <= 90:
        score['fremdness_client_revenue_percent'] = 70 * 0.03
    elif 90 < data['fremdness_client_revenue_percent'] <= 100:
        score['fremdness_client_revenue_percent'] = 65 * 0.03

    # 基本竞争策略
    if data['genericcompetitivestrategy'] == '0':
        score['genericcompetitivestrategy'] = 70 * 0.03
    elif data['genericcompetitivestrategy'] == '2':
        score['genericcompetitivestrategy'] = 80 * 0.03
    elif data['genericcompetitivestrategy'] == '1':
        score['genericcompetitivestrategy'] = 100 * 0.03

    # 产业链位置
    if data['industry_chain_position'] == '0':
        score['industry_chain_position'] = 85 * 0.04
    elif data['industry_chain_position'] == '1':
        score['industry_chain_position'] = 50 * 0.04
    elif data['industry_chain_position'] == '2':
        score['industry_chain_position'] = 95 * 0.04

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
        if 0 < mc <= 1:
            score['marketingchannel_type'] = 30 * 0.04
        elif 1 < mc <= 2:
            score['marketingchannel_type'] = 50 * 0.04
        elif 2 < mc <= 3:
            score['marketingchannel_type'] = 70 * 0.04
        elif 3 < mc <= 4:
            score['marketingchannel_type'] = 80 * 0.04
        elif 4 < mc <= 5:
            score['marketingchannel_type'] = 90 * 0.04
        elif 5 < mc <= 6:
            score['marketingchannel_type'] = 100 * 0.04
        elif 6 < mc <= 7:
            score['marketingchannel_type'] = 95 * 0.04
        elif 7 < mc:
            score['marketingchannel_type'] = 90 * 0.04

    # 收入类型
    # rm = 0
    rm = (len(data['revenue_mode']) + 1) / 2
    # if '0' in data['revenue_mode']:
    #     rm += 1
    # if '1' in data['revenue_mode']:
    #     rm += 1
    # if '2' in data['revenue_mode']:
    #     rm += 1
    # if '3' in data['revenue_mode']:
    #     rm += 1
    # if '4' in data['revenue_mode']:
    #     rm += 1
    # if '5' in data['revenue_mode']:
    #     rm += 1
    # if '6' in data['revenue_mode']:
    #     rm += 1
    # if '7' in data['revenue_mode']:
    #     rm += 1
    # if '8' in data['revenue_mode']:
    #     rm += 1
    # if '9' in data['revenue_mode']:
    #     rm += 1
    if rm == 1:
        score['revenue_mode'] = 30 * 0.04
    elif rm == 2:
        score['revenue_mode'] = 40 * 0.04
    elif rm == 3:
        score['revenue_mode'] = 60 * 0.04
    elif rm == 4:
        score['revenue_mode'] = 80 * 0.04
    elif rm == 5:
        score['revenue_mode'] = 90 * 0.04
    elif rm == 6:
        score['revenue_mode'] = 100 * 0.04
    elif rm == 7:
        score['revenue_mode'] = 90 * 0.04
    elif rm == 8:
        score['revenue_mode'] = 85 * 0.04
    elif rm == 9:
        score['revenue_mode'] = 60 * 0.04
    elif rm == 10:
        score['revenue_mode'] = 20 * 0.04

    # 平均每年人员扩张速度（目前总员工人数/公司成立年数）
    eepy = data['current_employee_number'] / data['company_operation_duration']
    if 0 < eepy <= 5:
        score['employee_expansion_per_year'] = 10 * 0.03
    elif 5 < eepy <= 10:
        score['employee_expansion_per_year'] = 20 * 0.03
    elif 10 < eepy <= 20:
        score['employee_expansion_per_year'] = 35 * 0.03
    elif 20 < eepy <= 30:
        score['employee_expansion_per_year'] = 55 * 0.03
    elif 30 < eepy <= 50:
        score['employee_expansion_per_year'] = 80 * 0.03
    elif 50 < eepy <= 100:
        score['employee_expansion_per_year'] = 90 * 0.03
    elif 100 < eepy:
        score['employee_expansion_per_year'] = 100 * 0.03

    # 平均融资间隔年数（公司成立年数/当前融资轮次）
    if data['current_finance_round'] == '0':
        score['company_duration_per_finance_round'] = 0
    else:
        if data['current_finance_round'] == '1':
            cfr = 1
        elif data['current_finance_round'] == '2':
            cfr = 2
        elif data['current_finance_round'] == '3':
            cfr = 3
        elif data['current_finance_round'] == '4':
            cfr = 4
        elif data['current_finance_round'] == '5':
            cfr = 5
        else:
            cfr = 6
        cdpfr = data['company_operation_duration'] / cfr
        if 0 < cdpfr <= 0.2:
            score['company_duration_per_finance_round'] = 100 * 0.02
        elif cdpfr <= 0.25:
            score['company_duration_per_finance_round'] = 95 * 0.02
        elif cdpfr <= 0.34:
            score['company_duration_per_finance_round'] = 90 * 0.02
        elif cdpfr <= 0.5:
            score['company_duration_per_finance_round'] = 85 * 0.02
        elif cdpfr <= 1:
            score['company_duration_per_finance_round'] = 80 * 0.02
        elif cdpfr <= 2:
            score['company_duration_per_finance_round'] = 70 * 0.02
        elif cdpfr <= 3:
            score['company_duration_per_finance_round'] = 60 * 0.02

    # 信息化建设速度（已信息化经营模块/公司成立年数）
    infos = ip / data['company_operation_duration']
    if 0 <= infos < 1:
        score['informatization_speed'] = 20 * 0.01
    elif 1 <= infos < 2:
        score['informatization_speed'] = 60 * 0.01
    elif 2 <= infos < 3:
        score['informatization_speed'] = 90 * 0.01
    elif 3 <= infos:
        score['informatization_speed'] = 100 * 0.01

    # 平均每年知识产权获授权数量（已获授权知识产权数量/公司成立年数）
    ipr = data['authorization_utility_model_number'] + 6 * data['authorization_patents_number'] \
        + data['authorization_software_copyright_number']
    iprpy = ipr / data['company_operation_duration']
    if iprpy == 0:
        score['intellectual_property_number_per_year'] = 0
    elif 0 < iprpy <= 1:
        score['intellectual_property_number_per_year'] = 10 * 0.02
    elif 1 < iprpy <= 3:
        score['intellectual_property_number_per_year'] = 20 * 0.02
    elif 3 < iprpy <= 5:
        score['intellectual_property_number_per_year'] = 35 * 0.02
    elif 5 < iprpy <= 10:
        score['intellectual_property_number_per_year'] = 65 * 0.02
    elif 10 < iprpy <= 20:
        score['intellectual_property_number_per_year'] = 85 * 0.02
    elif 20 < iprpy <= 50:
        score['intellectual_property_number_per_year'] = 95 * 0.02
    elif 50 < iprpy:
        score['intellectual_property_number_per_year'] = 100 * 0.02

    # 研发团队人均产出知识产权数量（已获授权知识产权数量/研发团队员工人数）
    if data['research_team_employee_number'] == 0:
        score['intellectual_property_per_research_team_employee_number'] = 0
    else:
        iprprt = ipr / data['research_team_employee_number']
        if 0 <= iprprt <= 1:
            score['intellectual_property_per_research_team_employee_number'] = 10 * 0.02
        elif 1 < iprprt <= 3:
            score['intellectual_property_per_research_team_employee_number'] = 35 * 0.02
        elif 3 < iprprt <= 5:
            score['intellectual_property_per_research_team_employee_number'] = 60 * 0.02
        elif 5 < iprprt <= 10:
            score['intellectual_property_per_research_team_employee_number'] = 85 * 0.02
        elif 10 < iprprt:
            score['intellectual_property_per_research_team_employee_number'] = 100 * 0.02

    # 销售员工占总员工比例（销售团队员工人数/目前总员工人数）
    saleper = data['sale_team_member_number'] / data['current_employee_number']
    if 0 <= saleper <= 0.1:
        score['sale_employee_percent'] = 0
    elif 0.1 < saleper <= 0.2:
        score['sale_employee_percent'] = 10 * 0.02
    elif 0.2 < saleper <= 0.3:
        score['sale_employee_percent'] = 40 * 0.02
    elif 0.3 < saleper <= 0.4:
        score['sale_employee_percent'] = 75 * 0.02
    elif 0.4 < saleper <= 0.5:
        score['sale_employee_percent'] = 90 * 0.02
    elif 0.5 < saleper <= 0.6:
        score['sale_employee_percent'] = 100 * 0.02
    elif 0.6 < saleper <= 0.7:
        score['sale_employee_percent'] = 85 * 0.02
    elif 0.7 < saleper <= 0.8:
        score['sale_employee_percent'] = 65 * 0.02
    elif 0.8 < saleper <= 0.9:
        score['sale_employee_percent'] = 50 * 0.02
    elif 0.9 < saleper <= 1:
        score['sale_employee_percent'] = 0

    # 研发员工占总员工比例（研发团队员工人数/目前总员工人数）
    rdper = data['research_team_employee_number'] / data['current_employee_number']
    if 0 <= rdper <= 0.1:
        score['research_employee_percent'] = 0
    elif 0.1 < rdper <= 0.2:
        score['research_employee_percent'] = 20 * 0.03
    elif 0.2 < rdper <= 0.3:
        score['research_employee_percent'] = 55 * 0.03
    elif 0.3 < rdper <= 0.4:
        score['research_employee_percent'] = 80 * 0.03
    elif 0.4 < rdper <= 0.5:
        score['research_employee_percent'] = 95 * 0.03
    elif 0.5 < rdper <= 0.6:
        score['research_employee_percent'] = 100 * 0.03
    elif 0.6 < rdper <= 0.7:
        score['research_employee_percent'] = 85 * 0.03
    elif 0.7 < rdper <= 0.8:
        score['research_employee_percent'] = 65 * 0.03
    elif 0.8 < rdper <= 0.9:
        score['research_employee_percent'] = 50 * 0.03
    elif 0.9 < rdper <= 1:
        score['research_employee_percent'] = 20 * 0.03

    # 招聘倾向和目前员工结构比较是否匹配
    if saleper > rdper and data['recruit_position_type_trend'] == '2':
        score['recruit_trend_comparison_current_employee_structure'] = 80 * 0.02
    elif saleper <= rdper and data['recruit_position_type_trend'] == '2':
        score['recruit_trend_comparison_current_employee_structure'] = 90 * 0.02
    elif saleper > rdper and data['recruit_position_type_trend'] == '1':
        score['recruit_trend_comparison_current_employee_structure'] = 100 * 0.02
    elif saleper <= rdper and data['recruit_position_type_trend'] == '1':
        score['recruit_trend_comparison_current_employee_structure'] = 95 * 0.02
    else:
        score['recruit_trend_comparison_current_employee_structure'] = 60 * 0.02

    # 未来一年人员扩张速度（未来一年新增员工人数/目前总员工人数）
    eepoy = data['post_one_year_new_employee_number'] / data['current_employee_number']
    if 0 <= eepoy <= 0.1:
        score['employee_expansion_post_one_year'] = 0
    elif 0.1 < eepoy <= 0.2:
        score['employee_expansion_post_one_year'] = 25 * 0.04
    elif 0.2 < eepoy <= 0.3:
        score['employee_expansion_post_one_year'] = 60 * 0.04
    elif 0.3 < eepoy <= 0.4:
        score['employee_expansion_post_one_year'] = 90 * 0.04
    elif 0.4 < eepoy <= 0.5:
        score['employee_expansion_post_one_year'] = 95 * 0.04
    elif 0.5 < eepoy <= 0.6:
        score['employee_expansion_post_one_year'] = 100 * 0.04
    elif 0.6 < eepoy <= 0.7:
        score['employee_expansion_post_one_year'] = 95 * 0.04
    elif 0.7 < eepoy <= 0.8:
        score['employee_expansion_post_one_year'] = 90 * 0.04
    elif 0.8 < eepoy <= 0.9:
        score['employee_expansion_post_one_year'] = 85 * 0.04
    elif 0.9 < eepoy <= 1:
        score['employee_expansion_post_one_year'] = 80 * 0.04
    else:
        score['employee_expansion_post_one_year'] = 70 * 0.04

    # 企业家创业前的管理年限（企业家管理经验年限-企业经营年限）
    enmdb = data['entrepreneur_management_duration'] - data['company_operation_duration']
    if enmdb <= 0:
        score['entrepreneur_management_duration_before'] = 0
    elif 0 < enmdb <= 2:
        score['entrepreneur_management_duration_before'] = 10 * 0.03
    elif 2 < enmdb <= 5:
        score['entrepreneur_management_duration_before'] = 30 * 0.03
    elif 5 < enmdb <= 10:
        score['entrepreneur_management_duration_before'] = 55 * 0.03
    elif 10 < enmdb <= 15:
        score['entrepreneur_management_duration_before'] = 80 * 0.03
    elif 15 < enmdb <= 20:
        score['entrepreneur_management_duration_before'] = 95 * 0.03
    elif 20 < enmdb <= 30:
        score['entrepreneur_management_duration_before'] = 100 * 0.03
    elif 30 < enmdb:
        score['entrepreneur_management_duration_before'] = 90 * 0.03

    # 发展阶段是否匹配人数（目前总员工人数&融资轮次）
    if cfr >= 3 and data['current_employee_number'] <= 10:
        score['development_stage_match_employee_number'] = 0
    elif cfr >= 2 and data['current_employee_number'] <= 10:
        score['development_stage_match_employee_number'] = 20 * 0.01
    else:
        score['development_stage_match_employee_number'] = 100 * 0.01

    # 总人均研发支出（目前总员工人数&研发支出占总支出比例&总支出）
    # tcost = data[]
    # repe = (data['research_expense_percent_to_total_cost'] * tcost) / data['current_employee_number']
    # if repe == 0:
    #     score['research_expense_per_employee'] = 0
    # elif 0 < repe <= 2e4:
    #     score['research_expense_per_employee'] = 10 * 0.02
    # elif 2e4 < repe <= 5e4:
    #     score['research_expense_per_employee'] = 20 * 0.02
    # elif 5e4 < repe <= 1e5:
    #     score['research_expense_per_employee'] = 40 * 0.02
    # elif 1e5 < repe <= 2e5:
    #     score['research_expense_per_employee'] = 60 * 0.02
    # elif 2e5 < repe <= 3e5:
    #     score['research_expense_per_employee'] = 80 * 0.02
    # elif 3e5 < repe <= 5e5:
    #     score['research_expense_per_employee'] = 90 * 0.02
    # elif 5e5 < repe <= 1e6:
    #     score['research_expense_per_employee'] = 95 * 0.02
    # elif 1e6 < repe:
    #     score['research_expense_per_employee'] = 100 * 0.02

    # 研发团队人均研发支出（研发团队员工人数&研发支出占总支出比例&总支出）
    # if data['research_team_employee_number'] == 0:
    #     score['research_expense_per_research_employee'] = 0
    # else:
    #     repre = (data['research_expense_percent_to_total_cost'] * tcost) / data['research_team_employee_number']
    #     if repre == 0:
    #         score['research_expense_per_research_employee'] = 0
    #     elif 0 < repre <= 2e4:
    #         score['research_expense_per_research_employee'] = 5 * 0.02
    #     elif 2e4 < repre <= 5e4:
    #         score['research_expense_per_research_employee'] = 10 * 0.02
    #     elif 5e4 < repre <= 1e5:
    #         score['research_expense_per_research_employee'] = 20 * 0.02
    #     elif 1e5 < repre <= 2e5:
    #         score['research_expense_per_research_employee'] = 45 * 0.02
    #     elif 2e5 < repre <= 3e5:
    #         score['research_expense_per_research_employee'] = 65 * 0.02
    #     elif 3e5 < repre <= 5e5:
    #         score['research_expense_per_research_employee'] = 80 * 0.02
    #     elif 5e5 < repre <= 1e6:
    #         score['research_expense_per_research_employee'] = 90 * 0.02
    #     elif 1e6 < repre:
    #         score['research_expense_per_research_employee'] = 100 * 0.02

    # 知识产权平均成本（已获授权知识产权数量&研发支出占总支出比例&总支出）
    # if ipr == 0:
    #     score['avg_cost_per_intellectual_property'] = 0
    # else:
    #     acpip = (data['research_expense_percent_to_total_cost'] * tcost) / ipr
    #     if acpip == 0:
    #         score['avg_cost_per_intellectual_property'] = 0
    #     elif 0 < acpip <= 2e4:
    #         score['avg_cost_per_intellectual_property'] = 5 * 0.02
    #     elif 2e4 < acpip <= 5e4:
    #         score['avg_cost_per_intellectual_property'] = 15 * 0.02
    #     elif 5e4 < acpip <= 1e5:
    #         score['avg_cost_per_intellectual_property'] = 25 * 0.02
    #     elif 1e5 < acpip <= 2e5:
    #         score['avg_cost_per_intellectual_property'] = 35 * 0.02
    #     elif 2e5 < acpip <= 3e5:
    #         score['avg_cost_per_intellectual_property'] = 50 * 0.02
    #     elif 3e5 < acpip <= 5e5:
    #         score['avg_cost_per_intellectual_property'] = 75 * 0.02
    #     elif 5e5 < acpip <= 1e6:
    #         score['avg_cost_per_intellectual_property'] = 100 * 0.02
    #     elif 1e6 < acpip:
    #         score['avg_cost_per_intellectual_property'] = 90 * 0.02

    # HR系统是否匹配人数（目前总员工人数&已信息化经营模块）
    if data['current_employee_number'] > 50 and '1' not in info_list:
        score['hr_system_match_employee'] = 0
    elif data['current_employee_number'] < 10 and '1' in info_list:
        score['hr_system_match_employee'] = 20 * 0.01
    else:
        score['hr_system_match_employee'] = 100 * 0.01

    # CRM系统是否匹配销售人数（已信息化经营模块&销售团队员工人数）
    if data['sale_team_member_number'] > 20 and '3' not in info_list:
        score['crm_system_match_sale_employee'] = 0
    elif data['sale_team_member_number'] < 5 and '3' in info_list:
        score['crm_system_match_sale_employee'] = 20 * 0.01
    else:
        score['crm_system_match_sale_employee'] = 100 * 0.01

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

    n1 = len(set(info_list).intersection(set(pi_software_list)))
    n2 = len(set(info_list).intersection(set(warehouse_software_list)))
    n3 = len(set(info_list).intersection(set(logistics_software_list)))
    score['inforpart_match_industry'] = 0.01 * 100 / n * (list1 * n1 + list2 * n2 + list3 * n3)

    # 当前融资轮次和已信息化经营模块是否匹配
    if cfr >= 3 > ip:
        score['current_finance_round_match_informatization_part'] = 0
    else:
        score['current_finance_round_match_informatization_part'] = 100 * 0.01

    # 当前融资轮次和企业战略规划来源是否匹配
    if cfr >= 3 and data['strategy_planning_source'] == '0':
        score['current_finance_round_match_strategy_planning_source'] = 0
    elif cfr >= 2 and data['strategy_planning_source'] == '1':
        score['current_finance_round_match_strategy_planning_source'] = 100 * 0.02
    elif cfr >= 2 and data['strategy_planning_source'] == '0':
        score['current_finance_round_match_strategy_planning_source'] = 30 * 0.02
    elif cfr <= 1 and data['strategy_planning_source'] == '2':
        score['current_finance_round_match_strategy_planning_source'] = 90 * 0.02

    else:
        score['current_finance_round_match_strategy_planning_source'] = 80 * 0.02

    # 当前融资轮次和销售渠道类型是否匹配
    if cfr >= 3 and mc <= 4:
        score['current_finance_round_match_marketingchannel'] = 0
    elif cfr <= 1 and mc >= 6:
        score['current_finance_round_match_marketingchannel'] = 80 * 0.02
    else:
        score['current_finance_round_match_marketingchannel'] = 100 * 0.02

    # 当前融资轮次和收入模式类型是否匹配
    if cfr >= 3 and rm <= 4:
        score['current_finance_round_match_revenue_type'] = 0
    elif cfr <= 1 and rm >= 8:
        score['current_finance_round_match_revenue_type'] = 80 * 0.02
    else:
        score['current_finance_round_match_revenue_type'] = 100 * 0.02

    # 人均净利润（净利润/目前总员工人数）
    # netprofit_pe = data['net_profit']/ data['current_employee_number']
    # if netprofit_pe <= 0:
    #     score['netprofit_per_employee'] = 0
    # elif 0 < netprofit_pe < 5e4:
    #     score['netprofit_per_employee'] = 20 * 0.02
    # elif 5e4 < netprofit_pe < 1e5:
    #     score['netprofit_per_employee'] = 35 * 0.02
    # elif 1e5 < netprofit_pe < 2e5:
    #     score['netprofit_per_employee'] = 70 * 0.02
    # elif 2e5 < netprofit_pe < 5e5:
    #     score['netprofit_per_employee'] = 85 * 0.02
    # elif 5e5 < netprofit_pe < 1e6:
    #     score['netprofit_per_employee'] = 95 * 0.02
    # elif 1e6 < netprofit_pe:
    #     score['netprofit_per_employee'] = 100 * 0.02

    # 人均营业收入（营业收入/目前总员工人数）
    # or_pe = data['revenue']/ data['current_employee_number']
    # if 0 < or_pe <= 1e5:
    #     score['operation_revenue_per_employee'] = 10 * 0.02
    # elif 1e5 < or_pe <= 2e5:
    #     score['operation_revenue_per_employee'] = 25 * 0.02
    # elif 2e5 < or_pe <= 5e5:
    #     score['operation_revenue_per_employee'] = 50 * 0.02
    # elif 5e5 < or_pe <= 1e6:
    #     score['operation_revenue_per_employee'] = 75 * 0.02
    # elif 1e6 < or_pe <= 2e6:
    #     score['operation_revenue_per_employee'] = 90 * 0.02
    # elif 2e6 < or_pe <= 3e6:
    #     score['operation_revenue_per_employee'] = 95 * 0.02
    # elif 3e6 < or_pe:
    #     score['operation_revenue_per_employee'] = 100 * 0.02

    # 销售团队人均销售额（营业收入 / 销售团队员工人数）
    # sale_pse = data['revenue']/ data['sale_team_member_number']
    # if 0 < sale_pse <= 1e5:
    #     score['sale_per_sale_employee'] = 5 * 0.02
    # elif 1e5 < sale_pse <= 2e5:
    #     score['sale_per_sale_employee'] = 15 * 0.02
    # elif 2e5 < sale_pse <= 5e5:
    #     score['sale_per_sale_employee'] = 30 * 0.02
    # elif 5e5 < sale_pse <= 1e6:
    #     score['sale_per_sale_employee'] = 65 * 0.02
    # elif 1e6 < sale_pse <= 2e6:
    #     score['sale_per_sale_employee'] = 90 * 0.02
    # elif 2e6 < sale_pse <= 3e6:
    #     score['sale_per_sale_employee'] = 95 * 0.02
    # elif 3e6 < sale_pse:
    #     score['sale_per_sale_employee'] = 100 * 0.02

    # 销售团队人均销售费用（销售费用/销售团队员工人数）
    # saleexp_pse = data['selling_expense']/ data['sale_team_member_number']
    # if 0 <= saleexp_pse < 2e4:
    #     score['sale_expense_per_sale_employee'] = 50 * 0.02
    # elif 2e4 <= saleexp_pse < 5e4:
    #     score['sale_expense_per_sale_employee'] = 70 * 0.02
    # elif 5e4 <= saleexp_pse < 1e5:
    #     score['sale_expense_per_sale_employee'] = 80 * 0.02
    # elif 1e5 <= saleexp_pse < 2e5:
    #     score['sale_expense_per_sale_employee'] = 90 * 0.02
    # elif 2e5 <= saleexp_pse < 3e5:
    #     score['sale_expense_per_sale_employee'] = 100 * 0.02
    # elif 3e5 <= saleexp_pse < 5e5:
    #     score['sale_expense_per_sale_employee'] = 80 * 0.02
    # elif 5e5 <= saleexp_pse < 1e6:
    #     score['sale_expense_per_sale_employee'] = 70 * 0.02
    # elif 1e6 <= saleexp_pse:
    #     score['sale_expense_per_sale_employee'] = 50 * 0.02

    bm_score = 0
    for value in score.values():
        bm_score += value
    return round(bm_score, 2)
