import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import max_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

# 设置字体为支持中文的字体 /usr/share/fonts/truetype/wqy/wqy-microhei.ttc
matplotlib.rcParams['font.family'] = 'AR PL UMing CN'  # 或 'Microsoft YaHei'
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
# 原始数据
data = {
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

# 转换为DataFrame
df = pd.DataFrame(data)


# 解析温度和湿度
def parse_condition(cond):
    t_part, h_part = cond.split('|')
    t = float(t_part.replace('℃', ''))
    h = float(h_part.replace('％湿度', '').replace('-', '0'))
    return t, h


# 解析所有条件
conditions = df['condition'].apply(parse_condition)
df['temperature'] = [c[0] for c in conditions]
df['humidity'] = [c[1] for c in conditions]

# 长格式转换
devices = ['设备1', '设备2', '设备3', '设备4', '设备5', '设备6']
long_data = []
for device in devices:
    temp_df = df[['temperature', 'humidity', device]].copy()
    temp_df = temp_df.rename(columns={device: 'value'})
    temp_df['device'] = device
    long_data.append(temp_df)
long_df = pd.concat(long_data)

# 准备建模数据
X = long_df[['temperature', 'humidity']].values
y = long_df['value'].values

# 多项式回归模型
degree = 2
poly_model = Pipeline([
    ('poly', PolynomialFeatures(degree=degree)),
    ('linear', LinearRegression())
])
poly_model.fit(X, y)

# 预测和评估
y_pred = poly_model.predict(X)
max_err = max_error(y, y_pred)
r2 = r2_score(y, y_pred)

print(f"拟合公式：V = f(T, H) 的 {degree} 次多项式")
print(f"最大误差：{max_err:.2f}")
print(f"R² 分数：{r2:.4f}")

# 提取模型系数
coef = poly_model.named_steps['linear'].coef_
intercept = poly_model.named_steps['linear'].intercept_
poly_features = poly_model.named_steps['poly'].get_feature_names_out(['T', 'H'])

# 打印公式
formula = f"V = {intercept:.2f}"
for feature, c in zip(poly_features, coef):
    if c != 0:
        formula += f" + {c:.2f}*{feature}"
print("\n拟合公式：")
print(formula)

# 计算设备平移量
device_offsets = {}
for device in devices:
    device_data = long_df[long_df['device'] == device]
    y_device = device_data['value'].values
    X_device = device_data[['temperature', 'humidity']].values
    y_pred_device = poly_model.predict(X_device)
    offset = np.mean(y_device - y_pred_device)
    device_offsets[device] = offset
    print(f"{device} 的平均平移量：{offset:.2f}")

# 可视化
# 3D图
fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(121, projection='3d')
ax.scatter(X[:, 0], X[:, 1], y, c='r', marker='o', label='实际值')
ax.scatter(X[:, 0], X[:, 1], y_pred, c='b', marker='^', label='预测值')
ax.set_xlabel('温度 (℃)')
ax.set_ylabel('湿度 (%)')
ax.set_zlabel('读数')
ax.set_title('3D 实际 vs 预测')
ax.legend()

# 2D图（温度固定，湿度变化）
ax2 = fig.add_subplot(122)
sample_temps = [20, 40, 55]
colors = ['r', 'g', 'b']
for temp, color in zip(sample_temps, colors):
    mask = (long_df['temperature'] == temp) & (long_df['device'] == '设备1')
    subset = long_df[mask]
    ax2.plot(subset['humidity'], subset['value'], 'o-', color=color, label=f'{temp}℃ 实际')
    pred_subset = poly_model.predict(subset[['temperature', 'humidity']])
    ax2.plot(subset['humidity'], pred_subset, '^--', color=color, label=f'{temp}℃ 预测')
ax2.set_xlabel('湿度 (%)')
ax2.set_ylabel('读数')
ax2.set_title('2D 湿度 vs 读数（不同温度）')
ax2.legend()

plt.tight_layout()
plt.show()
