from functions.errorinfo import wirte_error
from log.log import logger
from valuation_models.valuation_models_factory import ValuationModels,ValuationModelsFactory
from valuation_models.venture_investment.summary import get_summary_result

from hypothesis.wacc import WACC
from CONFIG.global_V import GlobalValue
from CONFIG.database import connect_mysql_fuyoubank_security


def backup_re_forquotation_abs(fr_output,forN,forRi,forEva,forApv,Cost_R,CS,pid,flag,abs_R):

    abs_re={}
    #新建估值模型工厂
    VMF=ValuationModelsFactory()
    NOPAT=VMF.choose_valuation_model(ValuationModels.NOR_NOPAT)
    EVA=VMF.choose_valuation_model(ValuationModels.NOR_EVA)
    RIM=VMF.choose_valuation_model(ValuationModels.NOR_RIM)
    APV = VMF.choose_valuation_model(ValuationModels.NOR_APV)

    for e in abs_R.keys():
        if e not in abs_re.keys(): #如果方法不存在于abs_re中，初始化
            abs_re[e]={}
        for e1 in abs_R[e].keys():
            if abs_R[e][e1] == {} or abs_R[e][e1]['score'] == 0:
                abs_re[e][e1]=False
            else:
                abs_re[e][e1]={}
                for item in ['MV_max','MV_min','MV_avg']:
                    abs_re[e][e1][item]=[]


                for re in GlobalValue.REQUIRE_RETURN:
                    re=re/100.0
                    wacc = WACC(re, fr_output, CS)

                    if e == 'rim':
                        # abs_RIM
                        ABS_R = RIM.get_output(fr_output, wacc, forRi, Cost_R)
                    elif e == 'nopat':
                        # abs_NOPAT
                        ABS_R = NOPAT.get_output(fr_output, wacc, forN, Cost_R)
                    elif e == 'eva':
                        # abs_EVA
                        ABS_R = EVA.get_output(fr_output, wacc, forEva, Cost_R)
                    else:
                        # abs_APV
                        ABS_R = APV.get_output(fr_output, wacc, forApv, Cost_R)
                    for item in ['MV_max', 'MV_min', 'MV_avg']:
                        if ABS_R[e1] == {} or ABS_R[e1]['score'] == 0:
                            temp = False
                        else:
                            temp = ABS_R[e1][item]
                        abs_re[e][e1][item].append(temp)
    #存
    db = connect_mysql_fuyoubank_security()
    cursor = db.cursor()
    try:
        for key1,value in abs_re.items():
            for key2,value2 in value.items():
                if abs_re[key1][key2]==False:
                    continue
                tablename='vr_abs_' + key1+"_"+key2
                sql_find = 'select count(*) from ' + tablename + ' where pid=%s and adjustment=%s'
                cursor.execute(sql_find, [pid, flag])
                find = list(cursor.fetchall())[0][0]
                if int(find) == 0:
                    wirte_error("数据库abs子方法结果插入备用re时没有找到该插入的条目\n")
                else:
                    abs_update_value = [str(GlobalValue.REQUIRE_RETURN),str(value2['MV_max']),str(value2['MV_avg']),
                                    str(value2['MV_min']),pid, flag]
                    abs_update_sql = 'Update ' + tablename + ''' set re_index_backup=%s,result_max_backup=%s,
                    result_avg_backup=%s,result_min_backup=%s where  pid=%s and adjustment=%s'''
                    cursor.execute(abs_update_sql, abs_update_value)
        db.commit()
    except Exception as e:
        logger(e)
    finally:
        cursor.close()
        db.close()

