from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


PAPER_STYLE = {
    "font.family": "serif",
    "font.serif": ["Times New Roman"],
    "mathtext.fontset": "stix",
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "grid.alpha": 0.3,
}


def apply_paper_style() -> None:
    """Apply the figure style used by the original notebooks."""
    plt.rcParams.update(PAPER_STYLE)


def plot_lpr_data(
    data: np.ndarray,
    title: str = "CE-4 LPR Data",
    lims: float | None = None,
    dx: float = 0.03,
    figsize: tuple[float, float] = (8, 4.8),
    cmap: str = "seismic",
):
    """Plot an LPR radargram with the original paper-style red-blue template.

    The function detects common Chang'e LPR data orientations and keeps the
    vertical axis as depth/time samples. It uses an equal-height colorbar and a
    top trace-number axis, matching the plotting convention from the legacy
    notebook.
    """
    data = np.asarray(data)
    valid_depths = [2048, 8192]
    rows, cols = data.shape

    if rows in valid_depths and cols not in valid_depths:
        data_plot = data
        n_depth, n_trace = rows, cols
    elif cols in valid_depths and rows not in valid_depths:
        data_plot = data.T
        n_depth, n_trace = cols, rows
    else:
        data_plot = data
        n_depth, n_trace = rows, cols

    x_max = n_trace * dx

    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 14
    plt.rcParams["axes.linewidth"] = 1.2

    fig, ax = plt.subplots(figsize=figsize)

    calc_lims = np.percentile(np.abs(data_plot), 98) if lims is None else lims
    im = ax.imshow(
        data_plot,
        aspect="auto",
        cmap=cmap,
        vmin=-calc_lims,
        vmax=calc_lims,
        origin="upper",
        extent=[0, x_max, n_depth, 0],
        interpolation="none",
    )

    ax.set_xlabel(f"Distance (m) [$\\Delta x$={dx:.2f} m]", fontweight="bold")
    ax.set_ylabel("Depth (samples)", fontweight="bold")
    ax.set_title(title, pad=15, fontsize=16, fontweight="bold")
    ax.tick_params(direction="in", length=5, width=1, colors="k", top=False)
    ax.grid(False)

    ax_top = ax.secondary_xaxis("top", functions=(lambda x: x / dx, lambda t: t * dx))
    ax_top.set_xlabel("Trace Number", labelpad=10, fontweight="bold")
    ax_top.tick_params(direction="in")

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.1)
    cbar = plt.colorbar(im, cax=cax)
    cbar.set_label("Amplitude (a.u.)", rotation=270, labelpad=15, fontweight="bold")
    cbar.ax.tick_params(direction="in")

    plt.tight_layout()
    return fig, ax


def plot_variance_analysis(
    variances: np.ndarray,
    boundaries: np.ndarray | list[int],
    thresholds: np.ndarray | list[float],
    segments: list[tuple[int, int]],
    data: np.ndarray | None = None,
    n_traces: int | None = None,
    ylim: tuple[float, float] | None = (0, 700),
    title: str = "Variance Analysis",
    figsize: tuple[float, float] = (12, 8),
    data_lims: float = 50,
):
    """Plot variance threshold result and synchronized radargram valid regions."""
    signal_color = "#95A5A6"
    valid_color = "#C0392B"
    thresh_color = "#DAA520"
    split_color = "gray"

    variances = np.asarray(variances)
    boundaries = np.asarray(boundaries, dtype=int)
    thresholds = np.asarray(thresholds, dtype=float)
    n_traces = int(n_traces or len(variances))

    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["Times New Roman"]
    plt.rcParams["mathtext.fontset"] = "stix"
    plt.rcParams["axes.unicode_minus"] = False

    font_title = 18
    font_label = 16
    font_tick = 14
    font_legend = 14

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=figsize,
        sharex=True,
        constrained_layout=True,
        gridspec_kw={"height_ratios": [1, 1.5]},
    )

    ax1.plot(
        variances,
        color=signal_color,
        linewidth=1.0,
        alpha=0.9,
        label="Signal Variance",
        zorder=1,
    )

    for i in range(len(boundaries) - 1):
        start, end = int(boundaries[i]), int(boundaries[i + 1])
        threshold = thresholds[i] if i < len(thresholds) else np.nan
        ax1.plot(
            range(start, end),
            [threshold] * (end - start),
            "--",
            color=thresh_color,
            linewidth=2.0,
            alpha=1.0,
            zorder=5,
        )

    for x_pos in boundaries[1:-1]:
        ax1.axvline(x_pos, color=split_color, linestyle=":", linewidth=1.5, alpha=0.6, zorder=0)

    if data is None:
        data_plot = np.zeros((1, len(variances)), dtype=float)
    else:
        data_plot = np.asarray(data)

    ax2.imshow(
        data_plot,
        aspect="auto",
        cmap="seismic",
        vmin=-data_lims,
        vmax=data_lims,
        interpolation="nearest",
        zorder=0,
    )

    for x_pos in boundaries[1:-1]:
        ax2.axvline(x_pos, color="black", linestyle=":", linewidth=1.5, alpha=0.3, zorder=20)

    for start, end in segments:
        ax1.axvspan(start, end, color=valid_color, alpha=0.35, lw=0, zorder=10)
        ax2.axvspan(start, end, color=valid_color, alpha=0.35, lw=0, zorder=10)

    ax1.set_xlim(0, n_traces)
    if ylim is not None:
        ax1.set_ylim(*ylim)

    ax1.set_ylabel("Amplitude Variance", fontsize=font_label, fontweight="bold", color="black")
    if title:
        ax1.set_title(title, fontsize=font_title, pad=25, color="black", fontweight="bold")
    ax1.grid(True, linestyle="-", alpha=0.1, zorder=0)
    ax1.tick_params(axis="y", labelsize=font_tick, direction="in")
    ax1.tick_params(labelbottom=False)

    ax2.set_ylabel("Depth (samples)", fontsize=font_label, fontweight="bold", color="black")
    ax2.set_xlabel("Trace Index", fontsize=font_label, fontweight="bold", color="black")
    ax2.tick_params(axis="both", which="major", labelsize=font_tick, direction="in", length=5, width=1)

    legend_elements = [
        plt.Line2D([0], [0], color=signal_color, lw=2, alpha=0.8, label="Variance"),
        plt.Line2D([0], [0], color=thresh_color, lw=2, linestyle="--", label="Threshold"),
        plt.Rectangle((0, 0), 1, 1, color=valid_color, alpha=0.5, label="Valid Region"),
        plt.Line2D([0], [0], color=split_color, linestyle=":", lw=2, label="Segmentation"),
    ]
    ax1.legend(
        handles=legend_elements,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        ncol=4,
        frameon=False,
        fontsize=font_legend,
        columnspacing=1.5,
    )

    return fig, (ax1, ax2)
