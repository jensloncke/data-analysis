import pandas as pd
import numpy as np

import yaml

from flex_caffeine_residualCa2.configuration.config import CONFIG


def calculate_baseline(values: pd.Series, time_values, start_time, end_time):
    baseline_mask = (time_values >= start_time) & (time_values <= end_time)
    baseline = np.median(values[baseline_mask])
    return baseline


def return_time_index(timestamp, time_list):
    time_mask = (time_list >= timestamp)
    time_index = np.argmax(time_mask)
    return time_index


def calculate_response(baseline, column_values, time_values, start_time, end_time):
    peak_mask = (time_values >= start_time) & (time_values <= end_time)
    peak_value = np.max(column_values[peak_mask])
    return peak_value - baseline


def calculate_auc(shifted_values, start_time, end_time, time_values):
    begin_auc = return_time_index(start_time, time_values)
    end_auc = return_time_index(end_time, time_values)
    return np.trapz(x=time_values[begin_auc: end_auc], y=shifted_values.iloc[begin_auc: end_auc])


def analyse_column(column_to_analyse: pd.Series, tijd: np.ndarray):
    baseline_response = calculate_baseline(column_to_analyse, tijd, CONFIG["constants"]["baseline_response_start_time"],
    CONFIG["constants"]["baseline_response_end_time"])
    baseline_ionomycin = calculate_baseline(column_to_analyse, tijd, CONFIG["constants"]["baseline_ionomycin_start_time"],
    CONFIG["constants"]["baseline_ionomycin_end_time"])

    caff_response = calculate_response(baseline_response, column_to_analyse, tijd, CONFIG["constants"]["response_start_time"],
                                      CONFIG["constants"]["response_end_time"])
    iono_response = calculate_response(baseline_ionomycin, column_to_analyse, tijd, CONFIG["constants"]["ionomycin_start_time"],
                                       CONFIG["constants"]["ionomycin_end_time"])


    shifted_values_response = column_to_analyse - baseline_response
    shifted_values_ionomycin = column_to_analyse - baseline_ionomycin
    shifted_values_response = shifted_values_response.where(shifted_values_response > 0, 0)
    shifted_values_ionomycin = shifted_values_ionomycin.where(shifted_values_ionomycin > 0, 0)
    caff_auc = calculate_auc(shifted_values_response, CONFIG["constants"]["response_start_time"],
                            CONFIG["constants"]["response_end_time"], tijd)
    iono_auc = calculate_auc(shifted_values_ionomycin, CONFIG["constants"]["ionomycin_start_time"],
                             CONFIG["constants"]["ionomycin_end_time"], tijd)

    return caff_response, iono_response, caff_auc, iono_auc


def analyse_data(df: pd.DataFrame):
    df = df.dropna(axis='columns', how="all")
    tijd = df["A3T"].values
    remove_columns = [column for column in df.columns if ("T" in column)]
    df = df.drop(remove_columns, axis=1)
    df_result = pd.DataFrame(columns=df.columns, index=["caff_response", "iono_response", "caff_auc", "iono_auc"])

    for column_name, column in df.iteritems():
        caff_response, iono_response, caff_auc, iono_auc = analyse_column(column, tijd)
        df_result.loc["caff_response", column_name] = caff_response
        df_result.loc["iono_response", column_name] = iono_response
        df_result.loc["caff_auc", column_name] = caff_auc
        df_result.loc["iono_auc", column_name] = iono_auc
    return df_result


if __name__ == "__main__":
    import os

    path_analysis = CONFIG["paths"]["data"]
    path_response = CONFIG["paths"]["response"]

    file_list = [filename for filename in os.listdir(path_analysis)
                 if filename[-4:] == ".csv" and os.path.isfile(path_analysis / filename)]
    print(file_list)

    for filename in file_list:
        data_to_analyze = pd.read_csv(path_analysis / filename, sep=";", skiprows=1)
        result = analyse_data(data_to_analyze)
        save_name_response = filename[:-4] + "_response.csv"
        result.to_csv(path_response / save_name_response, sep=";")
        with open(path_response / "config-parameters.yml",
                  'w') as file:  # with zorgt er voor dat file.close niet meer nodig is na with block
            yaml.dump(CONFIG["constants"], file)