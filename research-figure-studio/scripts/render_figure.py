#!/usr/bin/env python3
"""Render reproducible multi-panel scientific figures from JSON and optional CSV."""

import argparse
import csv
import json
import math
import sys
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing plotting dependency. Run: python -m pip install matplotlib numpy"
    ) from exc


def load_json(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def numeric(values):
    try:
        result = [float(value) for value in values]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Expected numeric values, got: {values!r}") from exc
    if not all(math.isfinite(value) for value in result):
        raise ValueError("Non-finite values are not supported; clean or explicitly mask them first")
    return result


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"CSV has no data rows: {path}")
    return {key: [row[key] for row in rows] for key in rows[0]}


def resolve_values(value, table, as_numeric=True):
    if isinstance(value, str):
        if table is None or value not in table:
            raise ValueError(f"CSV column not found: {value}")
        value = table[value]
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"Expected an array or CSV column name, got: {value!r}")
    return numeric(value) if as_numeric else [str(item) for item in value]


def apply_axis_options(ax, panel, theme):
    if panel.get("xlabel"):
        ax.set_xlabel(panel["xlabel"])
    if panel.get("ylabel"):
        ax.set_ylabel(panel["ylabel"])
    if panel.get("title"):
        ax.set_title(panel["title"], fontsize=theme["label_size"], pad=4)
    if panel.get("xlim"):
        ax.set_xlim(panel["xlim"])
    if panel.get("ylim"):
        ax.set_ylim(panel["ylim"])
    if panel.get("xscale"):
        ax.set_xscale(panel["xscale"])
    if panel.get("yscale"):
        ax.set_yscale(panel["yscale"])
    if panel.get("xticks") is not None:
        ax.set_xticks(panel["xticks"])
    if panel.get("yticks") is not None:
        ax.set_yticks(panel["yticks"])
    if panel.get("xticklabels") is not None and panel["type"] != "heatmap":
        ax.set_xticklabels(panel["xticklabels"])
    if panel.get("yticklabels") is not None and panel["type"] != "heatmap":
        ax.set_yticklabels(panel["yticklabels"])
    if panel.get("grid"):
        ax.grid(True, color=theme["grid_color"], linewidth=0.45, alpha=0.8)
        ax.set_axisbelow(True)


def add_reference_lines(ax, panel, theme):
    for value in panel.get("hlines", []):
        ax.axhline(value, color=theme["muted_color"], linewidth=0.7, linestyle=(0, (3, 2)), zorder=1)
    for value in panel.get("vlines", []):
        ax.axvline(value, color=theme["muted_color"], linewidth=0.7, linestyle=(0, (3, 2)), zorder=1)


def add_annotations(ax, panel, theme):
    for item in panel.get("annotations", []):
        options = {
            "fontsize": theme["tick_size"],
            "color": item.get("color", theme["text_color"]),
            "ha": "left",
            "va": "center",
        }
        if item.get("xytext") is not None:
            options["arrowprops"] = {
                "arrowstyle": "-",
                "color": item.get("color", theme["muted_color"]),
                "linewidth": 0.7,
                "shrinkA": 2,
                "shrinkB": 2,
            }
        ax.annotate(item["text"], xy=item["xy"], xytext=item.get("xytext"), **options)


