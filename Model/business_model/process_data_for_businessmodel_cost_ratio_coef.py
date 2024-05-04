# -*- coding: utf-8 -*-：

# 分数越高，成本率越低，60基准值


def process_data_cost_ratio_coef(data, financial_report_data):
    score = {}

    # 招聘倾向
    s = 0
    if data['recruit_position_type_trend'] == '0':
        s = 65
    elif data['recruit_position_type_trend'] == '1':
        s = 70
    elif data['recruit_position_type_trend'] == '2':
        s = 55
    elif data['recruit_position_type_trend'] == '3':
        s = 40
    score['recruit_position_type_trend'] = s * 0.2

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

    # 采购自外国供应商的成本占总支出
    if data['fremdness_supplier_cost_percent'] == 0:
        s = 60
    elif 0 < data['fremdness_supplier_cost_percent'] <= 10:
        s = 75
    elif 10 < data['fremdness_supplier_cost_percent'] <= 30:
        s = 65
    elif 30 < data['fremdness_supplier_cost_percent'] <= 70:
        s = 40
    elif 70 < data['fremdness_supplier_cost_percent'] <= 100:
        s = 20
    score['fremdness_supplier_cost_percent'] = s * 0.25

    # 基本竞争策略
    if data['genericcompetitivestrategy'] == '0':
        s = 100
    elif data['genericcompetitivestrategy'] == '1':
        s = 60
    elif data['genericcompetitivestrategy'] == '2':
        s = 40
    score['genericcompetitivestrategy'] = s * 0.2

    # 产业链位置
    if data['industry_chain_position'] == '0':
        s = 40
    elif data['industry_chain_position'] == '1':
        s = 60
    elif data['industry_chain_position'] == '2':
        s = 75
    score['industry_chain_position'] = s * 0.1

    # 平均每年人员扩张速度（目前总员工人数/公司成立年数）
    eepy = data['current_employee_number'] / data['company_operation_duration']
    if 0 < eepy <= 100:
        s = 60
    elif 100 < eepy:
        s = 40
    score['employee_expansion_per_year'] = s * 0.1

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
    score['employee_expansion_post_one_year'] = s * 0.15

    bm_score = 0
    for value in score.values():
        bm_score += value
    return round(bm_score, 2)
