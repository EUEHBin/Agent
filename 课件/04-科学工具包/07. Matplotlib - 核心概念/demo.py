import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体支持（可选）

plt.rcParams.update(
    {"font.sans-serif": ["PingFang SC"], "axes.unicode_minus": False, "figure.dpi": 100}
)
# 创建图形和2x2的子图布局
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
fig.suptitle("Figure", fontsize=16, fontweight="bold")
# 1. 直线
x1 = np.linspace(0, 10, 100)
y1 = 2 * x1 + 1  # y = 2x + 1
axes[0, 0].plot(x1, y1)
axes[0, 0].set_title("Axes")

# 2. 正弦曲线
x2 = np.linspace(0, 4 * np.pi, 200)
y2 = np.sin(x2)
axes[0, 1].plot(x2, y2, color="red", linewidth=2)
axes[0, 1].set_title("Axes")

# 3. 柱状图
categories = ["A", "B", "C", "D", "E", "F", "G"]
values = np.random.randint(10, 50, size=len(categories))
bars = axes[1, 0].bar(categories, values)
axes[1, 0].set_title("Axes")
axes[1, 0].plot(x2, y2 * 10 + 20, color="black", linewidth=2)

# 4. 散点图
x4 = np.random.rand(50)
y4 = np.random.rand(50)
axes[1, 1].set_title("Axes")

scatter = axes[1, 1].scatter(x4, y4)

# 注解
axes[0, 0].annotate(
    "Artist",
    xy=(6, 13),  # 箭头指向的点
    xytext=(8, 6),  # 文字位置
    arrowprops=dict(arrowstyle="->", color="black", lw=2),
    fontsize=12,
    color="black",
    bbox=dict(boxstyle="round", facecolor="yellow", alpha=0.7),
)

axes[0, 1].annotate(
    "axis",
    xy=(0, 0.2),
    xycoords="axes fraction",
    xytext=(0.2, 0.2),
    textcoords="axes fraction",
    arrowprops=dict(arrowstyle="->", color="black", lw=2),
    ha="center",
    fontsize=12,
    bbox=dict(boxstyle="round", facecolor="yellow", alpha=0.7),
)

axes[0, 1].annotate(
    "axis",
    xy=(0.2, 0),
    xycoords="axes fraction",
    xytext=(0.2, 0.2),
    textcoords="axes fraction",
    arrowprops=dict(arrowstyle="->", color="black", lw=2),
    ha="center",
    fontsize=12,
    bbox=dict(boxstyle="round", facecolor="yellow", alpha=0.7),
)

# 显示图形
plt.show()
