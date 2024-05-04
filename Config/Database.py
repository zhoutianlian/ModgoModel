# -*- coding: utf-8 -*-：
import os
from Config.CONFIG import config

class ConnDB:
    # sql配置
    sql_host = config['DEFAULT']['sql_host']
    sql_port = int(config['DEFAULT']['sql_port'])
    sql_user = config['DEFAULT']['sql_user']
    sql_password = config['DEFAULT']['sql_password']
    # 访问rdt_fintech/Mysql数据库
    rdt_mysql = dict(db='rdt_fintech',
                     host=sql_host,
                     port=sql_port,
                     user=sql_user,
                     password=sql_password,
                     charset='utf8mb4'
                     )
    # mongo配置
    mongo_host = config['DEFAULT']['mongo_host']
    mongo_port = int(config['DEFAULT']['mongo_port'])
    mongo_user = config['DEFAULT']['mongo_user']
    mongo_password = config['DEFAULT']['mongo_password']
    # 访问rdt_fintech/Mongo数据库
    rdt_mongo = dict(db='rdt_fintech',
                     uri='mongodb://%s:%s@%s:%s/?authSource=rdt_fintech' % (mongo_user, mongo_password, mongo_host, mongo_port))

    # tyc数据库
    tyc_mongo = dict(db='tyc_data',
                     uri='mongodb://%s:%s@%s:%s/?authSource=tyc_data' % (mongo_user, mongo_password, mongo_host, mongo_port))

    # 访问算法数据库
    orig = dict(db='AM_origin', uri='mongodb://%s:%s@%s:%s/?authSource=AM_origin' % (mongo_user, mongo_password, mongo_host, mongo_port))
    base = dict(db='AM_basement', uri='mongodb://%s:%s@%s:%s/?authSource=AM_basement' % (mongo_user, mongo_password, mongo_host, mongo_port))
    hypo = dict(db='AM_hypothesis', uri='mongodb://%s:%s@%s:%s/?authSource=AM_hypothesis' % (mongo_user, mongo_password, mongo_host, mongo_port))

    # 天眼查和爬虫接口
    # 接口配置
    DNS_FLASK = config['DEFAULT']['DNS_FLASK']
    tyc = DNS_FLASK + '/companyInfo?enterpriseName=%s&spider=%s&tyc=%s'
    # 增长率接口mini
    growth_mini = DNS_FLASK + '/revgrowthmini'
    # 增长率接口
    growth = DNS_FLASK + '/revgrowth'
    # Excel存储数据服务
    save = DNS_FLASK + '/saveValuationData'
    # redis
    redis_host = config['DEFAULT']['redis_host']
    redis_port = int(config['DEFAULT']['redis_port'])
    redis_password = config['DEFAULT']['redis_password']
    host = mongo_host
    port = mongo_port
    mq = config['DEFAULT']['DNS_MQ']


