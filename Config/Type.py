from Valuatoin import *

valuation_types = {0: valuation_old,  # PC端旧版估值
                   1: valuation_financial,  # PC端旧版金融公司估值
                   2: valuation_real_estate,  # PC端旧版房地产公司估值
                   3: valuation_venture_capital,  # PC端旧版风险投资估值
                   5: valuation_mini,  # 30秒估值
                   6: valuation_lite,  # 新版估值
                   }

market_type = {0: "沪深A股",
               1: "新三板",
               2: "区域股权交易所",
               3: "海外主板",
               4: "海外创业板",
               6: "科创板"
               }
