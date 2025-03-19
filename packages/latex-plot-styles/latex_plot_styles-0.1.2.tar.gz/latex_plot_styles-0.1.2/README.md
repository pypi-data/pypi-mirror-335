# latex-plot-styles
This project can be used to makte plots created with matplotlib nicer. It simplifys the styling options by providing a nice default configuration for thesis.

## setup
`latex-plot-styles` can pe installed using pip:
```
pip install latex-plot-styles
```
To use the full functionality you need a running LaTeX installation on your system. On Debian based systems this can be installed using:
```
sudo apt install texlive-full
```

## usage
Instead of configuring the styles and sizes for all your plots you can just do
```Python
import latex_plot_styles as lps
import matplotlib.pyplot as plt

lps.set_style()
fig, ax = plt.subplots(1, 1, figsize=lps.get_size())
...
plt.savefig("your_fig.pdf", bbox_inches="tight")
```

# configure your own styles
To configure your own styles you have to create an object from class `Config` and give this config object to `lps.set_style(your_config_object)`

# warning
This is just a small side project to simlify generating plots for my masters thesis. There are no automated tests, this is not ment for production, but feel free to use and adapt it for your own stuff. 

# changelog
0.1.0 basic funcitionality for matplotlib styles<br>
0.1.1 fix typo in package name<br>
0.1.2 change default colors to seaborn dark<br>