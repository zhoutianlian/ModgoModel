import xlrd
from pandas import Timestamp


def cell_list(cell_value: str):
    cell_value = str(cell_value)
    if cell_value == '':
        return list()
    string = cell_value.replace(' ', '')
    string = string.replace(',', '","')
    return eval('["%s"]' % string)


def readxl(file_path):
    # 读取录入表格
    excel = xlrd.open_workbook(file_path)
    data = dict()

    # 读取基本信息
    basic = excel.sheet_by_name('基本信息')
    data['enterprise_name'] = basic.cell_value(2, 3)
    data['mode'] = int(basic.cell_value(4, 3))
    data['type'] = int(basic.cell_value(5, 3))

    data['industry'], data['peer'] = dict(), dict()
    for row in [11, 17, 23, 29]:
        industry = int(basic.cell_value(row, 6))
        if industry >= 10000000:
            data['industry'][industry] = basic.cell_value(row - 2, 8)
            data['peer'][industry] = cell_list(basic.cell_value(row - 2, 10))

    data['basic'] = dict()
    data['basic']['round'] = int(basic.cell_value(33, 3))
    data['basic']['market'] = int(basic.cell_value(34, 3))
    data['basic']['staff'] = int(basic.cell_value(36, 3))
    data['basic']['qualify'] = cell_list(basic.cell_value(38, 3))

    # 读取财务数据
    fs = excel.sheet_by_name('财务数据')
    bal = list()
    flow = list()
    names = fs.col_values(1)
    bal_acc, flow_acc = names[2:15], names[17:29]

    for col in range(2, 7):
        values = fs.col_values(col)
        if values[15]:
            bal_data = values[2:15]
            bal.append(dict(zip(bal_acc, bal_data)))
            d = Timestamp(*xlrd.xldate_as_tuple(bal[-1]['date'], 0))
            bal[-1]['date'] = int(str(d.year)+str(d.month))
        if values[29]:
            flow_data = values[17:29]
            flow.append(dict(zip(flow_acc, flow_data)))
            d = Timestamp(*xlrd.xldate_as_tuple(flow[-1]['date'], 0))
            flow[-1]['date'] = int(str(d.year) + str(d.month))
            # flow[-1]['date'] = Timestamp(*xlrd.xldate_as_tuple(flow[-1]['date'], 0))
            d = Timestamp(*xlrd.xldate_as_tuple(flow[-1]['start'], 0))
            flow[-1]['start'] = int(str(d.year) + str(d.month))
            # flow[-1]['start'] = Timestamp(*xlrd.xldate_as_tuple(flow[-1]['start'], 0))

    data['bal'] = bal
    data['flow'] = flow

    # 读取商业模型
    data['bm'] = dict()
    # 读取分析师假设
    hypo = excel.sheet_by_name('分析师假设')
    data['hypo'] = dict()
    for acc, value in zip(hypo.col_values(1)[2:71], hypo.col_values(3)[2:71]):
        if value != '':
            data['hypo'][acc] = value
    # 列表式
    for row in [32, 41, 43, 45, 70]:
        data_list = list()
        for col in range(3, 10):
            data_list.append(hypo.cell_value(row, col))
        while len(data_list):
            if data_list[-1] == '':
                data_list.pop()
            else:
                break
        l = len(data_list)
        if l:
            for i in range(l):
                data_list[i] = 0 if data_list[i] == '' else data_list[i]
            data['hypo'][hypo.cell_value(row, 1)] = data_list

    def get_sub(title, from_row, till_row):
        t = dict()
        for a, v in zip(hypo.col_values(1)[from_row:till_row],
                        hypo.col_values(3)[from_row:till_row]):
            if v != '':
                t[acc] = v
        if len(t):
            data['hypo'][title] = t

    get_sub('optm', 74, 95)  # 乐观
    get_sub('pess', 95, 116)  # 悲观
    get_sub('sens', 118, 137)  # 敏感性
    get_sub('mont', 139, 157)  # 蒙特卡罗
    get_sub('judg', 159, 167)  # 评价
    get_sub('mark', 169, 171)  # 市场法
    get_sub('optn', 173, 176)  # 期权法
    get_sub('astb', 178, 181)  # 资产基础法

    return data


if __name__ == '__main__':
    FilePath = r'G:\工作\本地化工程\Modgo新模型录入表.xlsx'
    readxl(FilePath)
