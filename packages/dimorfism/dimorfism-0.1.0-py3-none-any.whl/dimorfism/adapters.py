import pandas as pd


def adapter_morphometry(data_path):
    wanted_colnames: list = [
        "bill_depth",
        "bill_length",
        "head_width",
        "Tarsus",
    ]
    complete_dataframe = pd.read_csv(data_path)
    return complete_dataframe[wanted_colnames + ["sexo"]]
