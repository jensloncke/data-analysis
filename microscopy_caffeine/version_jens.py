from pathlib import Path
import os
import pandas as pd
import numpy as np
from plotly import graph_objs as go
from plotly import offline as po

#path_analysis = Path("C:\\Users\\u0132307\\Box Sync\\PhD\\Data\\Ca2+ FURA microscope\\20200908-FURA2AM-HEK-RyR2CISD2-CTRL-KO\\Analysis")
#path_response = Path("C:\\Users\\u0132307\\Box Sync\\PhD\\Data\\Ca2+ FURA microscope\\20200908-FURA2AM-HEK-RyR2CISD2-CTRL-KO\\response")
path_analysis = Path(__file__).parent / "data"
path_response = path_analysis / "response"
os.makedirs(path_response, exist_ok=True)


def analysedata(filename, path_analysis, path_response):
    df = pd.read_csv(path_analysis / filename, sep=";")
    selectedcolumns = [column for column in df.columns if ("Ratio") in column]
    tijd = df["TimeStamp::TimeStamp!!D"].values  #numpy array met enkel de waardes =/= pandas series

    result_dataframe = pd.DataFrame(columns=selectedcolumns, index=["response", "auc"])

    for column_name in selectedcolumns:
        selectedcolumn = df[column_name]
        minimum = selectedcolumn.min()
        maximum = selectedcolumn.max()
        span = maximum - minimum
        cutoff = minimum + 0.1*span
        mask = (selectedcolumn >= minimum) & (selectedcolumn < cutoff)
        mediaan = np.median(selectedcolumn[mask])  #neemt alle waardes uit selectedcolumn waarvoor True in mask

        analysismask = (tijd >= 140)
        peak_index = np.argmax(selectedcolumn[analysismask])  #index van max van een array
        peak = selectedcolumn[analysismask].iloc[peak_index]
        response = peak - mediaan
        result_dataframe.loc["response", column_name] = response  #.loc[row, column]

        peak_time = tijd[analysismask][peak_index]
        peakwidth = 50
        windowmask = (tijd > peak_time-peakwidth) & (tijd < peak_time + peakwidth) & analysismask
        above_cutoff = selectedcolumn > cutoff
        above_cutoff[~windowmask] = False  #overal waar windowmask false was --> false in above_cutoff
        peak_start = np.argmax(above_cutoff) - 2
        peak_end = len(above_cutoff) - np.argmax(above_cutoff[::-1]) + 3

        shifted_values = selectedcolumn - mediaan
        shifted_values = shifted_values.where(shifted_values > 0, 0)
        area = np.trapz(x=tijd[peak_start:peak_end], y=shifted_values.iloc[peak_start:peak_end])
        result_dataframe.loc["auc", column_name] = area

    savenameresponse = filename[:-4] + "_response.csv"
    result_dataframe.to_csv(path_response / savenameresponse, sep=";")
    print(result_dataframe)


if __name__ == "__main__":

    filelist = [filename for filename in os.listdir(path_analysis) if filename[-4:] == ".csv" and os.path.isfile(
        path_analysis / filename)]
    print(filelist)

    for filename in filelist:
        analysedata(filename, path_analysis, path_response)
        break