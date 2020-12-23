import pandas as pd
import numpy as np
import plotnine as p9
from statsmodels.stats.weightstats import ttest_ind


def massage_df(data):
    df = data.drop(columns=0)
    df = df.rename(columns={1: "Time"})
    return df


def calculate_basal_calcium(dataframe: pd.DataFrame):
    dataframe = dataframe[(dataframe['Time'] > 10) & (dataframe['Time'] < 70)]
    dataframe = dataframe.drop(labels="Time", axis=1)
    return dataframe.median()


if __name__ == "__main__":
    from pathlib import Path
    import os
    path_analysis = Path("C:\\Users\\u0132307\\Box Sync\\PhD\\Data\\Ca2+_FURA_microscope\\20200716-Jens-ATP-CISD2KOHeLaT1\\Basal_calcium")
    path_basal = Path("C:\\Users\\u0132307\\Box Sync\\PhD\\Data\\Ca2+_FURA_microscope\\20200716-Jens-ATP-CISD2KOHeLaT1\\Basal_calcium\\Plot")
    os.makedirs(path_basal, exist_ok=True)
    file_list = [filename for filename in os.listdir(path_analysis)
                 if filename[-4:] == ".csv" and os.path.isfile(path_analysis / filename)]
    print(file_list)
    baselines_list = []

    for filename in file_list:
        data = pd.read_csv(path_analysis / filename, sep=";", header=None)
        result = massage_df(data)
        baseline = calculate_basal_calcium(result)
        baseline = baseline.to_frame()
        baseline["identifier"] = filename[:-4]
        if "KO" in filename:
            baseline["gen"] = "CISD2 KO"
        else:
            baseline["gen"] = "WT"
        baselines_list.append(baseline)

    pooled_data = pd.concat(baselines_list, axis=0, ignore_index=True)
    pooled_data = pooled_data.rename(columns={0: 'calcium'})
    pooled_data.to_csv(path_basal / "plot.csv", sep=";")

    WT = pooled_data.loc[pooled_data['gen'] == 'WT', 'calcium']
    KO = pooled_data.loc[pooled_data['gen'] == 'CISD2 KO', 'calcium']
    print(ttest_ind(WT, KO))