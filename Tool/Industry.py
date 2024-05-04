from copy import deepcopy


__all__ = ['find_similar_industry']


def find_similar_industry(wanted_industries: list, exist_industries: list):
    """
    对行业进行上溯
    :param wanted_industries: 想要的行业代码列表
    :param exist_industries: 可取的行业代码列表
    :return: 以想要的行业代码为key，以可取的行业代码list为value的字典
    """
    exist_dict = {}
    for ind in exist_industries:
        exist_dict[ind] = ind

    result_dict = {}
    for wanted in wanted_industries:
        name = deepcopy(wanted)  # 复制完整代码备用
        result_list = []
        exists = deepcopy(exist_dict)
        length = len(wanted)
        while len(wanted) > 0:
            find = False
            for ind in exists:
                code = exists[ind]
                if len(code) > length:
                    exists[ind] = code[:length]
                    code = exists[ind]
                if wanted == code:
                    result_list.append(ind)
                    find = True
            if find:
                break
            else:
                wanted = wanted[:-1]
                length = len(wanted)

        result_dict[name] = result_list
    return result_dict
