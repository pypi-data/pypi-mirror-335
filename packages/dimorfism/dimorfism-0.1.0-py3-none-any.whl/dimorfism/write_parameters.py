import json
from dimorfism.setup_data import split_data
from dimorfism.fit_logistic_regression import get_fitted_model


def get_model_parameters(selected_data):
    splited_data = split_data(selected_data)
    fitted_model = get_fitted_model(splited_data)
    parameters_dictionary = obtained_parameters(fitted_model)
    return parameters_dictionary


def obtained_parameters(fitted_model):
    keys = [str(name) for name in fitted_model.feature_names_in_] + ["Intercept"]
    values = [*fitted_model.coef_[0], fitted_model.intercept_.item()]
    return {k: float(v) for (k, v) in zip(keys, values)}


def write_json_parameters(parameters_dictionary, parameters_path):
    with open(parameters_path, "w") as outfile:
        json.dump(parameters_dictionary, outfile)
