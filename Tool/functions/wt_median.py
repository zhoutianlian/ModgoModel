from pandas import DataFrame
import numpy as np

def wt_median(numbers: DataFrame):
    wt = numbers.columns[0]
    median_wt = sum(numbers[wt])/2

    num = numbers.columns[1]
    numbers = numbers[numbers[wt] > 0]  # 剔除0权重

    if len(numbers) < 2:
        print('Length too short!')
        return None
    else:
        numbers = numbers.sort_values(by=num, ascending=True)
        count0 = 0.0
        count1 = numbers[wt][0]
        if count1 > median_wt:
            return numbers[num][0]
        else:
            for e in range(len(numbers) - 1):
                count0 += numbers[wt][e]
                count1 += numbers[wt][e + 1]
                if (count0 < median_wt) and (count1 > median_wt):
                    wt_mid = numbers[num][e + 1]
                    return wt_mid
                elif count0 == median_wt:
                    wt_mid = np.average(numbers[num][e], numbers[num][e + 1])
                    return wt_mid
    print('Failed!')
    return None
