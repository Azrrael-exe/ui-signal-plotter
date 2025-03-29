import numpy as np
from sklearn.linear_model import LinearRegression

from .component import Value


def forecast_next_value(values: list[Value]) -> Value:
    """
    Forecast the next value using linear regression based on historical values.

    Args:
        values: List of Value objects containing historical data

    Returns:
        float: Predicted next value
    """
    if len(values) < 2:
        raise ValueError("Need at least 2 values for forecasting")

    # Extract numerical values and create time indices
    y = np.array([v.value for v in values])
    X = np.array(range(len(values))).reshape(-1, 1)

    # Create and fit the model
    model = LinearRegression()
    model.fit(X, y)

    # Predict the next value
    next_index = np.array([[len(values)]])
    predicted_value = model.predict(next_index)[0]

    return Value(value=predicted_value, unit=values[0].unit)
