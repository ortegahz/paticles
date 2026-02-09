import re
from pprint import pprint

import numpy as np
import pandas as pd

COL_TEMPS = ['-10', '0', '20', '40', '55']
ROW_HUMIDS = ['NA', '20', '40', '60', '80', '95']

START_IDX = 1
# START_IDX = 9


def calculate_averages(device_template):
    average_data = []
    for row_idx in range(len(ROW_HUMIDS)):
        row = []
        for col_idx in range(len(COL_TEMPS)):
            cell_values = [
                device_template[f"设备{i + 1}"][row_idx][col_idx]
                for i in range(6)
            ]
            valid_values = [v for v in cell_values if not np.isnan(v)]
            row.append(np.mean(valid_values) if valid_values else np.nan)
        average_data.append(row)
    return average_data


def read_all_sheets(file_path):
    xls = pd.ExcelFile(file_path)
    return {sheet: xls.parse(sheet) for sheet in xls.sheet_names}


def parse_sheet_name(name):
    """ 增强型名称解析 """
    # 标准化输入格式
    clean_name = name.replace('｜', '|').replace('％', '%').replace(' ', '')

    # 温度解析（支持负值和小数）
    temp_match = re.search(r'(-?\d+\.?\d*)℃', clean_name)
    if not temp_match:
        return None, None
    temp = temp_match.group(1)

    # 湿度解析（增强模式匹配）
    humid_pattern = r'(?:湿度|h|H)?(\d+%|NA)(?![^℃]*℃)'  # 排除温度后的百分号
    humid_match = re.search(humid_pattern, clean_name)

    if humid_match:
        humid = humid_match.group(1).replace('%', '')
        # 处理特殊符号兼容
        if humid not in ROW_HUMIDS and humid != 'NA':
            humid = str(int(float(humid)))  # 处理小数湿度
    else:
        # 最后尝试匹配纯数字
        last_num_match = re.search(r'(\d+)(?!.*℃)(?!.*\d)', clean_name)
        humid = last_num_match.group(1) if last_num_match else 'NA'

    return temp, humid


def data_generate(file_path='/home/manu/tmp/热解例子数据采集表格1.xlsx', flip=True):
    device_template = {
        f"设备{i + 1}": [
            [np.nan] * len(COL_TEMPS) for _ in ROW_HUMIDS
        ] for i in range(6)
    }

    all_data = read_all_sheets(file_path)

    for sheet_name, df in all_data.items():
        if df.columns.size < 1:
            continue

        temp, humid = parse_sheet_name(sheet_name)
        if None in [temp, humid]:
            print(f"跳过无法解析的工作表: {sheet_name}")
            continue

        col_idx = COL_TEMPS.index(temp) if temp in COL_TEMPS else -1
        row_idx = ROW_HUMIDS.index(humid) if humid in ROW_HUMIDS else -1

        if -1 in [col_idx, row_idx]:
            print(f"坐标越界: {sheet_name} (T:{temp}/H:{humid})")
            continue

        print(f"解析成功: {sheet_name} -> 温度{temp}℃ 湿度{humid}%")

        ppm = df.iloc[:, 8].apply(lambda x: 0 if '初始' in str(x) or pd.isna(x) else int(float(x)))
        delta_ppm = ppm.diff().fillna(0)

        for dev_idx in range(6):
            adc = df.iloc[:, START_IDX + dev_idx].apply(
                lambda x: 0 if '初始' in str(x) or pd.isna(x) else int(float(x)))
            delta_adc = adc.diff().fillna(0)

            with np.errstate(divide='ignore', invalid='ignore'):
                ratios = np.where((delta_ppm != 0) & (delta_adc != 0),
                                  delta_adc / delta_ppm,
                                  np.nan)

            avg_ratio = np.nanmean(ratios)
            avg_ratio = avg_ratio * -1 if flip else avg_ratio
            device_template[f"设备{dev_idx + 1}"][row_idx][col_idx] = avg_ratio

    print("\n最终数据结构:")
    for device, data in device_template.items():
        df = pd.DataFrame(data, index=ROW_HUMIDS, columns=COL_TEMPS)
        print(f"\n{device} 数据矩阵:")
        print(df)

    print("\navg_matrix:")
    avg_matrix = calculate_averages(device_template)
    avg_df = pd.DataFrame(avg_matrix, index=ROW_HUMIDS, columns=COL_TEMPS)
    print(avg_df)

    return device_template, avg_df


