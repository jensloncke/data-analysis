import pandas as pd
import numpy as np

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
    baseline, cut_off_value = calculate_baseline_and_cutoff(column_to_analyse)

    raw_response = calculate_response(baseline, column_to_analyse, tijd, CONFIG["constants"]["response_start_time"],
                                      CONFIG["constants"]["response_end_time"])
    iono_response = calculate_response(baseline, column_to_analyse, tijd, CONFIG["constants"]["ionomycin_start_time"],
                                       CONFIG["constants"]["ionomycin_end_time"])
    response = raw_response / iono_response

    shifted_values = column_to_analyse - baseline
    shifted_values = shifted_values.where(shifted_values > 0, 0)
    raw_auc = calculate_auc(shifted_values, CONFIG["constants"]["response_start_time"],
                            CONFIG["constants"]["response_end_time"], tijd)
    iono_auc = calculate_auc(shifted_values, CONFIG["constants"]["ionomycin_start_time"],
                             CONFIG["constants"]["ionomycin_end_time"], tijd)
    auc = raw_auc / iono_auc
    return response, auc


def analyse_data(df: pd.DataFrame):
    df = df.dropna(axis='columns', how="all")
    tijd = df["A1T"].values
    remove_columns = [column for column in df.columns if ("T" in column)]
    df = df.drop(remove_columns, axis=1)
    df_result = pd.DataFrame(columns=df.columns, index=["response", "auc"])

    for column_name, column in df.iteritems():
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

    for filename in file_list:
        data_to_analyze = pd.read_csv(path_analysis / filename, sep=";")
        result = analyse_data(data_to_analyze)
        save_name_response = filename[:-4] + "_response.csv"
        result.to_csv(path_response / save_name_response, sep=";")
        with open(path_response / "config-parameters.yml",
                  'w') as file:  # with zorgt er voor dat file.close niet meer nodig is na with block
            yaml.dump(CONFIG["constants"], file)
