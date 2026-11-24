---
name: research-figure-studio
description: Creates publication-ready scientific figures in the restrained, high-impact style of Nature/Science/Joule/JACS energy and catalysis papers, including multi-panel data charts, mechanism/device schematics, graphical abstracts, and characterizations (microscopy/spectroscopy) that mix schematics with data plots. This skill should be used when a user requests 科研绘图、论文插图、数据图、机理图、器件图、示意图、图形摘要、Nature 风格、Science 风格、期刊配图, or asks to draw a figure from CSV/XLSX/JSON data.
agent_created: true
---

# Research Figure Studio

## Overview

Generate publication-ready scientific figures from data and textual descriptions. The style is grounded in 13 high-impact energy/catalysis papers (see `references/source-library.md`): desaturated colorblind-safe palettes, bold lowercase panel letters, an upper overview schematic over a data/characterization grid, only left/bottom axes with outward ticks, direct in-plot labels instead of boxed legends, and flat-vector-plus-soft-3D illustrations.

## Workflow decision tree

1. Classify the request into one of three paths:
   - **Data chart** (line/scatter/bar/heatmap from numbers) → `scripts/render_figure.py`.
   - **Schematic / device / mechanism / graphical abstract** (concepts, structures, flows) → `scripts/render_schematic.py`.
   - **Hybrid** (overview schematic + data panels) → compose both, combine into one figure via one script or assemble panels.
2. Identify the input data source. If the user attaches a spreadsheet, load the `workbuddy-sheetagent` skill and extract the values into a clean table or CSV before plotting; never plot from a screenshot of numbers.
3. Confirm the figure brief before heavy work when the request is ambiguous: message/story, panel sequence, target journal/column width (single 85 mm / double 180 mm), language (en/zh), and output formats. Do not over-ask when the intent is clear.

## Rules that always apply

- Plot only real, user-provided data. Never invent, smooth, drop points, or alter error bars to look "cleaner" or "more like a reference paper."
- Imitate general design conventions, never reproduce specific figures, photographs, or text from the reference papers.
- Color is never the sole encoding; add linestyle, marker, or direct labels.
- Always include units in axis labels; write quantity symbols in italics, units in roman.
- Deliver editable sources: PNG (600 dpi) + SVG + PDF + the JSON/script used to generate it.

## Data charts

1. Read `references/spec-schema.md` for the JSON schema.
2. Write a spec JSON (inline arrays, or `data` pointing to a CSV beside the spec). Pick palette from `assets/theme.json` (`energy` default).
3. Render:
   ```bash
   python scripts/render_figure.py figure.json output/figure --formats png,svg,pdf
   ```
   Use `--strict` to fail on publication-readiness warnings.
4. Inspect the PNG at final print size (view it, check label clipping and overlaps), then iterate on `xlim/ylim/xticks/legend` or panel arrangement.

Both renderers require matplotlib (and numpy for data charts). If import fails, install with `python -m pip install matplotlib numpy`.

## Schematics and graphical abstracts

1. Load `references/style-guide.md` sections 4–5 for illustration conventions.
2. For precise, editable text/geometry, use `scripts/render_schematic.py` with a JSON scene of shapes (rounded cards, rectangles, circles, polygons, arrows, text). See the script docstring for shape fields.
3. For photographic or complex soft-3D material textures, optionally generate a texture-only background with the image-generation tool, then composite vector text, arrows, and labels over it. Never let an image model draw axis numbers, chemical formulas, or data — those must be vector and exact.

## Final quality gate

Apply `references/quality-checklist.md` before delivering. If any item fails, fix and re-render. Present the PNG preview and provide the SVG/PDF/source together.

## Resources

- `references/spec-schema.md` — JSON schema and examples for `render_figure.py`.
- `references/style-guide.md` — visual conventions (layout, color, data plots, schematics, typography).
- `references/source-library.md` — the 13 reference papers and their reusable design DNA.
- `references/quality-checklist.md` — pre-delivery checklist.
- `assets/theme.json` — palettes, fonts, line/marker defaults.
- `scripts/render_figure.py` — multi-panel data chart renderer (line/scatter/bar/heatmap, CSV or inline data).
- `scripts/render_schematic.py` — declarative flat-vector schematic renderer.
