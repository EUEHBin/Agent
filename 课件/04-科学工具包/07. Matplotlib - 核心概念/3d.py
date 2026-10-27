import numpy as np
import matplotlib.pyplot as plt

# 设置中文字体支持（可选）
plt.rcParams.update(
    {"font.sans-serif": ["PingFang SC"], "axes.unicode_minus": False, "figure.dpi": 100}
)

fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={"projection": "3d"})

# 生成螺旋线数据
t = np.linspace(0, 20, 1000)
x = np.sin(t)
y = np.cos(t)
z = t

# 绘制3D线图
ax.plot(x, y, z, linewidth=2, color="red")

ax.set_xlabel("X轴")
ax.set_ylabel("Y轴")
ax.set_zlabel("Z轴")  # type: ignore
ax.set_title("3D螺旋线示例")
plt.show()