def set_db(name):
    # if name == 'product':
    #     ConnDB.rdt_mysql = dict(db='rdt_fintech',
    #                             host='172.19.221.239',
    #                             port=3306,
    #                             user='rdt',
    #                             password='Fu3You3R0D6t',
    #                             charset='utf8mb4'
    #                             )
    #     ConnDB.rdt_mongo = dict(db='rdt_fintech',
    #                             uri='mongodb://hub:hubhub@172.19.221.239:27017/?authSource=admin'
    #                             )
    #
    #     ConnDB.tyc = 'http://127.0.0.1:5001/companyInfo?enterpriseName=%s&spider=%s&tyc=%s'
    #     ConnDB.save = 'http://127.0.0.1:5001/saveValuationData'
    #     # redis
    #     ConnDB.redis_host = "172.19.221.239"
    #     ConnDB.redis_port = 6379
    #     ConnDB.redis_password = "f9Yr3@Dt5S"
    #     ConnDB.host = "172.19.221.239"

    if name == 'test':
        ConnDB.rdt_mysql = dict(db='rdt_fintech',
                                host=config['DEFAULT']['sql_host'],
                                port=int(config['DEFAULT']['sql_port']),
                                user= config['DEFAULT']['sql_user'],
                                password=config['DEFAULT']['sql_password'],
                                charset='utf8mb4'
                                )
        # mongo配置
        mongo_host = config['DEFAULT']['mongo_host']
        mongo_port = int(config['DEFAULT']['mongo_port'])
        mongo_user = config['DEFAULT']['mongo_user']
        mongo_password = config['DEFAULT']['mongo_password']
        # 访问rdt_fintech/Mongo数据库
        ConnDB.rdt_mongo = dict(db='rdt_fintech',
                         uri='mongodb://%s:%s@%s:%s/?authSource=rdt_fintech' % (
                         mongo_user, mongo_password, mongo_host, mongo_port))

        # tyc数据库
        ConnDB.tyc_mongo = dict(db='tyc_data',
                         uri='mongodb://%s:%s@%s:%s/?authSource=tyc_data' % (
                         mongo_user, mongo_password, mongo_host, mongo_port))

        # 访问算法数据库
        ConnDB.orig = dict(db='AM_origin', uri='mongodb://%s:%s@%s:%s/?authSource=AM_origin' % (
        mongo_user, mongo_password, mongo_host, mongo_port))
        ConnDB.base = dict(db='AM_basement', uri='mongodb://%s:%s@%s:%s/?authSource=AM_basement' % (
        mongo_user, mongo_password, mongo_host, mongo_port))
        ConnDB.hypo = dict(db='AM_hypothesis', uri='mongodb://%s:%s@%s:%s/?authSource=AM_hypothesis' % (
        mongo_user, mongo_password, mongo_host, mongo_port))

        # ConnDB.tyc = 'http://192.168.1.79:5001/companyInfo?enterpriseName=%s&spider=%s&tyc=%s'
        ConnDB.tyc = 'http://rdt.flask.modgo.pro/companyInfo?enterpriseName=%s&spider=%s&tyc=%s'
        # 增长率接口mini
        # ConnDB.growth_mini = 'http://192.168.1.79:5001/revgrowthmini'

        ConnDB.growth_mini = 'http://rdt.flask.modgo.pro/revgrowthmini'
        # 增长率接口
        # ConnDB.growth = 'http://192.168.1.79:5001/revgrowth'
        ConnDB.growth = 'http://rdt.flask.modgo.pro/revgrowth'
        # ConnDB.save = 'http://192.168.1.79:5001/saveValuationData'
        ConnDB.save = 'http://rdt.flask.modgo.pro/saveValuationData'
        # redis
        ConnDB.redis_host = config['DEFAULT']['redis_host']
        ConnDB.redis_port = int(config['DEFAULT']['redis_port'])
        ConnDB.redis_password = config['DEFAULT']['redis_password']
        ConnDB.host = mongo_host
        ConnDB.mq = "rdt.rocketmq.modgo.pro:9876"

    elif name == 'local_test':
        ConnDB.rdt_mysql = dict(db='rdt_fintech',
                                host='192.168.2.105',
                                port=3306, user='rdt',
                                password='rdt',
                                charset='utf8mb4'
                                )
        ConnDB.rdt_mongo = dict(db='rdt_fintech',
                                uri='mongodb://hub:hubhub@192.168.2.105:27017/?authSource=admin'
                                )
        ConnDB.orig = dict(db='AM_origin', uri='mongodb://hub:hubhub@192.168.2.105:27017/?authSource=admin')
        ConnDB.base = dict(db='AM_basement', uri='mongodb://hub:hubhub@192.168.2.105:27017/?authSource=admin')
        ConnDB.hypo = dict(db='AM_hypothesis', uri='mongodb://hub:hubhub@192.168.2.105:27017/?authSource=admin')

        ConnDB.tyc = 'http://rdt.flask.modgo.pro/companyInfo?enterpriseName=%s&spider=%s&tyc=%s'
        # 增长率接口mini
        ConnDB.growth_mini = 'http://rdt.flask.modgo.pro/revgrowthmini'
        # 增长率接口
        ConnDB.growth = 'http://rdt.flask.modgo.pro/revgrowth'
        ConnDB.save = 'http://rdt.flask.modgo.pro/saveValuationData'
        ConnDB.redis_host = "192.168.2.105"
        ConnDB.redis_port = 6379
        ConnDB.redis_password = "123123"
        ConnDB.host = "192.168.2.105"
        ConnDB.mq = "rdt.rocketmq.modgo.pro:9876"

    elif name == 'develop':
        ConnDB.rdt_mysql = dict(db='rdt_fintech',
                                host=config['DEFAULT']['sql_host'],
                                port=int(config['DEFAULT']['sql_port']),
                                user=config['DEFAULT']['sql_user'],
                                password=config['DEFAULT']['sql_password'],
                                charset='utf8mb4'
                                )
        # mongo配置
        mongo_host = config['DEFAULT']['mongo_host']
        mongo_port = int(config['DEFAULT']['mongo_port'])
        mongo_user = config['DEFAULT']['mongo_user']
        mongo_password = config['DEFAULT']['mongo_password']
        # 访问rdt_fintech/Mongo数据库
        ConnDB.rdt_mongo = dict(db='rdt_fintech',
                                uri='mongodb://%s:%s@%s:%s/?authSource=rdt_fintech' % (
                                    mongo_user, mongo_password, mongo_host, mongo_port))

        # tyc数据库
        ConnDB.tyc_mongo = dict(db='tyc_data',
                                uri='mongodb://%s:%s@%s:%s/?authSource=tyc_data' % (
                                    mongo_user, mongo_password, mongo_host, mongo_port))

        # 访问算法数据库
        ConnDB.orig = dict(db='AM_origin', uri='mongodb://%s:%s@%s:%s/?authSource=AM_origin' % (
            mongo_user, mongo_password, mongo_host, mongo_port))
        ConnDB.base = dict(db='AM_basement', uri='mongodb://%s:%s@%s:%s/?authSource=AM_basement' % (
            mongo_user, mongo_password, mongo_host, mongo_port))
        ConnDB.hypo = dict(db='AM_hypothesis', uri='mongodb://%s:%s@%s:%s/?authSource=AM_hypothesis' % (
            mongo_user, mongo_password, mongo_host, mongo_port))

        ConnDB.tyc = 'http://192.168.1.79:5001/companyInfo?enterpriseName=%s&spider=%s&tyc=%s'
        # 增长率接口mini
        ConnDB.growth_mini = 'http://192.168.1.79:5001/revgrowthmini'
        # 增长率接口
        ConnDB.growth = 'http://192.168.1.79:5001/revgrowth'
        ConnDB.save = 'http://192.168.1.79:5001/saveValuationData'
        # redis
        ConnDB.redis_host = "192.168.2.114"
        ConnDB.redis_port = 6379
        ConnDB.redis_password = "123123"
        ConnDB.host = "192.168.2.105"

    else:
        print(f'No such environment {name}!')


