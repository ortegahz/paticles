import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm
from scipy.interpolate import griddata
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

from xlsx2dict_v1 import data_generate

# 设置字体为支持中文的字体 /usr/share/fonts/truetype/wqy/wqy-microhei.ttc
matplotlib.rcParams['font.family'] = 'AR PL UMing CN'  # 或 'Microsoft YaHei'
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 创建数据框
temperatures = [-10, 0, 20, 40, 55]
humidities = ['NA', 20, 40, 60, 80, 95]

device_data, avg_df = data_generate()

device_dfs = {k: pd.DataFrame(v, index=humidities, columns=temperatures) for k, v in device_data.items()}

# 收集训练数据
X_train = []
y_train = []

for i, h in enumerate(humidities):
    h_val = 0 if h == 'NA' else float(h)
    for j, t in enumerate(temperatures):
        if not np.isnan(avg_df.iloc[i, j]):
            X_train.append([t, h_val])
            y_train.append(avg_df.iloc[i, j])

X_train = np.array(X_train)
y_train = np.array(y_train)

# 创建多项式特征
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(X_train)

# 训练多项式回归模型
model = LinearRegression()
model.fit(X_poly, y_train)

# 从模型中获取系数
coefficients = model.coef_
intercept = model.intercept_

feature_names = poly.get_feature_names_out(['温度', '湿度'])
equation_terms = []

for i, coef in enumerate(coefficients):
    if i == 0:
        continue  # 跳过常数项
    if abs(coef) > 1e-10:  # 忽略接近于零的系数
        term = f"{coef:.6f} × {feature_names[i]}"
        equation_terms.append(term)

# 计算各设备偏移量
offset_values = {}
max_errors = {}

for name, df in device_dfs.items():
    # 计算设备相对于平均值的偏移
    diffs = []
    for i in range(len(humidities)):
        for j in range(len(temperatures)):
            if not np.isnan(df.iloc[i, j]) and not np.isnan(avg_df.iloc[i, j]):
                diffs.append(df.iloc[i, j] - avg_df.iloc[i, j])

    # 计算平均偏移量作为设备的平移量
    offset = np.mean(diffs)
    offset_values[name] = offset

    # 使用平移模型计算预测值和误差
    errors = []
    for i in range(len(humidities)):
        for j in range(len(temperatures)):
            if not np.isnan(df.iloc[i, j]) and not np.isnan(avg_df.iloc[i, j]):
                predicted = avg_df.iloc[i, j] + offset
                actual = df.iloc[i, j]
                error = abs(predicted - actual)
                errors.append(error)

    max_errors[name] = max(errors)

# 创建预测函数的输入数据格式
X = []
Y = []
Z = []

# 将平均值数据转换为坐标和值
for i, h in enumerate(humidities):
    h_val = 0 if h == 'NA' else float(h)
    for j, t in enumerate(temperatures):
        if not np.isnan(avg_df.iloc[i, j]):
            X.append(t)
            Y.append(h_val)
            Z.append(avg_df.iloc[i, j])

# 通过插值生成平滑曲面的网格点
xi = np.linspace(min(X), max(X), 100)
yi = np.linspace(min(Y), max(Y), 100)
XI, YI = np.meshgrid(xi, yi)
ZI = griddata((X, Y), Z, (XI, YI), method='cubic')

# 绘制3D曲面图
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(XI, YI, ZI, cmap=cm.viridis, alpha=0.8)
ax.scatter(X, Y, Z, c='red', marker='o')
ax.set_xlabel('温度 (°C)')
ax.set_ylabel('湿度 (%RH)')
ax.set_zlabel('ADC变化量 (每1ppm)')
ax.set_title('温湿度对ADC变化量的影响(3D曲面)')
plt.colorbar(surf, ax=ax, shrink=0.5, aspect=5)

# 绘制2D等高线图
plt.figure(figsize=(12, 8))
plt.contourf(XI, YI, ZI, 20, cmap=cm.viridis)
plt.colorbar(label='ADC变化量 (每1ppm)')
plt.scatter(X, Y, c='red', marker='o')
plt.xlabel('温度 (°C)')
plt.ylabel('湿度 (%RH)')
plt.title('温湿度对ADC变化量的影响(2D等高线)')

# 打印结果
print("===== 计算公式 =====")
equation = f"ADC变化量 = {intercept:.6f} + {' + '.join(equation_terms)} + 设备偏移量"
print(equation)
print("\n或者等价于以下简化形式：")
print(f"ADC变化量 = {intercept:.6f}", end="")
for i, coef in enumerate(coefficients):
    if i == 0:
        continue
    if abs(coef) > 1e-10:
        print(f" + {coef:.6f}×{feature_names[i]}", end="")
print(" + 设备偏移量")

print("\n===== 各设备偏移量 =====")
for device, offset in offset_values.items():
    print(f"{device}: {offset:.4f}")

print("\n===== 各设备最大误差 =====")
for device, error in max_errors.items():
    print(f"{device}: {error:.4f}")

# 验证和测试
print("\n===== 模型验证 =====")
rmse = 0
count = 0
for i, h in enumerate(humidities):
    h_val = 0 if h == 'NA' else float(h)
    for j, t in enumerate(temperatures):
        if not np.isnan(avg_df.iloc[i, j]):
            X_test = np.array([[t, h_val]])
            X_test_poly = poly.transform(X_test)
            predicted = model.predict(X_test_poly)[0]
            actual = avg_df.iloc[i, j]
            error = abs(predicted - actual)
            rmse += error ** 2
            count += 1
            print(f"温度:{t}°C, 湿度:{h}%RH - 实际值:{actual:.4f}, 预测值:{predicted:.4f}, 误差:{error:.4f}")

if count > 0:
    rmse = np.sqrt(rmse / count)
    print(f"\n均方根误差(RMSE): {rmse:.4f}")

plt.tight_layout()
plt.show()
