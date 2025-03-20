from sklearn import linear_model


def get_fitted_model(splited_data):
    model = logistic_regression()
    x = splited_data["to_fit"]
    y = splited_data["to_fit_target"]
    fitted_model = model.fit(x, y)
    return fitted_model


def logistic_regression():
    return linear_model.LogisticRegression()
