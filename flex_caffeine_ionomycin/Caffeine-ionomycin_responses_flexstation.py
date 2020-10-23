import pandas as pd
import numpy as np
import os
import plotly
from pathlib import Path

path_analysis = Path("C:\\Users\\u0132307\\Box Sync\\PhD\\Data\\Ca2+_FURA_flexstation\\20200928-Trex293CISD2-Caff-Ionomycin\\20200928-Trex293CISD2-Caff-Ionomycin-1")
path_response = Path("C:\\Users\\u0132307\\Box Sync\\PhD\\Data\\Ca2+_FURA_flexstation\\20200928-Trex293CISD2-Caff-Ionomycin\\20200928-Trex293CISD2-Caff-Ionomycin-1\\Response")
os.makedirs(path_response, exist_ok=True)

def analysedata(filename, path_analysis, path_response):
    data = pd.read_csv(path_analysis / filename, sep=";", skiprows=[0])
    data = data.dropna(axis='columns', how="all")
    data["time"] = data["A1T"]
    remove_columns = [column for column in data.columns if ("T" in column)]
    data.drop(remove_columns, axis=1, inplace=True)
    print(remove_columns)
    print(data.head())
    tijd = data["time"].values  # numpy array met enkel de waardes =/= pandas series
    selectedcolumns = [column for column in data.columns if "time" not in column]
    result_dataframe = pd.DataFrame(columns=selectedcolumns, index=["response"])

    for column_name in selectedcolumns:
        selectedcolumn = data[column_name]
        minimum = selectedcolumn.min()
        maximum = selectedcolumn.max()
        span = maximum - minimum
        cutoff = minimum + 0.05 * span
        mask = (selectedcolumn >= minimum) & (selectedcolumn < cutoff)
        mediaan = np.median(selectedcolumn[mask])  # neemt alle waardes uit selectedcolumn waarvoor True in mask

        peakmask = (tijd >= 100) & (tijd < 300)
        peak_index = np.argmax(selectedcolumn[peakmask])  # index van max van een array
        peak = selectedcolumn[peakmask].iloc[peak_index]
        response = peak - mediaan
        ionomask = (tijd >= 300)
        iono_index = np.argmax(selectedcolumn[ionomask]) # index van max van ionomycin response
        iono_max = selectedcolumn[ionomask].iloc[iono_index]
        iono_peak = iono_max - mediaan
        response_norm = response / iono_peak
        result_dataframe.loc["response", column_name] = response_norm  # .loc[row, column]

    savenameresponse = filename[:-4] + "_response.csv"
    result_dataframe.to_csv(path_response / savenameresponse, sep=";")

    filelist = [filename for filename in os.listdir(path_analysis) if filename[-4:] == ".csv" and os.path.isfile(
        path_analysis / filename)]
    print(filelist)

if __name__ == "__main__":
    filename = "20200928-Trex290CISD2-Caff-Ionomycin-1.csv"
    # filelist = [filename for filename in os.listdir(path_analysis) if filename[-4:] == ".csv" and os.path.isfile(
    #     path_analysis / filename)]
    # print(filelist)

    analysedata(filename, path_analysis, path_response)

    # peak_time = tijd[peakmask][peak_index]
    # peakwidth = 50
    # windowmask = (tijd > peak_time - peakwidth) & (tijd < peak_time + peakwidth) & peakmask
    # above_cutoff = selectedcolumn > cutoff
    # above_cutoff[~windowmask] = False  # overal waar windowmask false was --> false in above_cutoff
    # peak_start = np.argmax(above_cutoff) - 2
    # peak_end = len(above_cutoff) - np.argmax(above_cutoff[::-1]) + 3
    #
    # shifted_values = selectedcolumn - mediaan
    # shifted_values = shifted_values.where(shifted_values > 0, 0)
    # area = np.trapz(x=tijd[peak_start:peak_end], y=shifted_values.iloc[peak_start:peak_end])
    # result_dataframe.loc["auc", column_name] = area



