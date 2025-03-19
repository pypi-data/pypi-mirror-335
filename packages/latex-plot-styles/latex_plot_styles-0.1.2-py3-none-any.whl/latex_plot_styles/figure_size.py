from .configs import Config, THESIS_CONFIG

def get_size(config:Config|None=THESIS_CONFIG, width:float|None=None, fraction:float=1, subplots:tuple[int, int]=(1,1)):
    """Get a LaTeX-compatible figure size for a given fraction of the text width and a given aspect ratio.

    Parameters
    ----------
    config : Config, optional
        Configuration object. Default is THESIS_CONFIG.
    width : float|None
        Width of the plot in points. Default is None and the width is taken from the config object. If the width is provided, the config object is ignored.
    fraction : float, optional
        Fraction of the text width to occupy. Default is 1.
    subplots : tuple, optional
        Number of subplots. Default is (1,1).

    Returns
    -------
    tuple
        Figure size in inches.
    """
    # Inspired by https://jwalton.info/Embed-Publication-Matplotlib-Latex/
    if width is None and config is None:
        raise ValueError("At least one of width or config must be provided.")
    
    if width is None:
        width = config.width
    
    fig_width_pt = width * fraction
    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    # https://disq.us/p/2940ij3
    golden_ratio = (5**.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in * golden_ratio * (subplots[0] / subplots[1])

    return (fig_width_in, fig_height_in)
