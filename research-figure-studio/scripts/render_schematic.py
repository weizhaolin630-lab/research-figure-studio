#!/usr/bin/env python3
"""Render declarative flat-vector scientific schematics (mechanism/device/process) from JSON."""

import argparse
import json
import sys
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle
except ModuleNotFoundError as exc:
    raise SystemExit("Missing plotting dependency. Run: python -m pip install matplotlib") from exc


def load_json(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def draw_text(ax, item, default_color):
    kwargs = {
        "fontsize": item.get("size", 7.2),
        "color": item.get("color", default_color),
        "ha": item.get("ha", "left"),
        "va": item.get("va", "center"),
    }
    if item.get("bold"):
        kwargs["fontweight"] = "bold"
    if item.get("italic"):
        kwargs["fontstyle"] = "italic"
    ax.text(item["x"], item["y"], item["text"], **kwargs)


def add_shape(ax, item, default_color):
    kind = item["type"]
    if kind == "rect":
        fill = item.get("fill", "none")
        edge = item.get("stroke", default_color)
        lw = item.get("lw", 0.7)
        radius = item.get("round", 0)
        if radius:
            ax.add_patch(FancyBboxPatch(
                (item["x"], item["y"]), item["w"], item["h"],
                boxstyle=f"round,pad=0.02,rounding_size={radius}",
                linewidth=lw, edgecolor=edge, facecolor=fill,
                linestyle=item.get("dash"),
            ))
        else:
            ax.add_patch(Rectangle(
                (item["x"], item["y"]), item["w"], item["h"],
                linewidth=lw, edgecolor=edge, facecolor=fill,
                linestyle=item.get("dash"),
            ))
    elif kind == "circle":
        ax.add_patch(Circle(
            (item["x"], item["y"]), item["r"],
            facecolor=item.get("fill", "none"), edgecolor=item.get("stroke", default_color),
            linewidth=item.get("lw", 0.7), linestyle=item.get("dash"),
        ))
    elif kind == "polygon":
        ax.add_patch(Polygon(
            item["points"], closed=True,
            facecolor=item.get("fill", "none"), edgecolor=item.get("stroke", default_color),
            linewidth=item.get("lw", 0.7),
        ))
    elif kind == "text":
        draw_text(ax, item, default_color)
    elif kind == "arrow":
        ax.add_patch(FancyArrowPatch(
            (item["x1"], item["y1"]), (item["x2"], item["y2"]),
            arrowstyle=item.get("style", "-|>"), mutation_scale=item.get("mutation", 9),
            linewidth=item.get("lw", 1.1), color=item.get("color", default_color),
            connectionstyle=item.get("connection", "arc3"),
            linestyle=item.get("dash"),
        ))
    else:
        raise ValueError(f"Unsupported shape type: {kind}")


def render(spec_path, output_prefix, formats, theme_path=None, dpi=None):
    spec = load_json(Path(spec_path).resolve())
    shapes = spec.get("shapes", [])
    if not shapes:
        raise ValueError("Scene requires at least one shape")

    theme = {}
    if theme_path:
        theme = load_json(theme_path)
    else:
        default_theme = Path(__file__).resolve().parent.parent / "assets" / "theme.json"
        if default_theme.exists():
            theme = load_json(default_theme)

    width_mm = float(spec.get("width_mm", 180))
    height_mm = float(spec.get("height_mm", 100))
    background = spec.get("background", theme.get("background", "#FFFFFF"))
    ink = spec.get("text_color", theme.get("text_color", "#1F2933"))

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": theme.get("font_family", ["Arial", "Liberation Sans", "DejaVu Sans"]),
        "text.color": ink,
        "axes.unicode_minus": False,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
    })
    fig = plt.figure(figsize=(width_mm / 25.4, height_mm / 25.4), facecolor=background)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width_mm)
    ax.set_ylim(0, height_mm)
    ax.axis("off")
    ax.set_facecolor(background)

    for item in shapes:
        add_shape(ax, item, ink)

    prefix = Path(output_prefix).resolve()
    prefix.parent.mkdir(parents=True, exist_ok=True)
    outputs = []
    for extension in formats:
        extension = extension.lower().lstrip(".")
        if extension not in {"png", "svg", "pdf"}:
            raise ValueError(f"Unsupported output format: {extension}")
        output = prefix.with_suffix(f".{extension}")
        fig.savefig(output, dpi=int(dpi or spec.get("dpi", 600)), facecolor=background)
        outputs.append(str(output))
    plt.close(fig)
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", help="JSON scene specification")
    parser.add_argument("output", help="Output path without extension")
    parser.add_argument("--formats", default="png,svg", help="Comma-separated png,svg,pdf")
    parser.add_argument("--theme", help="Optional theme JSON")
    parser.add_argument("--dpi", type=int, help="Raster DPI; default 600")
    args = parser.parse_args()
    try:
        outputs = render(
            args.spec,
            args.output,
            args.formats.split(","),
            theme_path=args.theme,
            dpi=args.dpi,
        )
    except (ValueError, KeyError, FileNotFoundError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(1) from exc
    print(json.dumps({"outputs": outputs}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