def render_xy(ax, panel, table, colors, theme):
    series_list = panel.get("series", [])
    if not series_list:
        raise ValueError(f"Panel {panel.get('label', '?')} has no series")
    chart_type = panel["type"]
    bar_count = len(series_list)
    categories = None

    for index, series in enumerate(series_list):
        color = series.get("color", colors[index % len(colors)])
        label = series.get("label", f"Series {index + 1}")
        y = resolve_values(series["y"], table)
        yerr = resolve_values(series["yerr"], table) if series.get("yerr") is not None else None

        if chart_type == "bar":
            categories = resolve_values(series["x"], table, as_numeric=False)
            if len(categories) != len(y):
                raise ValueError("Bar x/y lengths differ")
            positions = np.arange(len(categories), dtype=float)
            width = 0.8 / bar_count
            offset = (index - (bar_count - 1) / 2) * width
            ax.bar(
                positions + offset,
                y,
                width=width * 0.92,
                yerr=yerr,
                label=label,
                color=color,
                alpha=series.get("alpha", 1.0),
                edgecolor="white",
                linewidth=0.45,
                error_kw={"elinewidth": 0.65, "capsize": 2, "capthick": 0.65},
            )
            continue

        x = resolve_values(series["x"], table)
        if len(x) != len(y):
            raise ValueError(f"x/y lengths differ in series {label}")
        if yerr is not None and len(yerr) != len(y):
            raise ValueError(f"y/yerr lengths differ in series {label}")

        if chart_type == "scatter":
            ax.errorbar(
                x,
                y,
                yerr=yerr,
                fmt=series.get("marker", "o"),
                markersize=series.get("markersize", theme["marker_size"]),
                markerfacecolor=color,
                markeredgecolor="white",
                markeredgewidth=0.45,
                ecolor=color,
                elinewidth=0.7,
                capsize=2,
                linestyle="none",
                alpha=series.get("alpha", 1.0),
                label=label,
            )
        else:
            marker = series.get("marker", "o" if len(x) <= 60 else "None")
            ax.errorbar(
                x,
                y,
                yerr=yerr,
                color=color,
                linewidth=series.get("linewidth", theme["line_width"]),
                linestyle=series.get("linestyle", "-"),
                marker=marker,
                markersize=series.get("markersize", theme["marker_size"]),
                markerfacecolor=color,
                markeredgecolor="white",
                markeredgewidth=0.4,
                markevery=max(1, len(x) // 12),
                ecolor=color,
                elinewidth=0.65,
                capsize=2,
                capthick=0.65,
                alpha=series.get("alpha", 1.0),
                label=label,
            )
            if series.get("ylow") is not None and series.get("yhigh") is not None:
                low = resolve_values(series["ylow"], table)
                high = resolve_values(series["yhigh"], table)
                ax.fill_between(x, low, high, color=color, alpha=0.14, linewidth=0)

    if chart_type == "bar" and categories is not None:
        ax.set_xticks(np.arange(len(categories), dtype=float))
        ax.set_xticklabels(categories)
        ax.set_xlim(-0.6, len(categories) - 0.4)


def render_heatmap(ax, panel, theme):
    z = np.asarray(panel.get("z", []), dtype=float)
    if z.ndim != 2 or z.size == 0:
        raise ValueError("Heatmap requires a non-empty two-dimensional z array")
    sequential = LinearSegmentedColormap.from_list("sequential", theme["sequential"])
    diverging = LinearSegmentedColormap.from_list("diverging", theme["diverging"])
    cmap_name = panel.get("cmap", "sequential")
    cmap = plt.get_cmap(cmap_name) if cmap_name not in {"sequential", "diverging"} else (
        sequential if cmap_name == "sequential" else diverging
    )
    norm = None
    if panel.get("center") is not None:
        norm = TwoSlopeNorm(vcenter=float(panel["center"]), vmin=float(np.nanmin(z)), vmax=float(np.nanmax(z)))
        if cmap_name == "sequential":
            cmap = diverging
    image = ax.imshow(z, origin="lower", aspect="auto", cmap=cmap, norm=norm)
    if panel.get("xticklabels") is not None:
        ax.set_xticks(np.linspace(0, z.shape[1] - 1, len(panel["xticklabels"])))
        ax.set_xticklabels(panel["xticklabels"])
    if panel.get("yticklabels") is not None:
        ax.set_yticks(np.linspace(0, z.shape[0] - 1, len(panel["yticklabels"])))
        ax.set_yticklabels(panel["yticklabels"])
    if panel.get("colorbar", True):
        colorbar = ax.figure.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
        colorbar.ax.tick_params(labelsize=theme["tick_size"], width=0.6, length=2.5)
        colorbar.outline.set_visible(False)
        if panel.get("colorbar_label"):
            colorbar.set_label(panel["colorbar_label"], fontsize=theme["label_size"])


def configure_axes(ax, theme):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_linewidth(theme["axis_width"])
        ax.spines[side].set_color(theme["text_color"])
    ax.tick_params(
        axis="both",
        which="major",
        direction="out",
        labelsize=theme["tick_size"],
        width=theme["tick_width"],
        length=theme["tick_length"],
        colors=theme["text_color"],
        pad=2,
    )
    ax.xaxis.label.set_size(theme["label_size"])
    ax.yaxis.label.set_size(theme["label_size"])
    ax.xaxis.label.set_color(theme["text_color"])
    ax.yaxis.label.set_color(theme["text_color"])
    ax.set_facecolor(theme["background"])


def validate(spec):
    warnings = []
    panels = spec.get("panels", [])
    if not panels:
        raise ValueError("Specification requires at least one panel")
    for index, panel in enumerate(panels):
        name = panel.get("label", str(index + 1))
        if panel.get("type") not in {"line", "scatter", "bar", "heatmap"}:
            raise ValueError(f"Panel {name}: unsupported type {panel.get('type')!r}")
        if not panel.get("xlabel"):
            warnings.append(f"Panel {name}: missing xlabel or unit")
        if not panel.get("ylabel"):
            warnings.append(f"Panel {name}: missing ylabel or unit")
        if len(panel.get("series", [])) > 6:
            warnings.append(f"Panel {name}: more than six series; consider direct labels or splitting")
    return warnings


def render(spec_path, output_prefix, formats, theme_path=None, dpi=None):
    spec_path = Path(spec_path).resolve()
    spec = load_json(spec_path)
    warnings = validate(spec)
    theme_file = Path(theme_path) if theme_path else Path(__file__).resolve().parent.parent / "assets" / "theme.json"
    theme = load_json(theme_file)
    colors = theme["palettes"][spec.get("palette", theme["palette"])]
    panels = spec["panels"]
    nrows = int(spec.get("nrows", 1))
    ncols = int(spec.get("ncols", len(panels)))
    if nrows * ncols < len(panels):
        raise ValueError("nrows * ncols is smaller than the number of panels")

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": theme["font_family"],
        "font.size": theme["font_size"],
        "text.color": theme["text_color"],
        "axes.unicode_minus": False,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "savefig.facecolor": theme["background"],
        "savefig.edgecolor": theme["background"],
    })
    fig, axes = plt.subplots(
        nrows,
        ncols,
        figsize=(float(spec.get("width_mm", 85)) / 25.4, float(spec.get("height_mm", 65)) / 25.4),
        layout="constrained",
        squeeze=False,
    )
    fig.set_constrained_layout_pads(w_pad=0.055, h_pad=0.065, wspace=0.08, hspace=0.10)
    fig.patch.set_facecolor(theme["background"])
    flat_axes = axes.ravel()

    for index, panel in enumerate(panels):
        ax = flat_axes[index]
        configure_axes(ax, theme)
        table = None
        if panel.get("data"):
            csv_path = Path(panel["data"])
            if not csv_path.is_absolute():
                csv_path = spec_path.parent / csv_path
            table = read_csv(csv_path.resolve())
        if panel["type"] == "heatmap":
            render_heatmap(ax, panel, theme)
        else:
            render_xy(ax, panel, table, colors, theme)
        apply_axis_options(ax, panel, theme)
        add_reference_lines(ax, panel, theme)
        add_annotations(ax, panel, theme)
        if panel.get("label"):
            ax.text(
                0,
                1.025,
                panel["label"],
                transform=ax.transAxes,
                fontsize=theme["panel_label_size"],
                fontweight="bold",
                ha="left",
                va="bottom",
                color=theme["text_color"],
            )
        legend = panel.get("legend", len(panel.get("series", [])) > 1 and panel["type"] != "heatmap")
        if legend:
            options = legend if isinstance(legend, dict) else {}
            ax.legend(
                frameon=False,
                fontsize=theme["legend_size"],
                handlelength=1.6,
                handletextpad=0.5,
                borderaxespad=0.1,
                labelspacing=0.35,
                **options,
            )

    for ax in flat_axes[len(panels):]:
        ax.axis("off")

    prefix = Path(output_prefix).resolve()
    prefix.parent.mkdir(parents=True, exist_ok=True)
    outputs = []
    for extension in formats:
        extension = extension.lower().lstrip(".")
        if extension not in {"png", "svg", "pdf"}:
            raise ValueError(f"Unsupported output format: {extension}")
        output = prefix.with_suffix(f".{extension}")
        fig.savefig(output, dpi=int(dpi or spec.get("dpi", 600)))
        outputs.append(str(output))
    plt.close(fig)
    return outputs, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", help="JSON figure specification")
    parser.add_argument("output", help="Output path without extension")
    parser.add_argument("--formats", default="png,svg", help="Comma-separated png,svg,pdf")
    parser.add_argument("--theme", help="Optional theme JSON")
    parser.add_argument("--dpi", type=int, help="Raster DPI; default 600")
    parser.add_argument("--strict", action="store_true", help="Fail on publication-readiness warnings")
    args = parser.parse_args()
    try:
        outputs, warnings = render(
            args.spec,
            args.output,
            args.formats.split(","),
            theme_path=args.theme,
            dpi=args.dpi,
        )
    except (ValueError, KeyError, FileNotFoundError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1) from exc
    print(json.dumps({"outputs": outputs, "warnings": warnings}, ensure_ascii=False, indent=2))
    if args.strict and warnings:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
