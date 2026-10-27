import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

plt.rcParams.update(
    {"font.sans-serif": ["PingFang SC"], "axes.unicode_minus": False, "figure.dpi": 100}
)

fig, ax = plt.subplots(figsize=(8, 4))
fig.subplots_adjust(bottom=0.2)

x = np.linspace(0, 10, 100)
(line,) = ax.plot(x, np.random.randn(100).cumsum(), lw=2)
ax.set_title("点击按钮重新生成数据")

button_ax = fig.add_axes((0.4, 0.05, 0.2, 0.075))
button = Button(button_ax, "重新生成", color="lightblue", hovercolor="skyblue")


def regenerate(event):
    line.set_ydata(np.random.randn(100).cumsum())
    ax.relim()
    ax.autoscale_view()
    fig.canvas.draw_idle()


button.on_clicked(regenerate)

plt.show()
