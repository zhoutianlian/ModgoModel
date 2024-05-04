
import pandas as pd


def read_for_share_value_case():
    path = r'C:\Users\Administrator\Desktop\to_distribute.xlsx'
    vc_table = pd.read_excel(io=path, sheet_name="Sheet1")
    exit_value = 50000
    vc_series = 6
    years_to_exit = 1
    indus_code = {"203020": 0.8, "352020": 0.2}

    return exit_value, vc_series, vc_table, years_to_exit, indus_code


