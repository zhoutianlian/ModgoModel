import pickle
import os


def liner_mv(company_data, company_data_x):
    current_path = os.path.dirname(__file__)
    lm = current_path + "/liner_model/all_positive.linear"
    loaded_model = pickle.load(open(lm, 'rb'))
    company_data['liner_mv'] = loaded_model.predict(company_data_x)
    return company_data


def adjust_liner_mv(regCapital, jilin_mv_adjust):
    if regCapital >= 100000000:
        a = jilin_mv_adjust * 0.7
    elif 10000000 <= regCapital < 100000000:
        a = jilin_mv_adjust * 0.65
    elif 1000000 <= regCapital < 10000000:
        a = jilin_mv_adjust * 0.6
    else:
        a = jilin_mv_adjust * 0.55

    if a < regCapital:
        b = regCapital * np.random.randint(10001, 12000) / 10000
    else:
        b = a
    return b