import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

plt.rcParams.update(
    {"font.sans-serif": ["PingFang SC"], "axes.unicode_minus": False, "figure.dpi": 100}
)

fig, ax = plt.subplots(figsize=(8, 4))
fig.subplots_adjust(bottom=0.25)

x = np.linspace(0, 10, 500)
(line,) = ax.plot(x, np.sin(x), lw=2)
ax.set_ylim(-1.5, 1.5)
ax.set_title("拖动滑块调整频率")

slider_ax = fig.add_axes((0.2, 0.1, 0.6, 0.03))
slider = Slider(
    ax=slider_ax, label="频率", valmin=0.1, valmax=5.0, valinit=1.0, valstep=0.1
)


def update(freq):
    line.set_ydata(np.sin(freq * x))
    fig.canvas.draw_idle()


slider.on_changed(update)

plt.show()
