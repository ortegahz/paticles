import numpy as np
import pandas as pd


def read_all_sheets(file_path):
    xls = pd.ExcelFile(file_path)
    dataframes = {sheet_name: xls.parse(sheet_name) for sheet_name in xls.sheet_names}
    return dataframes


file_path = '/home/manu/tmp/热解例子数据采集表格1.xlsx'
data = read_all_sheets(file_path)

device_data = {}
for sheet_name, dataframe in data.items():
    if dataframe.columns.size < 1:
        continue
    print(f"\nSheet: {sheet_name}")

    ppm = dataframe.iloc[:, 8].apply(lambda x: 0 if '初始' in str(x) or pd.isna(x) else int(float(x)))
    delta_ppm = ppm.diff().fillna(0)
    print("delta_ppm:")
    print(delta_ppm)

    for device_col in range(9, 15):
        device_name = f"设备{device_col - 8}"
        adc = dataframe.iloc[:, device_col].apply(lambda x: 0 if '初始' in str(x) or pd.isna(x) else int(float(x)))
        delta_adc = adc.diff().fillna(0)

        with np.errstate(divide='ignore', invalid='ignore'):
            adc_per_ppm = np.where((delta_ppm != 0) & (delta_adc != 0),
                                   delta_adc / delta_ppm,
                                   np.nan)

        valid_values = pd.Series(adc_per_ppm).dropna()
        average_adc_ppm = valid_values.mean() if not valid_values.empty else np.nan

        device_data[device_name] = average_adc_ppm

        # print(f"\n{device_name} - delta_adc:")
        # print(delta_adc)
        # print(f"{device_name} - adc_per_ppm:")
        # print(pd.Series(adc_per_ppm))
        print(f"{device_name} - average_adc_ppm (exclude adc=0): {average_adc_ppm}")
        # break
    # break