class Fields:
    """
    数据库字段对照表
    """
    """
    rdt_fintech>t_valuating_record
    """
    eid = 'enterprise_id'  # 企业id
    uid = 'user_id'  # 用户id
    vdate = 'c_time'  # 估值日期
    type = 'val_type'
    input_method = 'val_inputmethod'

    """
    rdt_fintech>t_enterprise_manage_relation
    """
    mStatus = "manage_status"
    mType = "manage_type"

    """
    t_company_industry_code
    """
    code = 'stock_code'  # 股票代码
    gics = 'gics_code'  # GICS代码

    """
    算法数据库
    """
    # 市值
    mv = 'mv'  # 市值
    # 全称
    name = "name"
    # 股本
    share = 'total_capitalshare'  # 总股本
    # beta
    ub = 'beta_no_leverage'  # 无杠杆beta
    std = 'year_volatility'  # 年化波动率
    # 流动资产
    cash = 'a_cash'  # 现金MRQ
    ce = 'a_fvtpl'  # 以公允价值计量且其变动计入当期损益的金融资产MRQ
    ar = 'a_notesreceivablenaccountsreceivable'  # 应收账款和应收票据MRQ
    inv = 'a_inventory'  # 存货MRQ
    # 非流动资产
    ip = 'a_investmentproperties'  # 投资性房地产
    ppe = 'a_fixedassets'  # 固定资产
    cip = 'a_constructioninprogress'  # 在建工程
    ia = 'a_intangibelassets'  # 无形资产
    dev = 'a_researchanddevelopmentcosts'  # 开发支出
    le = 'a_longtermprepaidexpenses'  # 长期待摊费用
    ta = 'a_totalasset'  # 总资产MRQ
    # 流动负债
    ap = 'l_notespayablenaccountspayable'  # 应付账款和应收票据MRQ
    # 非流动负债
    tl = 'l_totalliabilities'  # 总负债MRQ
    # 报表附注
    rd = 'RDExpenditure'  # 研发支出LYR
    # 衍生数据表
    gr = 'gr_ttm'  # 营业收入TTM
    cogs = 'oc_ttm'  # 营业成本TTM
    da = 'da'  # 折旧和摊销 LYR
    op = 'ebit_ttm'  # EBIT
    tp = 'ebt_ttm'  # 利润总额（税前利润）
    np = 'pni_ttm'  # 归母净利润TTM
    cfo = 'cfo_ttm'  # 经营活动现金流TTM
    tcf = 'cf_ttm'  # 总现金流TTM
    capex = 'capexr'  # 资本性支出TTM
    div = 'divcashp'  # 现金分红TTM
    loan = 'debt_interest'  # 带息负债MRQ
    ic = 'total_capital'  # 全部投入资本
    na = 'tangible_asset'  # 归母有形净资产
    rg3 = 'gr_rate_3'  # 3年营业收入增长率
    # 一致预期表
    est_rev = 'est_mediansales'  # 预测营业收入中值
    est_np = 'est_mediannetprofit'  # 预测归母净利润中值
    est_cps = 'est_mediancps'  # 预测每股现金流中值
    est_dps = 'est_mediandps'  # 预测每股现金股利中值
    est_op = 'est_medianebit'  # 预测EBIT中值
    est_opda = 'est_medianebitda'  # 预测EBITDA中值
    est_bps = 'est_medianbps'  # 预测每股净资产中值
    est_tp = 'est_medianebt'  # 预测税前利润中值
    # 无风险利率
    rf = 'riskfree_rate'  # 十年国债YTM
    # 市场风险溢价
    mrp = 'risk_premium'  # 市场风险溢价
    # 最优资本结构
    dic = 'optimal_debt_to_investcapital'  # 最优D/IC
    industry = 'gics_code_third'  # 行业分类
    # 增长率
    indust = 'indus'  # 行业
    # 汇率
    fxcode = 'foreignExchange_code'  # 外汇代码
    fx = 'CLOSEW'  # 外汇收盘价
    """
    天眼查数据库
    """
    mname = 'enterprise_name'  # 公司名称
    mpic = 'actualCapital'  # 实缴资本
    mstock = 'regCapital'  # 注册资本

    """
    财报
    """
    mrev = 'e3101'  # 营业收入
    mprofit = 'e35s1'  # 净利润


    """
    保存结果
    """
    save_id = 'valuation_id'  # 估值id
    base_mv = 'syn_base_mv'  # 基准估值
    optm_mv = 'syn_optm_mv'  # 乐观估值
    pess_mv = 'syn_pess_mv'  # 悲观估值
    base_p = 'syn_basep'  # 每股基准估值
    optm_p = 'syn_optmp'  # 每股乐观估值
    pess_p = 'syn_pessp'  # 每股悲观估值
    lr_discount_p = 'syn_liqriskp'  # 流动性折价
    cp_premium_p = 'syn_controlp'  # 控制权溢价
    score = 'syn_score'  # 估值评分
    version = 'syn_version'  # 估值算法版本
    effect = 'syn_effect'  # 估值有效性

    """
    模型结果表
    """
    mbase_mv = 'model_base_mv'
    moptm_mv = 'model_optm_mv'
    mpess_mv = 'model_pess_mv'
    mliqrisk_mv = 'model_liqrisk_mv'
    mcontrol_mv = 'model_control_mv'
    mscore = 'model_score'
    mwt = 'model_wt'
    method = 'model_method_id'

    """
    结果追溯表
    """
    tb_mv = 'traceback_base_mv'
    tb_p = 'traceback_basep'
    tb_ke = 'traceback_ke'

    """
    rdt_fintech>Record
    """
    mindcode = 'inputIndustry'  # 行业代码
    mstaff = 'inputStaffNum'  # 社保人数
    mhitech = 'inputQual'  # 是否高新
    balId = 'balId'
    flowId = 'flowId'
    bmId = 'bmId'
    hyId = 'hypoId'
    mode = "inputValMode"
    market = "inputMarket"
    round = "inputRound"


