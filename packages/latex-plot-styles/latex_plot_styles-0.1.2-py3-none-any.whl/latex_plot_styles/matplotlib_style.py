import matplotlib.pyplot as plt
import seaborn as sns
from .configs import Config, THESIS_CONFIG

def set_style(
    config:Config=THESIS_CONFIG,
):
    """Set the style of the plot according to the configuration object.

    Parameters
    ----------
    config : Config, optional
        Configuration object. Default is THESIS_CONFIG.
    """
    tex_fonts = {
        "text.usetex": config.use_tex,
        "font.family": config.font_family,
        f"font.{config.font_family}": [config.font],
        "axes.labelsize": config.axes_labelsize,
        "font.size": config.font_size,
        "legend.fontsize": config.legend_fontsize,
        "xtick.labelsize": config.xtick_labelsize,
        "ytick.labelsize": config.ytick_labelsize,
    }
    plt.style.use(config.stylesheet_name)
    plt.style.use(tex_fonts)
    colors = sns.color_palette(config.color_palette)
    sns.set_palette(colors)