# -*- coding: utf-8 -*-：

# 保存结果数据
from Config.mongodb import save_mongo


def save_data(result, dloc, profit_growth_rate, gross_profit_ratio, cost_ratio, expense_ratio, risk_premium, VID):

    res_dict = {"VID": VID, "business_model_score": result, "dloc_coef": dloc,
                "profit_growth_rate_coef": profit_growth_rate,"gross_profit_ratio": gross_profit_ratio,
                "cost_ratio": cost_ratio, "expense_ratio": expense_ratio, "special_risk_premium_coef": risk_premium}

    save_mongo("rdt_fintech", "BM_OUT", res_dict)

