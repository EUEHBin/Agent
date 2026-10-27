import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox

plt.rcParams.update(
    {"font.sans-serif": ["PingFang SC"], "axes.unicode_minus": False, "figure.dpi": 100}
)

fig, ax = plt.subplots(figsize=(8, 4))
fig.subplots_adjust(bottom=0.2)

x = np.linspace(0, 10, 500)
line, = ax.plot(x, np.sin(x), lw=2)
ax.set_ylim(-1.5, 1.5)
ax.set_title("输入频率值后按回车")

text_ax = fig.add_axes((0.2, 0.05, 0.6, 0.06))
text_box = TextBox(text_ax, "频率", initial="1.0")


def submit(text):
    try:
        freq = float(text)
        line.set_ydata(np.sin(freq * x))
        fig.canvas.draw_idle()
    except ValueError:
        pass


text_box.on_submit(submit)

plt.show()