def data_generate_zero(file_path='/home/manu/tmp/热解例子数据采集表格1.xlsx'):
    device_template = {
        "condition": [
            "-10℃|-％湿度", "0℃|-％湿度", "20℃|20％湿度", "20℃|40％湿度",
            "20℃|60％湿度", "20℃|80％湿度", "20℃|95％湿度", "40℃|20％湿度",
            "40℃|40％湿度", "40℃|60％湿度", "40℃|80％湿度", "40℃|95％湿度",
            "55℃|20％湿度", "55℃|40％湿度", "55℃|60％湿度", "55℃|80％湿度",
            "55℃|95％湿度"
        ],
        "设备1": [2613, 2618, 2617, 2613, 2605, 2617, 2594, 2605, 2604, 2599, 2580, 2595, 2599, 2578, 2596, 2582, 2564],
        "设备2": [2612, 2615, 2619, 2617, 2611, 2618, 2604, 2612, 2612, 2606, 2591, 2595, 2595, 2591, 2597, 2581, 2569],
        "设备3": [2606, 2611, 2615, 2614, 2611, 2615, 2604, 2608, 2609, 2605, 2592, 2597, 2593, 2592, 2590, 2577, 2569],
        "设备4": [2605, 2609, 2615, 2615, 2605, 2615, 2599, 2609, 2609, 2602, 2588, 2591, 2593, 2591, 2599, 2581, 2565],
        "设备5": [2608, 2612, 2615, 2611, 2601, 2615, 2595, 2605, 2601, 2599, 2581, 2585, 2591, 2581, 2591, 2573, 2561],
        "设备6": [2609, 2611, 2617, 2610, 2599, 2614, 2590, 2599, 2599, 2596, 2572, 2581, 2591, 2574, 2581, 2573, 2556]
    }

    all_data = read_all_sheets(file_path)

    for i, (sheet_name, df) in enumerate(all_data.items()):
        if df.columns.size < 1:
            continue

        temp, humid = parse_sheet_name(sheet_name)
        if None in [temp, humid]:
            print(f"跳过无法解析的工作表: {sheet_name}")
            continue

        col_idx = COL_TEMPS.index(temp) if temp in COL_TEMPS else -1
        row_idx = ROW_HUMIDS.index(humid) if humid in ROW_HUMIDS else -1

        if -1 in [col_idx, row_idx]:
            print(f"坐标越界: {sheet_name} (T:{temp}/H:{humid})")
            continue

        print(f"解析成功: {sheet_name} -> 温度{temp}℃ 湿度{humid}%")

        # ppm = df.iloc[:, 8].apply(lambda x: 0 if '初始' in str(x) or pd.isna(x) else int(float(x)))
        # delta_ppm = ppm.diff().fillna(0)

        for dev_idx in range(6):
            adc = df.iloc[:, START_IDX + dev_idx].apply(
                lambda x: 0 if '初始' in str(x) or pd.isna(x) else int(float(x)))
            adc_zero = adc[0]
            _key = f"设备{dev_idx + 1}"
            device_template[_key][i] = adc_zero

    print("\nzero dict:")
    pprint(device_template, width=120, indent=4, sort_dicts=False)

    return device_template


if __name__ == '__main__':
    device_template, avg_df = data_generate()
    device_template_zero = data_generate_zero()
