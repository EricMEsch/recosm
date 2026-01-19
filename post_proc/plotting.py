import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def plot_event_distribution(x_values, y_values, ge77_values, plot_subplots=True, plot_green_cdf=True, save_path=None, x_label=None, y_label=None, alpha = 1.0):
    # Masks
    mask_no_ge77 = ge77_values == 0
    mask_ge77 = ge77_values > 0


    fig = plt.figure(figsize=(7.5, 6))
    if plot_subplots:
        gs = GridSpec(
            2, 2,
            width_ratios=[0.4, 6],
            height_ratios=[6, 0.4],
            hspace=0.09,
            wspace=0.09
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
        color='green', label='Ge-77 count = 0',
        alpha=alpha
    )
    
    ax_main.scatter(
        x_values[mask_ge77], y_values[mask_ge77],
        marker='x', s=25, linewidths=1,
        color='red', label='Ge-77 count > 0',
        alpha=alpha
    )
    
    ax_main.set_xscale('log')
    ax_main.set_yscale('log')


    ax_main.hlines(35, xmin=1e-3, xmax=x_values.max(),
                   color='orange', linestyle='--', label='Argon Threshold')
    ax_main.vlines(7, ymin=1e-3, ymax=y_values.max(),
                   color='blue', linestyle='--', label='Neutron Threshold')

    ax_main.legend()
    ax_main.grid(True, which="both", alpha=0.3)
    ax_main.set_title("Event Distribution")
    if plot_subplots:
    # -----------------------
    # Bottom CDF (x projection)
    # -----------------------
        x_red = np.sort(x_values[mask_ge77])
        cdf_x = np.arange(1, len(x_red) + 1) / len(x_red)
    
        ax_xcdf.plot(x_red, cdf_x, color='red')
        if plot_green_cdf:
            x_green = np.sort(x_values[mask_no_ge77])
            cdf_xg = np.arange(1, len(x_green) + 1) / len(x_green)
            ax_xcdf.plot(x_green, cdf_xg, color='green', alpha=0.8)
    
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
        ax_ycdf.plot(cdf_y, y_red, color='red')
        if plot_green_cdf:
            y_green = np.sort(y_values[mask_no_ge77])
            cdf_yg = np.arange(1, len(y_green) + 1) / len(y_green)
            ax_ycdf.plot(cdf_yg, y_green, color='green', alpha=0.8)
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
    
    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path)
    plt.show()
