# 问题为T 湿度为RH·实现以下公式
# ADC = 2.062464 + 0.016144*温度 + 0.005293*湿度 -0.000020*温度*湿度 -0.000052*温度^2 -0.000052*湿度^2 + 设备偏移量
def calculate_adc(T, RH, delta_adc):
    """
    根据给定的温度和湿度，计算ADC的值。

    参数：
    T (float): 温度，单位为摄氏度。
    RH (float): 湿度，单位为百分比。

    返回值：
    float: 计算得到的ADC值。
    """
    # ADC = 2.406789 + 0.010252 * T +  0.000233 * RH - 0.000018 * T * RH - 0.000061 * T**2 - 0.000008 * RH**2 + delta_adc
    ADC = 2.132185 + 0.014156 * T + 0.004144 * RH - 0.000033 * T ** 2 + -0.000013 * T * RH - 0.000046 * RH ** 2 + delta_adc
    # ADC = 2.647529 + (0.203993 * T) + (-0.026132 * RH) + (-0.021902 * T ** 2) + (-0.019353 * T* RH) + (-0.046510 * RH ** 2)
    return ADC


def calculate_delt_adc(T, RH):
    """
    根据给定的温度和湿度，计算delta_adc的值。

    参数：
    T (float): 温度，单位为摄氏度。
    RH (float): 湿度，单位为百分比。
    CO_ppm (float): CO浓度，单位为ppm。

    返回值：
    float: 计算得到的delta_adc值。
    """
    ADC = 2.132185 + 0.014156 * T + 0.004144 * RH - 0.000033 * T ** 2 + -0.000013 * T * RH - 0.000046 * RH ** 2
    # ADC = 2.406789 + 0.010252 * T +  0.000233 * RH - 0.000018 * T * RH - 0.000061 * T**2 - 0.000008 * RH**2
    return ADC


if __name__ == "__main__":
    # 示例用法
    T = 55  # 温度，单位为摄氏度
    RH = 20  # 湿度，单位为百分比
    init_adc = 2599
    CO_ppm = 190
    real_value = 2072

    calc_delta_adc = (init_adc - real_value) / CO_ppm - calculate_delt_adc(T, RH)
    delta_adc = -0.08743578947368436

    ADC_pre_ppm = calculate_adc(T, RH, delta_adc)
    print(f"calc_delta_adc = {calc_delta_adc} delta_adc = {delta_adc} ADC_pre_ppm = {ADC_pre_ppm}")
    calc_ppm = (init_adc - real_value) / ADC_pre_ppm

    print(f"Calc PPM：{calc_ppm} real PPM: {CO_ppm} delta PPM : {calc_ppm - CO_ppm}")
