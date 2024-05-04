# -*- coding: utf-8 -*-：
# 缺乏控制权折价，输出百分比


def process_data_dloc(data):


    # 实控人持股比例
    if data['actual_controller_shareholding_percent'] <= 50:
        score = 50
    else:
        score = 60

    return score
