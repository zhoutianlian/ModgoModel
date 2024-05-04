import pickle
import os
import math

from config.database import connect_to_test


def read_data(pid):
    db = connect_to_test()
    cursor = db.cursor()
    read_sql = "select l_shorttermborrowings, l_shorttermdebenturespayable," \
               " l_currentportionofnoncurrentliabilitiy, l_longtermborrowings, " \
               "l_debenturespayable, l_longtermpayable, l_totalliabilities from valuation_realestate_input_liability where pid = %s;"
    try:
        cursor.execute(read_sql, [pid])
    except Exception as e:
        print(e)
        cursor.close()
        db.close()
    tuple_demo_1 = cursor.fetchall()[0]

    read_sql = "select is_netprofit, is_totaloperatingrevenue from valuation_realestate_input_income where pid = %s;"
    try:
        cursor.execute(read_sql, [pid])
    except Exception as e:
        print(e)
        cursor.close()
        db.close()
    tuple_demo_2 = cursor.fetchall()[0]

    read_sql = "select note_average_tax_rate from valuation_realestate_input_note where pid = %s;"
    try:
        cursor.execute(read_sql, [pid])
    except Exception as e:
        print(e)
        cursor.close()
        db.close()
    tuple_demo_3 = cursor.fetchall()[0]

    read_sql = "select e_totalequityattributabletoshareholdersoftheparent from valuation_realestate_input_equity where pid = %s;"
    try:
        cursor.execute(read_sql, [pid])
    except Exception as e:
        print(e)
        cursor.close()
        db.close()
    tuple_demo_4 = cursor.fetchall()[0]

    read_sql = "select a_totalasset, a_constructioninprogress from valuation_realestate_input_asset where pid = %s;"
    try:
        cursor.execute(read_sql, [pid])
    except Exception as e:
        print(e)
        cursor.close()
        db.close()
    tuple_demo_5 = cursor.fetchall()[0]

    read_sql = "select building_construction_area, cpi_reside_rent_y from valuation_china_realestate_year where pid = %s;"
    try:
        cursor.execute(read_sql, [pid])
    except Exception as e:
        print(e)
        cursor.close()
        db.close()
    tuple_demo_6 = cursor.fetchall()[0]

    read_sql = "select land_transaction_price_m, land_acquisition_area_m, real_estate_development_enterprises_funds_m from valuation_china_realestate_month where pid = %s;"
    try:
        cursor.execute(read_sql, [pid])
    except Exception as e:
        print(e)
        cursor.close()
        db.close()
    tuple_demo_7 = cursor.fetchall()[0]

    read_sql = "select per_consumption_expenditure_reside, per_capita_disposable_income_reside from valuation_china_citizen_expense_season where pid = %s"
    try:
        cursor.execute(read_sql, [pid])
    except Exception as e:
        print(e)
        cursor.close()
        db.close()
    tuple_demo_8 = cursor.fetchall()[0]
    cursor.close()
    db.close()

    lsb = tuple_demo_1[0]
    lsd = tuple_demo_1[1]
    lc = tuple_demo_1[2]
    llb = tuple_demo_1[3]
    ld = tuple_demo_1[4]
    llt = tuple_demo_1[5]
    ltl = tuple_demo_1[6]
    inp = tuple_demo_2[0]
    ito = tuple_demo_2[1]
    natr = tuple_demo_3[0]
    et = tuple_demo_4[0]
    at = tuple_demo_5[0]
    ac = tuple_demo_5[1]
    bca = tuple_demo_6[0]
    crr = tuple_demo_6[1]
    ltp = tuple_demo_7[0]
    laa = tuple_demo_7[1]
    red = tuple_demo_7[2]
    pce = tuple_demo_8[0]
    pcd = tuple_demo_8[1]

    a = lsb + lsd + lc + llb + ld + llt
    b = inp * natr
    c = et
    d = ltl / at
    e = bca
    f = ltp / laa
    g = red
    h = crr
    i = pce
    j = pcd
    k = ito / ac

    list_demo = [a, b, c, d, e, f, g, h, i, j, k]
    return list_demo


def func(pid):
    dict_demo = {}
    path = os.path.join(os.getcwd(), "optimal_real_estate.model")
    print(path)
    file_read = open(path, 'rb')
    model = pickle.load(file_read)
    list_demo = read_data(pid)
    result = model.predict(list_demo)
    dict_demo["result"] = result / (1 + 0.15132256) / 1.2
    dict_demo["result_avg"] = dict_demo["result"]
    dict_demo["result_max"] = dict_demo["result"] * (1 + 0.13)
    dict_demo["result_min"] = dict_demo["result"] * (1 - 0.08)

func(32)