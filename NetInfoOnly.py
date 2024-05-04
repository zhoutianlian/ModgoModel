from keras import backend
from Algorithm.GuessFS import *


def net_info_only_evaluation(company_name):


    backend.clear_session()
    gics1: int
    staff: int

    share: int = 0
    pic: int = 0
    na = guess_na(pic=pic, share=share)
    guess_rev(na=na)


    unvalid_pat: int

    x_operation = [gics1, staff, na, 0, unvalid_pat]
    x_all = [gics1, staff, na, 0, unvalid_pat]

    x_list = [x_all, x_industry, x_size, x_operation]
    for i in range(5):
        try:
            model = pk.load(open(self.modpath % 'pb', 'rb'))
            pb_list = model.predict(x_list)
            self.detail['pb'] = pb_list[-1]
            adj_pb_list = [pb * self.mult_adj * self.sprm for pb in pb_list]
            pb_val_list = [pb * self.na for pb in adj_pb_list]
            break
        except Exception as err:
            print(err)
            time.sleep(5)
    else:
        raise TimeoutError
    return tuple(pb_val_list)