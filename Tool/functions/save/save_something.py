import numpy as np
from CONFIG.database import connect_mysql_rdt_fintech
from log.log import logger
import random

def save_stock_value(VID, SS_R, flag, Modify_time,listtime_ans,gpscore,listtime_h5):
    for key in SS_R.keys():
        if type(SS_R[key]) == np.float64:
            SS_R[key] = SS_R[key].item()
    if type(gpscore) == np.float64:
        gpscore = gpscore.item()
    for key in range(len(listtime_ans)):
        if type(listtime_ans[key]) == np.float64 or type(listtime_ans[key]) == np.int64:
            listtime_ans[key] = listtime_ans[key].item()

    beat = random.randint(70, 95)
    ######数据库操作
    db = connect_mysql_rdt_fintech()
    cursor = db.cursor()

    try:
        sql_find = 'select count(*) from t_general_final_result where valuation_id=%s'
        cursor.execute(sql_find, [VID])
        find = list(cursor.fetchall())[0][0]
        if int(find) == 0:
            sql_insert = 'Insert into t_general_final_result(generalresult_estimatevalue_basic,generalresult_estimatevalue_optimistic,' \
                         'generalresult_estimatevalue_pessimistic,generalresult_marketability_premium,valuation_id,' \
                         'generalresult_controlright_premium,generalresult_score,generalresult_peervalue_basic,' \
                         'generalresult_peervalue_optimistic,generalresult_peervalue_pessimistic,c_time,m_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) '
            sql_value = [SS_R["MV_avg"], SS_R["MV_max"], SS_R["MV_min"], 0, VID, 0, SS_R["score"], SS_R["p_avg"],
                         SS_R["p_max"], SS_R["p_min"], Modify_time, Modify_time]

            cursor.execute(sql_insert, sql_value)
        else:
            sql_insert = 'Update t_general_final_result set generalresult_estimatevalue_basic=%s,' \
                         'generalresult_estimatevalue_optimistic=%s,generalresult_estimatevalue_pessimistic=%s,' \
                         'generalresult_marketability_premium=%s,generalresult_controlright_premium=%s,' \
                         'generalresult_score=%s,generalresult_peervalue_basic=%s,generalresult_peervalue_optimistic=%s,' \
                         'generalresult_peervalue_pessimistic=%s,m_time=%s where valuation_id=%s'
            sql_value = [SS_R["MV_avg"], SS_R["MV_max"], SS_R["MV_min"], 0, 0, SS_R["score"], SS_R["p_avg"],
                         SS_R["p_max"], SS_R["p_min"], Modify_time, VID]

            cursor.execute(sql_insert, sql_value)

        sql_find_prospect = 'select count(*) from t_valuation_prospect_output where valuation_id=%s'
        cursor.execute(sql_find_prospect, [VID])
        find = list(cursor.fetchall())[0][0]
        if int(find) == 0:
            sql_insert = 'Insert into t_valuation_prospect_output(prospect_ipoprobability,prospect_rapidipodate,' \
                         'prospect_rapidipomarket,prospect_ipoprediction,prospect_growthpotential_score,' \
                         'valuation_id,prospect_profitpotential_score,prospect_operatingefficiency_score,' \
                         'prospect_capitalstructure_score,prospect_normativegovernance_score,' \
                         'prospect_financingchanneladvice,prospect_financingprobability,prospect_leading_peers,c_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) '
            sql_value = [None, listtime_ans[1], listtime_ans[0], str(listtime_h5), gpscore, VID, None, None, None, None,None,None,beat,Modify_time]

            cursor.execute(sql_insert, sql_value)
        else:
            sql_insert = 'Update t_valuation_prospect_output set prospect_ipoprobability=%s,prospect_rapidipodate=%s,' \
                         'prospect_rapidipomarket=%s,prospect_ipoprediction=%s,prospect_growthpotential_score=%s,' \
                         'prospect_profitpotential_score=%s,prospect_operatingefficiency_score=%s,' \
                         'prospect_capitalstructure_score=%s,prospect_normativegovernance_score=%s,' \
                         'prospect_financingchanneladvice=%s,prospect_financingprobability=%s,prospect_leading_peers=%s,c_time=%s where valuation_id=%s'
            sql_value = [None, listtime_ans[1], listtime_ans[0], str(listtime_h5), gpscore, None, None, None, None,None,None,beat,Modify_time, VID]
            cursor.execute(sql_insert, sql_value)
    except Exception as e:
        logger(e)
        cursor.close()
        db.close()
    db.commit()
    cursor.close()
    db.close()


# 收入，市场， 期权
def save_vr(VID, vr_result, proportion, time, flag):
    db = connect_mysql_rdt_fintech()
    cursor = db.cursor()
    valuation_methods = [100000, 200000, 400000]
    valuation_results = [["avg_abs", "max_abs", "min_abs","score_abs"], ["avg_mkt", "max_mkt", "min_mkt","score_mkt"],
                         ["avg_sam", "max_sam", "min_sam", "score_sam"]]
    try:
        sql_find = 'select count(*) from t_scenario_result where valuation_id=%s'
        cursor.execute(sql_find, [VID])
        find = list(cursor.fetchall())[0][0]
        if int(find) == 0:
            for i in range(3):
                insert_value = [valuation_methods[i], vr_result[valuation_results[i][0]], vr_result[valuation_results[i][1]],
                                    vr_result[valuation_results[i][2]], 0, VID,0, proportion[i], vr_result[valuation_results[i][3]], time, time]
                insert_sql = 'Insert into t_scenario_result (scenario_valuationmethod,scenario_estimatevalue_basic,' \
                                 'scenario_estimatevalue_optimistic,scenario_estimatevalue_pessimistic,' \
                                 'scenario_marketability_premium,valuation_id,scenario_controlright_premium,' \
                                 'scenario_weight,scenario_score,c_time,m_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                cursor.execute(insert_sql, insert_value)
        else:
            for i in range(3):
                update_value = [vr_result[valuation_results[i][0]], vr_result[valuation_results[i][1]],
                                        vr_result[valuation_results[i][2]], 0, 0, proportion[i], vr_result[valuation_results[i][3]], time,VID,valuation_methods[i]]
                update_sql = 'Update t_scenario_result set scenario_estimatevalue_basic=%s,' \
                                 'scenario_estimatevalue_optimistic=%s,scenario_estimatevalue_pessimistic=%s,' \
                                 'scenario_marketability_premium=%s,scenario_controlright_premium=%s,' \
                                 'scenario_weight=%s,scenario_score=%s,m_time=%s where valuation_id=%s and scenario_valuationmethod=%s'
                cursor.execute(update_sql, update_value)
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        logger(e)
        cursor.close()
        db.close()
