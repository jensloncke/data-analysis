import pandas as pd
import numpy as np
import yaml
import plotly.express as px
from configuration.config import CONFIG


def read_and_clean_df(path, file):
    data_to_analyze = pd.read_csv(path / file, sep="\t", skiprows=2)
    data_to_analyze.drop(data_to_analyze.tail(12).index, inplace=True)
    data_to_analyze.drop(data_to_analyze.head(2).index, inplace=True)
    df = data_to_analyze.stack().str.replace(',', '.').unstack()
    df.drop(list(df.filter(regex="Temp")), axis=1, inplace=True)
    df = df.astype(float)
    df = set_index(df.dropna(axis=1))
    df.drop(list(df.filter(regex = "T")), axis = 1, inplace = True)
    return df


def set_index(df: pd.DataFrame):
    matches = ["B3T"]
    if any(match in df.columns for match in matches):
        colnames = df.columns.tolist()
        match = ''.join(list(set(colnames) & set(matches)))
        tijd = [col for col in df.astype(float).columns if match in col]
        df.set_index(tijd, inplace=True)
        df.dropna(inplace=True)
        return df.copy()
    else:
        return df.copy()


def calculate_baseline(values: pd.Series, start_time, end_time):
    baseline = np.median(pd.to_numeric(values).loc[start_time:end_time,])
    return baseline


def calculate_response(baseline, column_values, start_time, end_time):
    peak_value = np.max(column_values.loc[start_time:end_time,])
    return peak_value - baseline


def calculate_auc(shifted_values, start_time, end_time):
    slice = shifted_values.loc[start_time:end_time,]
    return np.trapz(y=slice)


def analyse_column(column_to_analyse: pd.Series):
    baseline_response = calculate_baseline(column_to_analyse, CONFIG["constants"]["baseline_response_start_time"], CONFIG["constants"]["baseline_response_end_time"])

    response = calculate_response(baseline_response, column_to_analyse, CONFIG["constants"]["response_start_time"],
                                      CONFIG["constants"]["response_end_time"])
    shifted_values_response = column_to_analyse - baseline_response
    shifted_values_response = shifted_values_response.where(shifted_values_response > 0, 0)
    AUC = calculate_auc(shifted_values_response, CONFIG["constants"]["response_start_time"],
                            CONFIG["constants"]["response_end_time"])

    return response, AUC


def analyse_data(df: pd.DataFrame):
    df_result = pd.DataFrame(columns=df.columns, index=["Response", "AUC"])

    for column_name, column in df.iteritems():
        response, AUC = analyse_column(column)
        df_result.loc["Response", column_name] = response
        df_result.loc["AUC", column_name] = AUC
    return df_result


def plot_data(df, save_name_plot, path):
    fig = px.line(df, title = save_name_plot[:-4])
    fig_save = os.path.join(path, save_name_plot)
    fig.write_html(fig_save)


def save_data(result: pd.DataFrame, df: pd.DataFrame, path, filename):
    save_name_response = filename[:-4] + "_response.csv"
    save_name_data = filename[:-4] + "_data.csv"
    save_name_plot = filename[:-4] + "_plot.html"
    plot_data(df, save_name_plot, path)
    result.to_csv(path / save_name_response, sep=";")
    df.to_csv(path / save_name_data, sep=";")
    with open(path / "config-parameters.yml",
              'w') as file:  # with zorgt er voor dat file.close niet meer nodig is na with block
        yaml.dump(CONFIG["constants"], file)


if __name__ == "__main__":
    import os
    path_analysis = CONFIG["paths"]["data"]
    path_response = CONFIG["paths"]["response"]

    file_list = [filename for filename in os.listdir(path_analysis)
                 if filename[-4:] == ".txt" and os.path.isfile(path_analysis / filename)]
    print(file_list)

    for filename in file_list:
        df = read_and_clean_df(path_analysis, filename)
        result = analyse_data(df)
        save_data(result, df, path_response, filename)