import pandas as pd
import numpy as np
import os

import yaml

from flex_caffeine_ionomycin.configuration.config import CONFIG

def calculate_baseline_and_cutoff(values: pd.Series):
    minimum = values.min()
    maximum = values.max()
    span = maximum - minimum
    cutoff = minimum + span * CONFIG["constants"]["cut_off_percentage"]
    mask = (values >= minimum) & (values < cutoff)
    baseline = np.median(values[mask])
    return baseline, cutoff

def determine_peak_start_and_end_indices(values, peak_mask):
    peak_window = values[peak_mask]
    peak_start = np.argmax(peak_window)
    peak_end = len(peak_window) - np.argmax(peak_window[::-1])
    return peak_start, peak_end


def determine_ionomycin_start_and_end_indices(values, iono_mask):
    iono_window = values[iono_mask]
    iono_start = np.argmax(iono_window)
    iono_end = len(peak_window) - np.argmax(peak_iono[::-1])
    return iono_start, iono_end


def analyse_column(column_to_analyse: pd.Series, tijd: np.ndarray):
    baseline, cut_off_value = calculate_baseline_and_cutoff(column_to_analyse)

    peak_mask = (tijd >= CONFIG["constants"]["response_start_time"]) & (tijd <= CONFIG["constants"]["response_end_time"])
    peak_index = np.argmax(column_to_analyse[peak_mask])
    peak_value = column_to_analyse[peak_mask].iloc[peak_index]
    raw_response = peak_value - baseline
    iono_mask = (tijd >= CONFIG["constants"]["ionomycin_start_time"]) & (tijd <= CONFIG["constants"]["ionomycin_end_time"])
    iono_index = np.argmax(column_to_analyse[iono_mask])
    iono_value = column_to_analyse[iono_mask].iloc[iono_index]
    iono_response = iono_value - baseline
    response = raw_response / iono_response
    peak_start, peak_end = determine_peak_start_and_end_indices(column_to_analyse, peak_mask)
    iono_start, iono_end = determine_ionomycin_start_and_end_indices(column_to_analyse, iono_mask)
    shifted_values = column_to_analyse - baseline
    shifted_values = shifted_values.where(shifted_values > 0, 0)
    raw_auc = np.trapz(x=tijd[peak_start: peak_end], y=shifted_values.iloc[peak_start_idx: peak_end_idx])
    iono_auc = np.trapz(x=tijd[iono_start: iono_end], y=shifted_values.iloc[iono_start_idx: iono_end_idx])
    auc = raw_auc / iono_auc
    return response, auc


def analyse_data(df: pd.DataFrame):
    df = df.dropna(axis='columns', how="all")
    df["time"] = df["A1T"]
    remove_columns = [column for column in df.columns if ("T" in column)]
    df.drop(remove_columns, axis=1, inplace=True)
    tijd = df["time"].values
    selected_columns = [column for column in df.columns if "time" not in column]
    df_to_analyse = df[selected_columns]
    df_result = pd.DataFrame(columns=selected_columns, index=["response", "auc"])

    for column_name, column in df_to_analyse.iteritems():
        response, auc = analyse_column(column, tijd)
        df_result.loc["response", column_name] = response
        df_result.loc["auc", column_name] = auc

    return df_result


if __name__ == "__main__":
    import os

    path_analysis = CONFIG["paths"]["data"]
    path_response = CONFIG["paths"]["response"]

    file_list = [filename for filename in os.listdir(path_analysis)
                 if filename[-4:] == ".csv" and os.path.isfile(path_analysis / filename)]
    print(file_list)

# put this block BEHIND hashtags if you want to decide baseline for every seperate file
    for filename in file_list:
        data_to_analyze = pd.read_csv(path_analysis / filename, sep=";")
        result = analyse_data(data_to_analyze)
        save_name_response = filename[:-4] + "_response.csv"
        result.to_csv(path_response / save_name_response, sep=";")


