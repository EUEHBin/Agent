import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, ArtistAnimation
from collections import deque

# 设置中文字体支持（可选）
plt.rcParams.update(
    {"font.sans-serif": ["PingFang SC"], "axes.unicode_minus": False, "figure.dpi": 100}
)

fig, ax = plt.subplots(figsize=(8, 4))

x = np.linspace(0, 2 * np.pi, 100)
(line,) = ax.plot([], [], lw=2)
(point,) = ax.plot([], [], "ro", ms=8)


def init():
    ax.set_xlim(0, 2 * np.pi + 5)
    ax.set_ylim(-1.5, 1.5)
    return line, point


def update(frame):
    y = np.sin(x + frame * 0.1)
    line.set_data(x, y)
    point.set_data([x[-1]], [y[-1]])
    return line, point


ani = FuncAnimation(fig, update, frames=100, init_func=init, blit=True, interval=50)

plt.show()
