# -*- coding: utf-8 -*-：
from Config.mongodb import read_mongo_limit


def read_data(bm_id, flag):

    df = read_mongo_limit("rdt_fintech", "NewBm", {'_id': bm_id}, None)
    try:
        company_operation_duration = df["B1001"].values[0]
        current_employee_number = df["B1201"].values[0]
        entrepreneur_management_duration = df["B1002"].values[0]
        post_one_year_new_employee_number = df["B1301"].values[0]
        recruit_position_type_trend = df["B1302"].values[0]
        research_team_employee_number = df["B1203"].values[0]
        sale_team_member_number = df["B1202"].values[0]
        actual_controller_shareholding_percent = df["B2001"].values[0]
        current_finance_round = df["B2101"].values[0]
        capital_market = df["B2102"].values[0]
        informatization_part = df["B2201"].values[0]
        strategy_planning_source = df["B2301"].values[0]
        authorization_utility_model_number = df["B3001"].values[0]
        authorization_patents_number = df["B3002"].values[0]
        authorization_software_copyright_number = df["B3004"].values[0]
        research_expense_percent_to_total_cost = df["B3104"].values[0]
        income_tax_rate = df["B3103"].values[0]
        fremdness_supplier_cost_percent = df["B4001"].values[0]
        fremdness_client_revenue_percent = df["B4002"].values[0]
        genericcompetitivestrategy = df["B4102"].values[0]
        industry_chain_position = df["B4101"].values[0]
        marketingchannel_type = df["B4202"].values[0]
        revenue_mode = df["B4205"].values[0]

        data = {'company_operation_duration': company_operation_duration,
        'current_employee_number': current_employee_number,
        'entrepreneur_management_duration': entrepreneur_management_duration,
        'post_one_year_new_employee_number': post_one_year_new_employee_number,
        'recruit_position_type_trend': recruit_position_type_trend,
        'research_team_employee_number': research_team_employee_number,
        'sale_team_member_number': sale_team_member_number,
        'actual_controller_shareholding_percent': actual_controller_shareholding_percent,
        'current_finance_round': current_finance_round,
        'capital_market': capital_market,
        'informatization_part': informatization_part,
        'strategy_planning_source': strategy_planning_source,
        'authorization_utility_model_number': authorization_utility_model_number,
        'authorization_patents_number': authorization_patents_number,
        'authorization_software_copyright_number': authorization_software_copyright_number,
        'research_expense_percent_to_total_cost': research_expense_percent_to_total_cost,
        'income_tax_rate': income_tax_rate,
        'fremdness_supplier_cost_percent': fremdness_supplier_cost_percent,
        'fremdness_client_revenue_percent': fremdness_client_revenue_percent,
        'genericcompetitivestrategy': genericcompetitivestrategy,
        'industry_chain_position': industry_chain_position,
        'marketingchannel_type': marketingchannel_type,
        'revenue_mode': revenue_mode}

        if flag == 1:
            entrepreneur_relevent_experience = df["B1003"].values[0]
            name = df["B1101"].values[0]
            position = df["B1102"].values[0]
            background_intro = df["B1103"].values[0]
            master_employee_pct = df["B1204"].values[0]
            phd_employee_pct = df["B1205"].values[0]
            research_team_avg_employee_duration = df["B1206"].values[0]
            promition_regulation_status = df["B1401"].values[0]
            company_culture_effect = df["B1402"].values[0]
            esop = df["B2002"].values[0]
            shareholder_name = df["B2003"].values[0]
            shareholder_share_pct = df["B2004"].values[0]
            informatization_expense_pct = df["B2202"].values[0]
            authorization_appearance_patents_number = df["B3003"].values[0]
            authorization_work_copyright_number = df["B3005"].values[0]
            registed_trademark_number = df["B3006"].values[0]
            patents_implement_pct = df["B3007"].values[0]
            last_year_research_expensed = df["B3101"].values[0]
            last_year_research_capitalized = df["B3102"].values[0]
            company_identification = df["B3201"].values[0]
            outsourcing_status = df["B4103"].values[0]
            selling_expenses_to_total_pct = df["B4201"].values[0]
            revenue_pct_from_first_five_customers = df["B4203"].values[0]
            purchase_pct_from_first_five_supplier = df["B4204"].values[0]
            concept_tag = df["B4301"].values[0]
            main_product_lifecycle = df["B4401"].values[0]
            main_product_market_share = df["B4402"].values[0]
            company_lifecycle = df["B5001"].values[0]
            barriers_to_entry = df["B5002"].values[0]
            substitutes_same_industry_quantity = df["B5101"].values[0]
            substitutes_different_industry_status = df["B5102"].values[0]
            market_capacity = df["B5201"].values[0]
            correlation_trade_revenue_pct = df["B6001"].values[0]
            penalty_status = df["B6101"].values[0]
            department_status = df["B6202"].values[0]
            government_assistance_to_netprofit_pct = df["B6002"].values[0]
            company_approbation_system = df["B6201"].values[0]
            environmental_cost = df["B6003"].values[0]

            data_detail = {
                "entrepreneur_relevent_experience": entrepreneur_relevent_experience,
                "name": name,
                "position": position,
                "background_intro": background_intro,
                "master_employee_pct": master_employee_pct,
                "phd_employee_pct": phd_employee_pct,
                "research_team_avg_employee_duration": research_team_avg_employee_duration,
                "promition_regulation_status": promition_regulation_status,
                "company_culture_effect": company_culture_effect,
                "esop": esop,
                "shareholder_name": shareholder_name,
                "shareholder_share_pct": shareholder_share_pct,
                "informatization_expense_pct": informatization_expense_pct,
                "authorization_appearance_patents_number": authorization_appearance_patents_number,
                "authorization_work_copyright_number": authorization_work_copyright_number,
                "registed_trademark_number": registed_trademark_number,
                "patents_implement_pct": patents_implement_pct,
                "last_year_research_expensed": last_year_research_expensed,
                "last_year_research_capitalized": last_year_research_capitalized,
                "company_identification": company_identification,
                "outsourcing_status": outsourcing_status,
                "selling_expenses_to_total_pct": selling_expenses_to_total_pct,
                "revenue_pct_from_first_five_customers": revenue_pct_from_first_five_customers,
                "purchase_pct_from_first_five_supplier": purchase_pct_from_first_five_supplier,
                "concept_tag": concept_tag,
                "main_product_lifecycle": main_product_lifecycle,
                "main_product_market_share": main_product_market_share,
                "company_lifecycle": company_lifecycle,
                "barriers_to_entry": barriers_to_entry,
                "substitutes_same_industry_quantity": substitutes_same_industry_quantity,
                "substitutes_different_industry_status": substitutes_different_industry_status,
                "market_capacity": market_capacity,
                "correlation_trade_revenue_pct": correlation_trade_revenue_pct,
                "penalty_status": penalty_status,
                "department_status": department_status,
                "government_assistance_to_netprofit_pct": government_assistance_to_netprofit_pct,
                "company_approbation_system": company_approbation_system,
                "environmental_cost": environmental_cost
            }
            data.update(data_detail)
    except:
        current_finance_round = df["B2101"].values[0]
        capital_market = df["B2102"].values[0]
        data = {
            'current_finance_round': current_finance_round,
            'capital_market': capital_market
        }

    return data


# read_data(99)
