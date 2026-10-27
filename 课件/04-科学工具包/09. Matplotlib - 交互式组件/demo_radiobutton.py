import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons

plt.rcParams.update(
    {"font.sans-serif": ["PingFang SC"], "axes.unicode_minus": False, "figure.dpi": 100}
)

fig, ax = plt.subplots(figsize=(8, 5))
fig.subplots_adjust(left=0.3)

x = np.linspace(0, 10, 200)
(line,) = ax.plot(x, np.sin(x), lw=2, color="royalblue")
ax.set_ylim(-2, 2)
ax.set_title("单选按钮切换函数类型")

radio_ax = fig.add_axes((0.05, 0.4, 0.15, 0.2))
radio = RadioButtons(radio_ax, ("sin", "cos", "tan"))

func_map = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": lambda x: np.tan(x) * 0.5,
}


def switch(label):
    line.set_ydata(func_map[label](x))
    fig.canvas.draw_idle()


radio.on_clicked(switch)

plt.show()
