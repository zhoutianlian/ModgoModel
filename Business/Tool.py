def tag(target, x, y):
    lower, higher = None, None
    for x_value, y_value in zip(x, y):
        if x_value < target:
            if lower is None:
                lower = (x_value, y_value)  # 不存在lower时添加lower
            elif lower[0] < x_value:
                lower = (x_value, y_value)  # x_value比lower原值更大时替换lower
        else:
            if higher is None:
                higher = (x_value, y_value)  # 不存在higher时添加higher
            elif higher[0] > x_value:
                higher = (x_value, y_value)  # x_value比higher更小时替换higher
    sum_wt = higher[0] - lower[0]
    lower_wt = (higher[0] - target) / sum_wt
    higher_wt = (target - lower[0]) / sum_wt
    return lower_wt * lower[1] + higher_wt * higher[1]
