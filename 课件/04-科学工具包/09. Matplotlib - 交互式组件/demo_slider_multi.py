import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

plt.rcParams.update(
    {"font.sans-serif": ["PingFang SC"], "axes.unicode_minus": False, "figure.dpi": 100}
)

fig, ax = plt.subplots(figsize=(8, 5))
fig.subplots_adjust(bottom=0.3)

x = np.linspace(0, 10, 500)
line, = ax.plot(x, np.sin(x), lw=2)
ax.set_ylim(-2, 2)

freq_slider_ax = fig.add_axes((0.2, 0.15, 0.6, 0.03))
freq_slider = Slider(freq_slider_ax, "频率", 0.1, 5.0, valinit=1.0)

amp_slider_ax = fig.add_axes((0.2, 0.1, 0.6, 0.03))
amp_slider = Slider(amp_slider_ax, "振幅", 0.1, 2.0, valinit=1.0)


def update(_):
    line.set_ydata(amp_slider.val * np.sin(freq_slider.val * x))
    fig.canvas.draw_idle()


freq_slider.on_changed(update)
amp_slider.on_changed(update)

plt.show()
