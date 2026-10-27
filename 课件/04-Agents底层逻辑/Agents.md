## 沟通规范

**非常重要：当用户提问时，不能修改任何东西，不能新增任何东西，不能删除任何东西，仅回答用户问题即可**

## 课件规范

- 课件以 **Jupyter Notebook** 格式编写
- 使用 VS Code 的 Jupyter 插件运行
- Jupyter 的 Python 解释器必须使用**当前工程的虚拟环境**中的解释器，切勿使用其他环境

## Matplotlib绘图注意事项

在使用Matplotlib来进行绘图的时候，必须要考虑到中文乱码的情况，需要在绘图之前使用下列代码进行配置。

```python
# 设置中文字体支持（可选）
plt.rcParams.update({
    "font.sans-serif":["PingFang SC"],
    "axes.unicode_minus":False,
    "figure.dpi": 100
})
```

## 重要工程说明

`./HTML`

该目录下保存的是一个React工程。该工程的目的是为了阐述神经网络和Transformer架构的一些原理。这里边制作的页面都是为了阐述这些原理而存在的。

## 工程管理

- 使用 **UV** 进行工程管理
- 安装依赖时，统一使用 UV 格式：`uv add <package>`
