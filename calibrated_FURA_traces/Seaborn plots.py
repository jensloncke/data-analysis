import pandas as pd
import numpy as np
import plotnine as p9
import seaborn as sns
from matplotlib import pyplot as plt
from statsmodels.stats.weightstats import ttest_ind

def order_genotypes(genotypes):
    mapping = {"WT":0, "CISD2 KO":1}
    return genotypes.map(mapping)

if __name__ == "__main__":
    from pathlib import Path
    import os
    path_analysis = Path("C:\\Users\\u0132307\\Box Sync\\PhD\\Data\\Ca2+_FURA_microscope\\20200716-Jens-ATP-CISD2KOHeLaT1\\Basal_calcium\\Plot")
    data = pd.read_csv(path_analysis / "plot.csv", sep=";")
    print(data)
    data = data.sort_values("gen", key=order_genotypes)

    palette = ["royalblue", "firebrick"]
    pastelpalette = ["lightsteelblue", "salmon"]
    params = {"text.usetex":True, "font.family":"serif"}
    sns.set_theme(style="ticks", context="notebook", font_scale=1, palette=palette, rc=params)
    # fig,axis=plt.subplots(figsize=(5, 4))
    axis = sns.violinplot(data=data, x="gen", y="calcium", inner="quartile", palette=pastelpalette)
    axis = sns.swarmplot(data=data, x="gen", y="calcium", hue="identifier", ax=axis)
    axis.set_xlabel("Genotype")
    axis.set_ylabel(r"$\left[\textrm{Ca}^{2+}\right]_\textrm{cyt}$")
    axis.set_title(r"Basal cytosolic $\textrm{Ca}^{2+}$ levels")
    plt.tight_layout()
    plt.savefig(path_analysis / "violinplot.png")
