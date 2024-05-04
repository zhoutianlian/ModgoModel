from pandas import DataFrame as Df
from datetime import date

__all__ = ['dict_to_str', 'df_to_dict', 'date_to_ym', 'merge_dict']


def dict_to_str(my_dict: dict, link: str = '=', split: str = ', '):
    """
    用于将字典转化为字符串
    :param my_dict:
    :param link:
    :param split:
    :return:
    """
    string = ''
    for key in my_dict:
        string += f'{key}{link}{my_dict[key]}{split}'
    tail = len(split)
    return string[:-tail]


def df_to_dict(data_frame: Df, keys_col_name: str, values_col_name):
    """
    将DataFrame的两个字段转化为字典，一个作为key，一个（或一组）作为value
    :param data_frame:
    :param keys_col_name:
    :param values_col_name:
    :return:
    """
    if type(values_col_name) is str:
        return __df_to_dict_single(data_frame, keys_col_name, values_col_name)
    elif type(values_col_name) is list:
        return __df_to_dict_multiple(data_frame, keys_col_name, values_col_name)
    else:
        raise TypeError


def __df_to_dict_single(data_frame, keys_col_name, values_col_name):
    result_dict = {}
    origin_dict = data_frame.to_dict('record')
    for row in origin_dict:
        result_dict[row[keys_col_name]] = row[values_col_name]
    return result_dict


def __df_to_dict_multiple(data_frame, keys_col_name, values_col_name):
    result_dict = {}
    origin_dict = data_frame.to_dict('record')
    for row in origin_dict:
        data_dict = {}
        for value_name in values_col_name:
            data_dict[value_name] = row[value_name]
        result_dict[row[keys_col_name]] = data_dict
    return result_dict


def date_to_ym(full_date: date, split: str = '-'):
    return '%s%s%s' % (full_date.year, split, full_date.month)


def merge_dict(dict1: dict, dict2: dict, dgt: int = None):
    if dgt is None:
        def cal(val, *agrs):
            return val
    else:
        cal = round

    md = {}
    for name in dict1:
        if type(dict1[name]) is dict:
            md[name] = merge_dict(dict1[name], dict2[name])
        elif type(dict1[name]) is list:
            try:
                md_list = [cal(val1 + val2, dgt) for val1, val2 in zip(dict1[name], dict2[name])]
                md[name] = md_list
            except TypeError:
                return None
        else:
            try:
                md[name] = cal(dict1[name] + dict2[name], dgt)
            except TypeError:
                return None
    return md