class Index:
    hkd = 'HKDCNY.EX'  # 港币兑人民币
    gbp = 'GBPCNY.EX'  # 英镑兑人民币
    usd = 'USDCNY.EX'  # 美元兑人民币


class Database:
    # Lite估值记录表
    # vr_lite = dict(tb='t_valuation_record',
    #                select=[Fields.eid, Fields.uid, Fields.bdate, Fields.vdate, Fields.indcode, Fields.indpct,
    #                        Fields.peerid, Fields.fsid, Fields.bmid, Fields.hpid, Fields.mode]
    #                )
    #
    # # Mini估值记录表
    # vr_mini = dict(tb='t_valuation_record_mini',
    #                select=[Fields.mname, Fields.mindcode, Fields.mpic, Fields.mstock, Fields.mstaff, Fields.mhitech,
    #                        Fields.mrev, Fields.mprofit]
    #                )
    # 估值记录表
    vr = dict(tb='t_valuating_record',
              select=[Fields.type, Fields.eid, Fields.uid])

    # 公司行业表
    peers = dict(tb='t_company_industry_code',
                 where=Fields.gics,
                 select=Fields.code)
    # 估值输入表
    record = dict(tb='ValuatingInput',
                  select=[Fields.mindcode, Fields.mstaff, Fields.mhitech, Fields.flowId, Fields.balId, Fields.bmId,
                          Fields.hyId, Fields.mode, Fields.market, Fields.round])
    # 公司信息表
    enterprise = dict(tb='t_enterprise_info', select=[Fields.mname])

    # 用户表
    user = dict(tb='t_user_info', select=["id"])

    # 公司用户管理关系表
    enterprise_user = dict(tb='t_enterprise_manage_relation', select=[Fields.mStatus, Fields.mType])

    # tyc_data
    tyc = dict(tb='TycEnterpriseInfo', select=[Fields.mpic, Fields.mstock])

    # 假设表
    hypo = dict(tb='Hypo'
                )

    # 资产负债表
    bs = dict(tb='NewBal'
              )

    # 利润表
    ps = dict(tb='NewFlow', select=[Fields.mrev, Fields.mprofit]
              )

    # 商业模型数据表
    bm = dict(tb='NewBm'
              )

    # 市值数据表
    mv = dict(tb='mv',
              select=[Fields.code, Fields.mv]
              )
    # A股公司基本信息表
    company = dict(tb="valuation_basic_list_company_info", select=[Fields.code, Fields.name])
    # 新三板公司基本信息表
    san_company = dict(tb="valuation_basic_list_san_info", select=[Fields.code, Fields.name])
    # 香港主板公司基本信息表
    hk_company = dict(tb="valuation_basic_list_hk_info", select=[Fields.code, Fields.name])
    # 美国公司基本信息表
    america_company = dict(tb="valuation_basic_list_america_info", select=[Fields.code, Fields.name])

    # 股价数据表
    share = dict(tb='valuation_list_company_market_price',
                 select=[Fields.code, Fields.share]
                 )

    # 无杠杆beta表
    beta = dict(tb='valuation_list_company_market_beta',
                # select=None,
                select=[Fields.ub, Fields.std, Fields.code]
                )

    # 流动资产表
    ca = dict(tb='valuation_list_company_fs_currentasset',
              select=[Fields.cash, Fields.ce, Fields.ar, Fields.inv, Fields.code]
              )

    # 非流动资产表
    la = dict(tb='valuation_list_company_fs_noncurrentasset',
              select=[Fields.ip, Fields.ppe, Fields.cip, Fields.ia, Fields.dev, Fields.le, Fields.ta, Fields.code]
              )

    # 流动负债表
    cl = dict(tb='valuation_list_company_fs_currentliability',
              select=[Fields.ap, Fields.code]
              )

    # 非流动负债表
    ll = dict(tb='valuation_list_company_fs_noncurrentliability',
              select=[Fields.tl, Fields.code]
              )

    # 报表附注表
    note = dict(tb='valuation_fs_note',
                select=[Fields.rd, Fields.code]
                )

    # 衍生数据表
    der = dict(tb='valuation_fs_derivative_statements',
               select=[Fields.gr, Fields.cogs, Fields.da, Fields.op, Fields.tp, Fields.np, Fields.cfo, Fields.tcf,
                       Fields.capex, Fields.div, Fields.loan, Fields.ic, Fields.na, Fields.rg3, Fields.code]
               )

    # 一致预期表
    est = dict(tb='valuation_list_company_expection',
               select=[Fields.est_rev, Fields.est_np, Fields.est_cps, Fields.est_dps, Fields.est_op, Fields.est_opda,
                       Fields.est_bps, Fields.est_tp, Fields.code]
               )

    # 无风险利率
    rf = dict(tb='lasted_riskfree_risk',
              select=Fields.rf
              )

    # 市场风险溢价
    mrp = dict(tb='market_premium',
               select=Fields.mrp
               )

    # 最优资本结构
    dic = dict(tb='optimal_debt_to_investcapital'
               )

    # 增长率
    indrg = dict(tb='industry_growth_rate',
                 where=Fields.indust,
                 select=Fields.indust
                 )

    # 汇率
    fx = dict(tb='valuation_list_foreign_exchange',
              where=Fields.fxcode,
              select=[Fields.fxcode, Fields.fx]
              )

    # 综合结果表
    result = dict(tb='t_syn_result',
                  where='valuation_id'
                  )

    # 模型结果表
    model = dict(tb='t_model_result',
                 where='valuation_id'
                 )

    # 结果追溯表
    trace = dict(tb='t_model_result',
                 where='valuation_id')

    # 估值存档表
    doc = dict(tb='val_doc'
               )

    # Mini结果表
    result_mini = dict(tb='MiniValuationResult'
                       )

    # 估值结果表
    result_valuation = dict(tb='ValuationResult')

    # basement 营业收入
    rev = dict(tb="is_operatingrevenue_ttm",
               select=["stock_code", "is_operatingrevenue_ttm"])
    # basement
    netprofit = dict(tb="is_netprofit_ttm",
               select=["stock_code", "is_netprofit_ttm"])

    # basement 营业收入
    # register = dict(tb="is_operatingrevenue",
    #            select=["stock_code", "is_operatingrevenue"])

    price = dict(tb="w_close_price",
               select=["stock_code", "w_close_price"])
    paycapital = dict(tb="valuation_list_company_fs_equity",
                      select=["stock_code", "e_paidincapital"])
    indus = dict(tb="valuation_basic_list_company_info",
                      select=["stock_code", "gics_code_forth", "stock_name"])
