# JSON 绘图规格

## 最小示例

```json
{
  "width_mm": 85,
  "height_mm": 65,
  "panels": [
    {
      "label": "a",
      "type": "line",
      "xlabel": "Time (h)",
      "ylabel": "Current density (A cm$^{-2}$)",
      "series": [
        {"label": "Catalyst A", "x": [0, 10, 20, 30], "y": [1.0, 1.2, 1.5, 1.8]},
        {"label": "Catalyst B", "x": [0, 10, 20, 30], "y": [0.8, 0.9, 1.0, 1.1]}
      ]
    }
  ]
}
```

运行：

```bash
python scripts/render_figure.py figure.json output/figure --formats png,svg,pdf
```

## 顶层字段

| 字段 | 默认值 | 说明 |
|---|---:|---|
| `width_mm` | 85 | 图宽；单栏常用 85，双栏常用 180 |
| `height_mm` | 65 | 图高，按面板信息量设置 |
| `nrows` | 1 | 面板行数 |
| `ncols` | 面板数 | 面板列数 |
| `palette` | `energy` | `energy`、`earth` 或 `mono` |
| `dpi` | 600 | 位图分辨率 |
| `panels` | 必填 | 面板数组，按行排列 |

## 面板字段

- `type`：`line`、`scatter`、`bar` 或 `heatmap`。
- `label`：面板字母，如 `a`、`b`；留空则不显示。
- `title`：短标题；优先使用面板字母和正文标题表达信息。
- `xlabel`、`ylabel`：始终包含物理量与单位。
- `xlim`、`ylim`：`[min, max]`。
- `xscale`、`yscale`：`linear`、`log`、`symlog`。
- `xticks`、`yticks`：显式刻度数组。
- `xticklabels`、`yticklabels`：刻度文字。
- `grid`：默认 `false`；仅对读数密集图开启。
- `legend`：`true`、`false` 或 Matplotlib legend 参数字典。
- `data`：CSV 路径，相对于 JSON 文件；序列中的 `x`、`y`、`yerr` 写列名。
- `annotations`：标注数组，字段为 `text`、`xy`、`xytext`，可选 `color`。
- `hlines`、`vlines`：参考线数值数组。

## 序列字段

| 字段 | 适用类型 | 说明 |
|---|---|---|
| `label` | 全部 | 图例或直接标注文字 |
| `x`、`y` | line/scatter/bar | 数值数组；使用 CSV 时为列名 |
| `yerr` | line/scatter/bar | 误差数组或 CSV 列名 |
| `color` | line/scatter/bar | 显式色值；默认取主题色 |
| `linestyle` | line | `-`、`--`、`:`、`-.` |
| `marker` | line/scatter | `o`、`s`、`^`、`D`、`v` 等 |
| `linewidth` | line | 线宽，默认来自主题 |
| `markersize` | line/scatter | 标记大小 |
| `alpha` | line/scatter/bar | 透明度，避免用透明度掩盖重叠 |
| `ylow`、`yhigh` | line | 置信区间边界，生成半透明填充 |

## 柱状图

`x` 为类别数组，`y` 为数值数组。多序列自动分组。类别较长时旋转并优先横向重排面板，不缩小到不可读。

## 热图

```json
{
  "label": "d",
  "type": "heatmap",
  "z": [[1, 2, 3], [2, 4, 6], [3, 6, 9]],
  "xlabel": "Parameter X",
  "ylabel": "Parameter Y",
  "xticklabels": ["0.1", "0.2", "0.3"],
  "yticklabels": ["1", "2", "3"],
  "cmap": "sequential",
  "colorbar": true,
  "colorbar_label": "Response (a.u.)"
}
```

设置 `center: 0` 可切换为以零为中心的发散色图。

## 科学与出版约束

- 只绘制输入数据；不得为“更平滑”“更像参考论文”而补点、删点或改误差。
- 保留异常值；需要排除时记录原因并让用户确认。
- 颜色不是唯一编码；配合线型、标记、形状或直接标签。
- 坐标标签必须含单位；无量纲量写 `a.u.` 或明确归一化方式。
- 保留 SVG/PDF 和 JSON，确保可编辑、可复现。
