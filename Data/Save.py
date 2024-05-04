from math import sqrt
import numpy as np
from datetime import datetime
import random

from Supplement.Score import effectiveness as eft
from Data.Conn import *
import Config.Database
from Config.Database import Database as Db, Fields as Fd
from Config.About import version
from Config.global_V import GlobalValue
from Tool.functions.adjust_accuracy import adjust_accuracy_mini, adjust_accuracy
from Tool.functions.growthpotentialscore.normal import get_growth_potential_pscore

__all__ = ['save', 'save_mini']


def save(vid, doc, mode, orig_bal, orig_flow, ipo):
    gen_record = save_general(doc, mode, orig_bal, orig_flow)
    model_record = save_model(doc)
    traceback_record = save_traceback(doc)
    res = save_lite(gen_record, model_record)
    res['time'] = datetime.now()
    res["traceback"] = traceback_record
    market = dict()
    for key, value in doc["ipo_prospect"].items():
        if value != -1:
            market[key] = value
    order_market = sorted(market.items(), key=lambda x: x[1])
    if order_market:
        brand = order_market[0][0]
        year = order_market[0][1]
    else:
        brand = ""
        year = 99
    beat = random.randint(70, 95)
    ipo = 1 if ipo else 0
    gpscore = get_growth_potential_pscore(doc["hypo"]["rg"])
    res["ipo_prospect"] = {"IpoMarket": {brand: year}, "GPScore": gpscore, "LeadingPeers": beat, "ipo": ipo}
    res["doc"] = doc
    db_config = Config.Database.ConnDB
    tb = Db.result_valuation['tb']
    with ConnMongo(**db_config.rdt_mongo) as conn:
        conn(tb).upsert(where={'_id': vid}, data=res)
    if "try" in doc["hypo"]:
        adjust_accuracy(vid, doc["hypo"]["try"])
    else:
        adjust_accuracy(vid)
    return gen_record, model_record


def save_lite(gen_record, model_record):
    result = dict()
    result["val"] = {}
    result["val"]["syn"] = [gen_record[Fd.pess_mv], gen_record[Fd.base_mv], gen_record[Fd.optm_mv]]
    result["val"]["peer_value"] = [gen_record[Fd.pess_p], gen_record[Fd.base_p], gen_record[Fd.optm_p]]
    result["val"]["score"] = gen_record[Fd.score]
    result["val"][Fd.lr_discount_p] = gen_record[Fd.lr_discount_p]
    result["val"][Fd.cp_premium_p] = gen_record[Fd.cp_premium_p]
    result["val"][Fd.effect] = gen_record[Fd.effect]
    result['version'] = version
    result['val']["detail"] = {}
    for i in model_record:
        result['val']["detail"][str(i[Fd.method])] = {"syn": [i[Fd.mpess_mv], i[Fd.mbase_mv], i[Fd.moptm_mv]],
                                                      "wt": i[Fd.mwt], "score": i[Fd.mscore],
                                                      Fd.mliqrisk_mv: i[Fd.mliqrisk_mv],
                                                      Fd.mcontrol_mv: i[Fd.mcontrol_mv]}

    return result


