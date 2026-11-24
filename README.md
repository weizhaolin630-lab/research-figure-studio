# Research Figure Studio

科研绘图 Skill：按 Nature / Science / Joule / JACS 等能源与催化顶刊的「克制、留白、高信息密度」视觉语言，从数据或文字描述生成可发表的论文配图——多面板数据图、机理/器件示意图、图形摘要，以及「示意图 + 数据」混合图。

## 能力一览

| 路径 | 输入 | 工具 | 输出 |
|---|---|---|---|
| 数据图 | CSV / JSON 数值 | `scripts/render_figure.py` | line / scatter / bar / heatmap 多面板 |
| 示意图 | 文字描述 / JSON 场景 | `scripts/render_schematic.py` | 平面矢量机理图、器件图、流程图 |
| 混合图 | 数据 + 示意图 | 两脚本组合 | 上全景示意图 + 下数据/表征网格 |

## 风格要点（提炼自 13 篇参考论文）

- **布局**：加粗小写面板字母（a、b、c…）左上角；常见结构为顶部全宽示意图 + 下方 2–4 列数据网格。
- **配色**：去饱和、色盲安全的 `energy` 色板（蓝/红/青/琥珀/紫/灰），一图 ≤ 4 主色；元素假彩约定 O=绿、Co=红、Ni=青、Cu=橙。
- **坐标轴**：仅保留左、下两条轴，刻度向外，深灰文字；单位必写、量符号斜体。
- **图例**：就地文字标注优先，不用方框图例；颜色不作唯一编码，叠加线型/标记。
- **示意**：平面矢量 + 柔和 3D 球棍/器件；流程左→右，箭头细。
- **字号层级**：面板字母 10 pt 加粗 > 轴标签 8 pt > 刻度 7 pt > 图例 6–7 pt。

## 安装

```bash
python -m pip install matplotlib numpy
```

（仅 `render_schematic.py` 需要 matplotlib；`render_figure.py` 还需要 numpy。）

## 快速开始

### 1. 数据图

写一份 JSON 规格（数值内联，或用 `data` 指向同目录 CSV）：

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

```bash
python scripts/render_figure.py figure.json output/figure --formats png,svg,pdf
```

`--strict` 会在「缺单位」「系列过多」等出版就绪告警时以非零码退出。

### 2. 示意图

```json
{
  "width_mm": 180,
  "height_mm": 100,
  "label": "a",
  "shapes": [
    {"type": "rect",  "x": 10, "y": 40, "w": 44, "h": 22, "fill": "#EEF4FB", "stroke": "#3B6FB6", "round": 4},
    {"type": "text",  "x": 32, "y": 51, "text": "Catalyst", "bold": true},
    {"type": "arrow", "x1": 56, "y1": 51, "x2": 84, "y2": 51},
    {"type": "rect",  "x": 86, "y": 40, "w": 54, "h": 22, "fill": "#FDF2F3", "stroke": "#D1495B", "round": 4},
    {"type": "text",  "x": 113, "y": 51, "text": "Product", "bold": true}
  ]
}
```

```bash
python scripts/render_schematic.py scene.json output/scene --formats png,svg,pdf
```

形状支持 `rect`（圆角）、`circle`、`polygon`、`arrow`、`text`，坐标单位 mm。

## 常用能力速查

- **双 y 轴**：序列加 `"yaxis": "right"`，面板用 `y2label` / `y2lim` / `y2scale` 配置右轴。
- **误差棒**：`yerr`（各类型）/ `xerr`（line、scatter）。
- **置信区间**：line 序列 `ylow` / `yhigh` 生成半透明填充。
- **坐标反转**：`x_invert` / `y_invert`（电化学极化曲线常用）。
- **热图标注**：`annotate_values: true` 在单元格内标数值，`value_fmt` 控格式。
- **参考线 / 标注**：`hlines`、`vlines`、`annotations`。

完整字段见 `references/spec-schema.md`。

## 目录结构

```
research-figure-studio/
├── SKILL.md                      # 技能定义与工作流
├── README.md                     # 本文件
├── scripts/
│   ├── render_figure.py          # 多面板数据图渲染器
│   └── render_schematic.py       # 声明式平面矢量示意图渲染器
├── assets/
│   └── theme.json                # 色板、字体、线宽/标记默认值
└── references/
    ├── source-library.md         # 13 篇参考论文与共性设计 DNA
    ├── style-guide.md            # 视觉规范（布局/配色/数据图/示意图/字体）
    ├── spec-schema.md            # JSON 规格与字段说明
    └── quality-checklist.md      # 交付前质量检查
```

## 参考论文（风格基准，非内容来源）

仅借鉴通用设计惯例，不复制任何图件、照片、数据或文字。全部 DOI 经 Crossref 核实有效。

| # | 论文 | 期刊/年 | DOI 链接 |
|---|---|---|---|
| 1 | Enriched asymmetric π electrons confining single-site Pt for acidic hydrogen evolution | Joule 2025 | https://doi.org/10.1016/j.joule.2025.101968 |
| 2 | Interfacial confinement enables conformal IrOx nanofilms for low-Ir-loading PEM electrolysis | JACS 2026 | https://doi.org/10.1021/jacs.6c18729 |
| 3 | Breathing mode in Nd-CoOx for active and stable PEM water electrolysis | Nat Commun 2025 | https://doi.org/10.1038/s41467-025-66408-1 |
| 4 | Water-hydroxide trapping in cobalt tungstate for PEM water electrolysis | Science 2024 | https://doi.org/10.1126/science.adk9849 |
| 5 | 10,000-h-stable intermittent alkaline seawater electrolysis | Nature 2025 | https://doi.org/10.1038/s41586-025-08610-1 |
| 6 | Highly ordered, ultra-dense intermetallic nanocrystals extend heavy-duty fuel cell life | Nat Catal 2026 | https://doi.org/10.1038/s41929-026-01607-7 |
| 7 | A precursor-valence-gating strategy for controllable synthesis of metal nanocrystals | Nat Synthesis 2026 | https://doi.org/10.1038/s44160-026-01022-7 |
| 8 | Rare-earth terbium frustrates deep reconstruction of cobalt sulfide for long-lived AEM electrolysis | Angew 2026 | https://doi.org/10.1002/anie.8233285 |
| 9 | Positively charged hollow Co nanoshells by Kirkendall effect for alkaline hydrogen evolution | Adv Mater 2024 | https://doi.org/10.1002/adma.202405386 |
| 10 | Scalable metal–organic framework-based electrodes for efficient alkaline water electrolysis | Nat Chem Eng 2025 | https://doi.org/10.1038/s44286-025-00262-2 |
| 11 | Upgrading glycerol to sorbose via a tandem photoelectrocatalysis–enzyme catalysis | Nat Sustain 2026 | https://doi.org/10.1038/s41893-026-01856-1 |
| 12 | High-entropy alloy nanowires for direct electrosynthesis of chlorine from seawater | Nat Synthesis 2026 | https://doi.org/10.1038/s44160-026-00999-5 |
| 13 | Modulating the covalency of Ru-O bonds by dynamic reconstruction for efficient acidic oxygen evolution | Nat Commun 2025 | https://doi.org/10.1038/s41467-025-58654-0 |

## 使用约定

- **只画真实数据**：不补点、删点、改误差或「美化」趋势。
- **原创表达**：不复制参考论文的具体图像、示意图、照片或文字。
- **交付物**：PNG（600 dpi）+ SVG + PDF + 生成所用的 JSON/脚本，保证可编辑、可复现。
- 交付前用 `references/quality-checklist.md` 逐项自检。
