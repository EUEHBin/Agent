import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import (
    CheckButtons,
)

# 设置中文字体支持（可选）
plt.rcParams.update(
    {"font.sans-serif": ["PingFang SC"], "axes.unicode_minus": False, "figure.dpi": 100}
)

fig, ax = plt.subplots(figsize=(8, 5))
fig.subplots_adjust(left=0.3)

x = np.linspace(0, 10, 200)
lines = {}
colors = ["red", "blue", "green"]
labels = ["sin(x)", "cos(x)", "sin(x)*cos(x)"]
funcs = [np.sin, np.cos, lambda x: np.sin(x) * np.cos(x)]

for label, color, func in zip(labels, colors, funcs):
    (line,) = ax.plot(x, func(x), color=color, lw=2, label=label, visible=True)
    lines[label] = line

ax.legend(loc="upper right")
ax.set_title("复选框控制曲线显隐")

check_ax = fig.add_axes((0.05, 0.4, 0.15, 0.2))
check = CheckButtons(check_ax, labels, [True, True, True])


def toggle(label):
    line = lines[label]
    line.set_visible(not line.get_visible())
    fig.canvas.draw_idle()


check.on_clicked(toggle)

plt.show()
