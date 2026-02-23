import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

import legendstyles
plt.style.use(legendstyles.LEGEND)

TEXT_WIDTH = 5.906
FIGSIZE = {
    'single': (TEXT_WIDTH * 0.7, TEXT_WIDTH * 0.7 * 0.618),
    'wide': (TEXT_WIDTH * 0.7, TEXT_WIDTH * 0.7 * 0.5),
}

plt.rcParams.update({
    'font.size': 8,
    'axes.labelsize': 9,
    'axes.titlesize': 10,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
    'lines.linewidth': 1.2,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.format': 'pdf',
    'font.family': 'sans-serif',
})

def label_with_unit(name, unit=None):
    if unit:
        return f'{name} in {unit}'
    return name

def style_axes(ax, title=None, xlabel=None, ylabel=None, xscale=None, yscale=None):
    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if xscale:
        ax.set_xscale(xscale)
    if yscale:
        ax.set_yscale(yscale)
    ax.grid(True, alpha=0.3, which='both')
    ax.set_axisbelow(True)

def watermark(ax):
    try:
        legendstyles.legend_watermark(ax, logo_suffix='-1000', approved=True)
    except Exception:
        pass

def plot_event_distribution(x_values, y_values, ge77_values, plot_subplots=True, plot_green_cdf=True, save_path=None, x_label=None, y_label=None, alpha = 1.0):
    # Masks
    mask_no_ge77 = ge77_values == 0
    mask_ge77 = ge77_values > 0


    fig = plt.figure(figsize=FIGSIZE['single'], dpi=300)
    if plot_subplots:
        gs = GridSpec(
            2, 2,
            width_ratios=[0.4, 6],
            height_ratios=[6, 0.4],
            hspace=0.18,
            wspace=0.18
        )
        ax_main = fig.add_subplot(gs[0, 1])
        ax_xcdf = fig.add_subplot(gs[1, 1], sharex=ax_main)
        ax_ycdf = fig.add_subplot(gs[0, 0], sharey=ax_main)
    else:
        gs = GridSpec(
            1, 1,
        )
        ax_main = fig.add_subplot(gs[0, 0])

    # -----------------------
    # Main scatter plot
    # -----------------------
    ax_main.scatter(
        x_values[mask_no_ge77], y_values[mask_no_ge77],
        marker='x', s=25, linewidths=1,
        color=legendstyles.colors.achatblue, label='Ge-77 count = 0',
        alpha=alpha
    )
    
    ax_main.scatter(
        x_values[mask_ge77], y_values[mask_ge77],
        marker='x', s=25, linewidths=1,
        color=legendstyles.colors.DeepCove, label='Ge-77 count > 0',
        alpha=alpha
    )
    
    ax_main.set_xscale('log')
    ax_main.set_yscale('log')


    ax_main.hlines(35, xmin=1e-3, xmax=x_values.max(),
                   color='orange', linestyle='--', label='Argon Threshold')
    ax_main.vlines(7, ymin=1e-3, ymax=y_values.max(),
                   color='blue', linestyle='--', label='Neutron Threshold')

    ax_main.legend()
    ax_main.grid(True, which="both", alpha=0.1, linestyle='--')
    ax_main.set_title("Event Distribution")
    if plot_subplots:
    # -----------------------
    # Bottom CDF (x projection)
    # -----------------------
        x_red = np.sort(x_values[mask_ge77])
        cdf_x = np.arange(1, len(x_red) + 1) / len(x_red)
    
        ax_xcdf.plot(x_red, cdf_x, color=legendstyles.colors.DeepCove)
        if plot_green_cdf:
            x_green = np.sort(x_values[mask_no_ge77])
            cdf_xg = np.arange(1, len(x_green) + 1) / len(x_green)
            ax_xcdf.plot(x_green, cdf_xg, color=legendstyles.colors.achatblue)
    
        ax_xcdf.set_xscale('log')
        ax_xcdf.set_ylim(0, 1)
    
    
        #ax_xcdf.set_ylabel("CDF")
        ax_xcdf.set_xlabel(x_label if x_label is not None else r"Waterveto tagged neutrons")
    
        # -----------------------
        # Left CDF (y projection, flipped)
        # -----------------------
        y_red = np.sort(y_values[mask_ge77])
        cdf_y = np.arange(1, len(y_red) + 1) / len(y_red)
    
        # NOTE: CDF is now on x-axis
        ax_ycdf.plot(cdf_y, y_red, color=legendstyles.colors.DeepCove)
        if plot_green_cdf:
            y_green = np.sort(y_values[mask_no_ge77])
            cdf_yg = np.arange(1, len(y_green) + 1) / len(y_green)
            ax_ycdf.plot(cdf_yg, y_green, color=legendstyles.colors.achatblue, alpha=0.8)
        ax_ycdf.set_xlim(0, 1)
        ax_ycdf.set_yscale('log')
    
    
        ax_ycdf.set_xlabel("CDF")
        ax_ycdf.set_ylabel(y_label if y_label is not None else "Argonveto scintillation photons detected")
    
        ax_ycdf.invert_xaxis()
        # -----------------------
        # Tick cleanup
        # -----------------------
        plt.setp(ax_main.get_xticklabels(), visible=False)
        plt.setp(ax_main.get_yticklabels(), visible=False)
    else:
        ax_main.set_xlabel(x_label if x_label is not None else "Waterveto tagged neutrons")
        ax_main.set_ylabel(y_label if y_label is not None else "Argonveto scintillation photons detected")
    
    watermark(ax_main)
    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path)
    plt.show()
