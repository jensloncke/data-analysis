import pandas as pd
import numpy as np
import os

import yaml

from microscopy_caffeine.configuration.config import CONFIG

def calculate_baseline_and_cutoff(values: pd.Series):
    minimum = values.min()
    maximum = values.max()
    span = maximum - minimum
    cutoff = minimum + span * CONFIG["constants"]["cut_off_percentage"]
    mask = (values >= minimum) & (values < cutoff)
    baseline = np.median(values[mask])
    return baseline, cutoff

def determine_peak_start_and_end_indices(values, cutoff, timestamps, peak_time, analysis_mask):
    peak_width = CONFIG["constants"]["max_peak_width"]
    window_mask = (timestamps > peak_time - peak_width) & (timestamps < peak_time + peak_width) & analysis_mask
    above_cutoff = values > cutoff
    above_cutoff[~window_mask] = False
    peak_start = np.argmax(above_cutoff)
    peak_end = len(above_cutoff) - np.argmax(above_cutoff[::-1])
    return peak_start - CONFIG["constants"]["peak_index_delta"], peak_end + CONFIG["constants"]["peak_index_delta"] + 1

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
    import os

    path_analysis = CONFIG["paths"]["data"]
    path_response = CONFIG["paths"]["response"]

    file_list = [filename for filename in os.listdir(path_analysis)
                 if filename[-4:] == ".csv" and os.path.isfile(path_analysis / filename)]
    print(file_list)

# put this block BEHIND hashtags if you want to decide baseline for every seperate file
#     for filename in file_list:
#         data_to_analyze = pd.read_csv(path_analysis / filename, sep=";")
#         result = analyse_data(data_to_analyze)
#         save_name_response = filename[:-4] + "_response.csv"
#         result.to_csv(path_response / save_name_response, sep=";")