def backup_re_forquotation_vi(predict,finance_plan,var_mulpA,var_mulp3,indus_DEratio,amount_plan,interval,remain_round,
                              campany_scal,indus_dtol,indus_turnover,pid):
    vi_re={}
    #新建估值工场
    VMF = ValuationModelsFactory()
    VI_SAM = VMF.choose_valuation_model(ValuationModels.VI_SAM)
    VI_NOR = VMF.choose_valuation_model(ValuationModels.VI_NOR)

    for item in ['MV_max', 'MV_min', 'MV_avg']:
        vi_re[item] = []

    for re in GlobalValue.REQUIRE_RETURN:
        re = re / 100.0
        ans_normal = VI_NOR.get_VC2(predict, finance_plan, var_mulpA, var_mulp3, indus_DEratio, re, amount_plan,
                             GlobalValue.MUTILPLIER,interval,remain_round)
        ans_samuelson={}
        if campany_scal['L']!=0:
            ans_samuelson = VI_SAM.get_samuelson_results(predict, finance_plan, campany_scal, indus_DEratio, indus_dtol, re,
                                          indus_turnover, amount_plan, GlobalValue.MUTILPLIER, interval, remain_round)

        summary_result = get_summary_result(ans_normal, ans_samuelson)

        for item in ['MV_max', 'MV_min', 'MV_avg']:
            if summary_result != False:
                vi_re[item].append(summary_result[item])
            else:
                vi_re[item].append(False)


    #存
    db = connect_mysql_fuyoubank_security()
    cursor = db.cursor()
    try:
        sql_find = 'select count(*) from valuation_simple_venturecapital_model_output where pid=%s'
        cursor.execute(sql_find, [pid])
        find = list(cursor.fetchall())[0][0]
        if int(find) == 0:
            wirte_error("数据库风险投资lite方法结果插入备用re时没有找到该插入的条目\n")
        else:
            vi_update_value = [str(GlobalValue.REQUIRE_RETURN), str(vi_re['MV_max']), str(vi_re['MV_avg']),
                                str(vi_re['MV_min']), pid]
            vi_update_sql = '''Update valuation_simple_venturecapital_model_output set re_index_backup=%s,result_max_backup=%s,
                            result_avg_backup=%s,result_min_backup=%s where  pid=%s '''
            cursor.execute(vi_update_sql, vi_update_value)
            db.commit()
    except Exception as e:
        logger(e)
    finally:
        cursor.close()
        db.close()

#注意不包括风投的sam模型，(金融的sam不需要rebackup)只有正常（精简，精细）的samuelson
def backup_re_forquotation_sam(name,sam_input,fr_output,CS,pid,flag):
    sam_re={}
    for item in ['MV_max', 'MV_min', 'MV_avg']:
        sam_re[item] = []

    VMF=ValuationModelsFactory()
    SAM=VMF.choose_valuation_model(name)


    for re in GlobalValue.REQUIRE_RETURN:
        re = re / 100.0
        wacc = WACC(re, fr_output, CS)
        sam_input['wacc']=wacc['wacc_avg']
        sam_result = SAM.valuation_samuelson(sam_input)[GlobalValue.SAM_NAME]
        for item in ['MV_max', 'MV_min', 'MV_avg']:
            if sam_result != False:
                sam_re[item].append(sam_result[item])
            else:
                sam_re[item].append(False)

    #存

    db = connect_mysql_fuyoubank_security()
    cursor = db.cursor()
    try:
        sql_find = 'select count(*) from '+GlobalValue.SAM_NAME+' where pid=%s and adjustment=%s'
        cursor.execute(sql_find, [pid,flag])
        find = list(cursor.fetchall())[0][0]
        if int(find) == 0:
            wirte_error("数据库正常估值samuelson方法结果插入备用re时没有找到该插入的条目\n")
        else:
            sam_update_value = [str(GlobalValue.REQUIRE_RETURN), str(sam_re['MV_max']), str(sam_re['MV_avg']),
                                str(sam_re['MV_min']), pid,flag]
            sam_update_sql = 'Update '+GlobalValue.SAM_NAME+''' set re_index_backup=%s,result_max_backup=%s,
                            result_avg_backup=%s,result_min_backup=%s where  pid=%s and  adjustment=%s'''
            cursor.execute(sam_update_sql, sam_update_value)
            db.commit()
    except Exception as e:
        logger(e)
    finally:
        cursor.close()
        db.close()

    # # 新增存储货币单位
    # db = connect_mysql_fuyoubank_security()
    # cursor = db.cursor()
    # try:
    #     sql_find = 'select currency, company_id from parent where id=%s'
    #     cursor.execute(sql_find, [pid])
    #     find = list(cursor.fetchall())[0]
    #     sql = 'Update quotation_company_basic_info set currency_unit=%s where company_id=%s'
    #     cursor.execute(sql, [find[0], find[1]])
    #     db.commit()
    # except Exception as e:
    #     logger(e)
    # finally:
    #     cursor.close()
    #     db.close()
