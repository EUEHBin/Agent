import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, ArtistAnimation
from collections import deque

# 设置中文字体支持（可选）
plt.rcParams.update(
    {"font.sans-serif": ["PingFang SC"], "axes.unicode_minus": False, "figure.dpi": 100}
)
# 使用可迭代对象作为 frames


fig, ax = plt.subplots(figsize=(8, 4))

# 保存最近100个数据点
x_data = deque(maxlen=100)
y_data = deque(maxlen=100)

(line,) = ax.plot([], [], lw=2)

ax.set_xlim(0, 100)
ax.set_ylim(-1.5, 1.5)


# -----------------------------
# 无限生成器（模拟实时数据流）
# -----------------------------
def data_stream():
    t = 0
    while True:
        yield t, np.sin(t * 0.1)
        t += 1


# -----------------------------
# 每收到一条数据就更新一次图像
# -----------------------------
def update(frame):
    x, y = frame

    x_data.append(x)
    y_data.append(y)

    line.set_data(x_data, y_data)

    # x轴跟着移动，形成滚动窗口
    if x >= 100:
        ax.set_xlim(x - 100, x)


ani = FuncAnimation(
    fig,
    update,
    frames=data_stream(),
    interval=30,
    cache_frame_data=False,
)  # 无限生成器


plt.show()
