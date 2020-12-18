import pandas as pd
import numpy as np
import plotnine as p9


def massage_df(data):
    df = data.drop(columns=0)
    df = df.rename(columns={1: "Time"})
    df = df[(df['Time'] > 10) & (df['Time'] < 70)]
    df = pd.melt(df, id_vars="Time", var_name="cell", value_name="calcium")
    df = df.assign(identifier=filename[:-4])

    if "KO" in filename:
        df = df.assign(gen="KO")
    else:
        df = df.assign(gen="WT")

    return df


def calculate_basal_calcium(dataframe):


if __name__ == "__main__":
    from pathlib import Path
    import os
    path_analysis = Path("C:\\Users\\u0132307\\Box Sync\\PhD\\Data\\Ca2+_FURA_microscope\\20200716-Jens-ATP-CISD2KOHeLaT1\\Basal_calcium")

    file_list = [filename for filename in os.listdir(path_analysis)
                 if filename[-4:] == ".csv" and os.path.isfile(path_analysis / filename)]
    print(file_list)

    for filename in file_list:
        data = pd.read_csv(path_analysis / filename, sep=";", header=None)
        result = massage_df(data)
        # baseline = calculate_basal_calcium(df)
        # savename = filename[:-4] + "_F_over_F0.svg"
        # plot_data(result, savename, path_analysis)
