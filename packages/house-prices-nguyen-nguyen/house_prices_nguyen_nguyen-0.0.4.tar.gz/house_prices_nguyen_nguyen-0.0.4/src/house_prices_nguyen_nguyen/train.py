from typing import Optional

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_squared_log_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from house_prices.src.house_prices_nguyen_nguyen.preprocess import (
    get_scaler,
    get_encoder,
    process_data
)


def split_train_test_data(
        df_input: pd.DataFrame,
        selected_features: list[str],
        label_col: str
) -> (
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame
):
    """
    Split data into training and testing sets
    :param df_input: pandas DataFrame
    :param selected_features: list of features to include in the model
    :param label_col: column name of the label to predict
    :return: pd Dataframe for X_train, y_train, X_test, y_test
    """
    df = df_input[selected_features + [label_col]]
    df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)
    X_train = df_train.drop(columns=[label_col])
    y_train = df_train[[label_col]]
    X_test = df_test.drop(columns=[label_col])
    y_test = df_test[[label_col]]

    return X_train, y_train, X_test, y_test


def train_model(
        X_train: pd.DataFrame,
        y_train: pd.DataFrame
) -> xgb.XGBRegressor:
    """
    Train the model
    :param X_train:
    :param y_train:
    :return: xgboost Regressor model
    """
    model = xgb.XGBRegressor()
    model.fit(X_train, y_train)

    return model


def save_model(
        model: xgb.XGBRegressor,
        encoder: OneHotEncoder,
        scaler: StandardScaler,
        path: str
) -> None:
    """
    Save the model, encoder, and scaler to disk
    :param model: xgboost Regressor model
    :param encoder: sklearn OneHotEncoder object
    :param scaler: sklearn StandardScaler object
    :param path: path to save the model
    :return: None
    """
    joblib.dump(model, f"{path}/model.joblib")
    joblib.dump(encoder, f"{path}/encoder.joblib")
    joblib.dump(scaler, f"{path}/scaler.joblib")


def compute_rmsle(
        y_test: np.ndarray,
        y_pred: np.ndarray,
        precision: int = 2
) -> float:
    """
    Compute the Root Mean Squared Log Error
    :param y_test: The actual values in the test set
    :param y_pred: The predicted values from the model
    :param precision: The number of decimal places to round the result
    :return: float
    """
    rmsle = np.sqrt(mean_squared_log_error(y_test, y_pred))

    return round(rmsle, precision)


def process_train_and_test_data(
        X_train: pd.DataFrame,
        X_test: pd.DataFrame,
        cols_for_encode: list[str],
        cols_for_scale: list[str],
        cols_no_transform: list[str],
        one_hot_encoder: OneHotEncoder,
        scaler: StandardScaler
) -> (pd.DataFrame, pd.DataFrame):
    X_processed_train = \
        process_data(X_train, one_hot_encoder, scaler,
                     cols_for_encode, cols_for_scale, cols_no_transform)
    X_processed_test = \
        process_data(X_test, one_hot_encoder, scaler,
                     cols_for_encode, cols_for_scale, cols_no_transform)

    return X_processed_train, X_processed_test


def _build_model(
        df: pd.DataFrame,
        cols_for_encode: list[str],
        cols_for_scale: list[str],
        cols_no_transform: list[str],
        label_col: str,
        model_path: str
) -> dict:
    """
    Build the model and return the Root Mean Squared Log Error
    :param df: pandas DataFrame
    :param cols_for_encode: list of columns to encode
    :param cols_for_scale: list of columns to scale
    :param cols_no_transform: list of columns that should not be processed
    :param label_col: column name of the label to predict
    :param model_path: path to save the model
    :return: dictionary with the Root Mean Squared Log Error
    """
    (X_train, y_train, X_test, y_test) = split_train_test_data(
        df, cols_for_encode + cols_for_scale + cols_no_transform, label_col)
    one_hot_encoder = get_encoder(X_train, cols_for_encode)
    scaler = get_scaler(X_train, cols_for_scale)
    (X_processed_train, X_processed_test) = process_train_and_test_data(
        X_train, X_test, cols_for_encode, cols_for_scale,
        cols_no_transform, one_hot_encoder, scaler)
    model = train_model(X_processed_train, y_train)
    save_model(model, one_hot_encoder, scaler, model_path)

    return {"rmsle": compute_rmsle(y_test, model.predict(X_processed_test))}


def build_model(
        df: pd.DataFrame,
        cols_for_encode: Optional[list[str]] = ["HouseStyle", "BldgType"],
        cols_for_scale: Optional[list[str]] =
        ["LotArea", "YearBuilt", "BedroomAbvGr"],
        cols_no_transform: Optional[list[str]] = ["OverallCond"],
        label_col: Optional[str] = "SalePrice",
        model_path: Optional[str] = "../models"
) -> dict:
    """
    Build the model and return the Root Mean Squared Log Error,
    with optional arguments
    :return: dictionary with the Root Mean Squared Log Error
    """

    return _build_model(
        df,
        cols_for_encode,
        cols_for_scale,
        cols_no_transform,
        label_col,
        model_path
    )
