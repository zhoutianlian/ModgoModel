# -*- coding: utf-8 -*-：
from Algorithm.Average import synthesis_mini, weight
from Config.About import version
from Data.Conn import ConnMongo, ConnMysql
from Data.Read import prepare, FinStm
from Evaluate.IPO import IPOProspect
from Report.Log import logger
from Tool.Util import merge_data, change_format
from Config.global_V import GlobalValue


def run_mini(vid: int, eid: int, saving: bool = True, *args, **kwargs):
    """
    执行极速估值的方法
    :param vid:
    :param eid: 公司id
    :param saving: 是否将结果保存到数据库
    :param args: 备用字段
    :param kwargs: 备用字段
    :return:
    """
    # 导入工程包
    from Data.Read import read_all_mini, read_ipo
    from Data.Save import save_mini
    from Algorithm.RGRAlgo import h_model
    from Process.Valuate import dcf_valuator_mini, mkt_valuator_mini, opt_valuator_mini, net_valuator_mini
    from Algorithm.GuessFS import guess_na
    # 导入通用包
    import pandas as pd
    from datetime import datetime
    from numpy import average

    root, loop, doc, db_config, db, fd = prepare()

    # 读取估值信息
    with ConnMysql(**db_config.rdt_mysql) as conn:
        tb, select = db.enterprise['tb'], db.enterprise['select']
        com_data = conn(tb).find_one(where={'id': eid}, select=select)

    with ConnMongo(**db_config.tyc_mongo) as conn:
        tb, select = db.tyc['tb'], db.tyc['select']
        tyc_data = conn(tb).find_one(where={'name': com_data["enterprise_name"]}, select=select)

    with ConnMongo(**db_config.rdt_mongo) as conn:
        tb, select = db.record['tb'], db.record['select']
        vid_data = conn(tb).find_one(where={'_id': vid}, select=select)

    vid_data = merge_data(vid_data, tyc_data)

    with ConnMongo(**db_config.rdt_mongo) as conn:
        tb, select = db.ps['tb'], db.ps['select']
        ps_data = conn(tb).find_one(where={'_id': vid_data["flowId"][0]}, select=select)

    # 存储录入数据（和查询的GICS代码）
    if fd.mhitech not in vid_data:
        vid_data[fd.mhitech] = []
    doc['input'] = dict(name=com_data[fd.mname], rev=ps_data[fd.mrev], profit=ps_data[fd.mprofit],
                        gics=vid_data[fd.mindcode], staff=vid_data[fd.mstaff], hitech=vid_data[fd.mhitech])

    # 提取财务信息
    fs = {'rev': ps_data[fd.mrev], 'np': ps_data[fd.mprofit], 'share': vid_data[fd.mstock]}
    if fd.mpic in vid_data:
        fs["pic"] = vid_data[fd.mpic]
    bottom = guess_na(**fs)

    # 读取耗时信息
    logger(1, '读取耗时信息')
    indus = vid_data[fd.mindcode]
    name = com_data[fd.mname]
    rg, peer, algo, mkt_mult, net_info, ipo = read_all_mini(loop, fs, name, indus, bottom, spider=0)

    # 存储对标公司数据
    try:
        tyc = net_info['tyc']['TycEnterpriseInfo'][0]
    except Exception as err:
        print(err)
        tyc = dict()

    estab_time = tyc.setdefault('estiblishTime', '')
    if type(estab_time) is not str:
        try:
            etime = datetime.fromtimestamp(int(tyc['estiblishTime'] / 1000))
            etime = etime.strftime('%Y-%m-%d')
        except Exception as err:
            print(err)
            etime = None
    else:
        etime = estab_time

    doc['business'] = dict(regcap=tyc.setdefault('regCapital', 0),  # 注册资本
                           stock=vid_data[fd.mstock],  # 股本数量
                           pic=tyc.setdefault('actualCapital', 0),  # 实缴资本
                           indus=tyc.setdefault('industry', 0),  # 行业
                           legperson=tyc.setdefault('legalPersonName', 0),  # 法人代表
                           estab_time=etime,  # 成立时间
                           regloc=tyc.setdefault('regLocation', 0),  # 注册地址
                           scope=tyc.setdefault('businessScope', 0))  # 业务范围

    tr = 0.25 if 1 in vid_data[fd.mhitech] else 0.15  # 高新技术企业，税率为0.15，其他为0.25

    # 市场法估值
    logger(1, '市场法估值...')
    mult_adj = 1.13 if 1 in vid_data[fd.mhitech] else 1  # 高新技术企业，乘数提高13%
    mult_adj *= 1.5  # 实际使用后发现乘数偏低，设次参数调整
    mkt_case, mkt_detail = mkt_valuator_mini(peer, fs, mkt_mult, mult_adj, bottom)
    mkt_val, mkt_wt, key_list = synthesis_mini(mkt_case)
    print(mkt_val, mkt_wt, key_list)
    # 整合子模型估值和权重
    mkt_submod_wt = [average(k) for k in zip(*mkt_wt)]
    for submod, val in mkt_case.items():
        if val is not None:
            mkt_case[submod] = (mkt_case[submod], mkt_submod_wt.pop(0))
        else:
            mkt_case[submod] = (mkt_case[submod], 0)
    # 保存市场法详情
    doc['mkt'] = dict(val=mkt_val, submod=mkt_case, detail=mkt_detail)

    # 收入法估值
    ub = peer['ub'].median()
    de = algo['dic'] / (1 - algo['dic'])
    beta = ub * (1 + (1 - tr) * de)
    sprp = 0.05 if 1 in vid_data[fd.mhitech] else 0.08  # 非高新其他风险为0.08 高新其他风险为0.05
    sprp -= 0.03  # 实际使用后发现乘数偏低，设次参数调整
    ke = algo['rf'] + beta * algo['mrp'] + sprp

    rg_list = h_model(rg)
    npm = max(peer['npm'].median(), 0.02)  # 限制目标利润率在 2% 以上
    npm_list = h_model(fs['np'] / fs['rev'], npm)

    dcf_val, dcf_detail = dcf_valuator_mini(fs, rg_list, npm_list, ke, bottom)
    doc['dcf'] = dict(val=dcf_val, detail=dcf_detail)

    # 期权法估值
    kd = 0.12 if 1 in vid_data[fd.mhitech] else 0.15  # 高新债务成本为12% 其他为15%
    kd -= 0.05  # 实际使用后发现乘数偏低，设次参数调整
    wacc = ke * (1 - algo['dic']) + (1 - tr) * algo['dic'] * kd
    opt_val, opt_detail = opt_valuator_mini(fs, rg_list, npm_list, wacc, bottom)
    doc['opt'] = dict(val=opt_val, detail=opt_detail)

    # 网信估值
    net_input = {'code': vid_data[fd.mindcode],
                 'share': vid_data[fd.mstock],
                 'staff': vid_data[fd.mstaff],
                 'tech': vid_data[fd.mhitech],
                 'rev': ps_data[fd.mrev],
                 'np': ps_data[fd.mprofit]}

    net_case, net_detail = net_valuator_mini(root, net_info['tyc'], net_input, peer, mkt_mult, mult_adj, bottom)
    net_val, net_wt, key_list = synthesis_mini(net_case)
    # 整合子模型估值和权重
    net_submod_wt = [average(k) for k in zip(*net_wt)]
    for submod, wt in zip(net_case, net_submod_wt):
        net_case[submod] = (net_case[submod], wt)
    # 保存网信法详情
    doc['net'] = dict(val=net_val, submod=net_case, detail=net_detail)

    val = dict(dcf=dcf_val, mkt=mkt_val, opt=opt_val, net=net_val)

    # 综合估值
    logger(1, '计算综合估值')
    # syn_val, syn_wt, key_list = synthesis_mini(val)
    syn_val, syn_mod_wt, key_list = weight(val)
    # syn_mod_wt = [average(k) for k in zip(*syn_wt)]

    # 存储结果
    # doc['val'] = val
    doc['val'] = {}
    doc['val']["rg"] = rg
    doc['val']['syn'] = syn_val
    if "regCapital" in tyc_data:
        if type(tyc_data["regCapital"]) is str:
            reg = change_format(tyc_data["regCapital"])
        else:
            reg = tyc_data["regCapital"]
        if reg != 0:
            doc['val']['peer_value'] = [i / reg for i in syn_val]
    doc['val']["detail"] = {}
    # for i in [["dcf", 0], ["mkt", 1], ["opt", 2], ["net", 3]]:
    #     doc['val']["detail"][str(GlobalValue.MethodId[i[0]])] = {"syn": list(val[i[0]]), "wt": syn_mod_wt[i[1]]}

    for i in range(len(key_list)):
        doc['val']["detail"][str(GlobalValue.MethodId[key_list[i]])] = {"syn": list(val[key_list[i]]), "wt": syn_mod_wt[i]}

    # doc['val']['wt'] = syn_mod_wt

    doc['version'] = version

    # 上市估计

    if ipo:
        market = ipo
    else:
        ps = {"rev": fs["rev"], "np": fs["np"]}
        fs = FinStm()
        fs.add(ps=ps)
        ipo_evaluator = IPOProspect(fs, syn_val[1], mini=True)
        ipo_prospect = ipo_evaluator.get()

        market = dict()
        for key, value in ipo_prospect.items():
            if value != -1:
                market[key] = value
    order_market = sorted(market.items(), key=lambda x: x[1])
    if order_market:
        brand = order_market[0][0]
        year = order_market[0][1]
    else:
        brand = ""
        year = 99
    ipo = 1 if ipo else 0
    doc["ipo_prospect"] = {"IpoMarket": {brand: year}, "ipo": ipo}
    # 返回值
    # premium = pd.DataFrame(net_detail['net_prem']).apply(lambda x: x.mean()/net_val[1] * syn_val[1], axis=1).to_dict()
    # premium = {k: int(d) for k, d in premium.items()}
    # response = dict(syn_val=syn_val, premium=premium)

    if saving:
        save_mini(vid, doc)
    else:
        # print('>> Response <<\n', response)
        print('>> Document <<\n', doc)
        pass
    return "SUCCESS"