def save_general(doc, mode, orig_bal, orig_flow):
    share = doc['share']
    dgt = int(doc['hypo']['dgt'])
    lrp = round((doc['dcf_detail']['lr'] + doc['mkt_detail']['lr']) / 2 / share, dgt)
    cpp = round((doc['dcf_detail']['cp'] + doc['mkt_detail']['cp']) / 2 / share, dgt)

    peer_score = min(sqrt(len(doc['peer_data'])), 5)  # 对标公司得分，对标公司越多分越高，25家及以上满分 [0, 5]

    bm_score = min(sqrt(len(doc['bm'])), 5)  # 商业模式得分，项目越多得分越高，25项及以上满分 [0, 5]

    predict_score = max(5 - 0.2 * pow(doc['hypo']['years'] - len(doc['fs']), 2), 0)  # 财务预测得分，未预测年越多分越低，差5年0分 [0, 5]

    dcf_score = 0
    for sub_model in doc['dcf_detail']:
        if type(sub_model) is dict:
            dcf_score += sub_model['wt']
    dcf_score = min(dcf_score, 10)  # 收入法得分 [0, 10]

    mkt_score = 0
    for sub_model in doc['mkt_detail']:
        if type(sub_model) is dict:
            mkt_score += sub_model['wt']
    mkt_score = min(mkt_score, 10)  # 市场法得分，累计权重越高分越高 [0, 10]

    opt_score = 0
    for sub_model in doc['opt_detail']:
        if type(sub_model) is dict:
            opt_score += sub_model['wt']
    opt_score = min(opt_score, 5)  # 期权法得分，累计权重越高分越高 [0, 5]

    aba_score = 0
    for sub_model in doc['aba_detail']:
        if type(sub_model) is dict:
            aba_score += sub_model['wt']
    aba_score = min(aba_score, 5)  # 资产得分，累计权重越高分越高 [0, 5]

    # net_score = 0
    # for sub_model in doc['net_detail']:
    #     if type(sub_model) is dict:
    #         net_score += sub_model['wt']
    # net_score = min(net_score, 5)

    mode_score = mode * 1.5 + 0.5  # 估值模式得分，模式越高级分越高 [0, 5]

    score = peer_score + bm_score + predict_score + dcf_score + mkt_score + opt_score + aba_score + mode_score
    # 总分 [0, 50]

    effect = eft(orig_bal, orig_flow, doc)

    data_dict = {Fd.base_mv: doc['syn_val'][1],  # 基准估值
                 Fd.optm_mv: doc['syn_val'][2],  # 乐观估值
                 Fd.pess_mv: doc['syn_val'][0],  # 悲观估值
                 Fd.base_p: round(doc['syn_val'][1] / share, dgt),  # 每股基准估值
                 Fd.optm_p: round(doc['syn_val'][2] / share, dgt),  # 每股乐观估值
                 Fd.pess_p: round(doc['syn_val'][0] / share, dgt),  # 每股悲观估值
                 Fd.lr_discount_p: lrp,  # 流动性折价
                 Fd.cp_premium_p: cpp,  # 控制权溢价
                 Fd.score: round(score, dgt),  # 估值总评分
                 Fd.version: version,  # 估值算法版本
                 Fd.effect: round(effect, 8),  # 估值有效性
                 }

    return data_dict


def save_model(doc):
    # method_id = dict(dcf=100000, mkt=200000, opt=400000, aba=300000, net=620001)
    methods = doc['syn_wt']
    dgt = int(doc['hypo']['dgt'])
    model_info = []

    for method in methods:
        name = method + '_detail'
        method_detail = doc[name]
        lr = method_detail['lr'] if 'lr' in method_detail else 0
        cp = method_detail['cp'] if 'cp' in method_detail else 0
        scores = []
        for sub_method, info in method_detail.items():
            if type(info) is dict:
                try:
                    scores.append(info['wt'])
                except KeyError:
                    continue
        score = np.average(scores) - np.std(scores) + sqrt(len(scores))
        score = round(score, dgt)
        method_dict = {Fd.mbase_mv: method_detail['base'],
                       Fd.moptm_mv: method_detail['optm'],
                       Fd.mpess_mv: method_detail['pess'],
                       Fd.mliqrisk_mv: lr,
                       Fd.mcontrol_mv: cp,
                       Fd.mscore: score,
                       Fd.mwt: methods[method][1],
                       Fd.method: GlobalValue.MethodId[method],
                       }

        model_info.append(method_dict)
    return model_info


def save_traceback(doc):
    share = doc['share']
    dgt = int(doc['hypo']['dgt'])
    tb_data = doc['traceback']
    data_list = []
    for ke, mv in tb_data:
        p = round(mv / share, dgt)
        data = {Fd.tb_ke: ke,
                Fd.tb_mv: mv,
                Fd.tb_p: p}
        data_list.append(data)
        if mv < 0:
            break
    return data_list


def save_mini(vid, doc):
    doc['time'] = datetime.now()
    db_config = Config.Database.ConnDB
    tb = Db.result_valuation['tb']
    with ConnMongo(**db_config.rdt_mongo) as conn:
        conn(tb).upsert(where={'_id': vid}, data=doc)
    # 调整估值精度
    adjust_accuracy_mini(vid)
