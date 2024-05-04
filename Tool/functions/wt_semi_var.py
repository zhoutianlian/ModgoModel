from pandas import DataFrame


def wt_semi_var(numbers: DataFrame, base: float, half: str):
    number_list = numbers.copy()
    wt = number_list.columns[0]
    num = number_list.columns[1]
    number_list = number_list[number_list[wt] > 0]  # 剔除0权重

    if half == 'up':
        number_list = number_list[number_list[num] > base]
    elif half == 'low':
        number_list = number_list[number_list[num] < base]
    else:
        print('Half should be ''up'' or ''low''')
        return None

    number_list['wt_var'] = (number_list[num] - base) ** 2 * number_list[wt]
    semi_var = sum(number_list['wt_var'])/sum(number_list[wt])
    return semi_var
