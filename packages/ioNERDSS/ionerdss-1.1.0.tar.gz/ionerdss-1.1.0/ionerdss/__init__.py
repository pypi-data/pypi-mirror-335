from .model_setup import *
from .analysis import *
from .nerdss_model import *
from .nerdss_simulation import *
from .nerdss_analysis import *

import seaborn as sns

# Set the figure style using Seaborn
fontsize = 12
sns.set_style("ticks")
sns.set_context("paper", rc={
    "font.size": fontsize,
    "axes.titlesize": fontsize,
    "axes.labelsize": fontsize,
    "xtick.labelsize": fontsize,
    "ytick.labelsize": fontsize,
    "legend.fontsize": fontsize,
    "font.family": "serif"
})

# print the version of the package
import pkg_resources
__version__ = pkg_resources.get_distribution("ioNERDSS").version
print(f"ioNERDSS version {__version__} loaded.")
