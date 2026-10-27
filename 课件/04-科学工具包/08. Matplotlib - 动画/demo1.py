import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, ArtistAnimation
from IPython.display import HTML

# 设置中文字体支持（可选）
plt.rcParams.update(
    {"font.sans-serif": ["PingFang SC"], "axes.unicode_minus": False, "figure.dpi": 100}
)

fig, ax = plt.subplots(figsize=(8, 4))

x = np.linspace(0, 2 * np.pi, 100)
(line,) = ax.plot(x, np.sin(x))

ax.set_ylim(-1.5, 1.5)
ax.set_title("正弦波动画")

frames = 100


def update(frame):
    # 最后一帧相位 = 2π，和第一帧（相位 0）在视觉上相等
    phase = 2 * np.pi * frame / frames
    line.set_ydata(np.sin(x + phase))
    return (line,)


ani = FuncAnimation(fig, update, frames=range(frames + 1), interval=16, repeat=True)

plt.show()
