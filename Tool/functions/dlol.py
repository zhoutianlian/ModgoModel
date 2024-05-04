from Config.mongodb import read_mongo_limit


def func(key, value):
    try:
        demo = read_mongo_limit("AM_hypothesis", "indus_dlol", {'gics_code': int(key)}, {'_id': 0})["industry_dlol_ipo"].values[0] * value
        return demo
    except Exception as e:
        return func(key[:-2], value)


def mkt_dlol(args):
    indus_dict = args["indus_code"]
    df_ipo = 0
    for key, value in indus_dict.items():
        demo = func(key, value)
        df_ipo += demo
    capital_market = args["capital_market"]
    if capital_market not in [0, 3]:
        if capital_market == 1:
            df_ipo *= 0.9989
    else:
        df_ipo = 0

    return 1-df_ipo

