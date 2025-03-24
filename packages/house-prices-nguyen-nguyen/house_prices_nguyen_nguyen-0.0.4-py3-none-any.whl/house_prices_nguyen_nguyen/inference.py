from typing import Optional

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from house_prices.src.house_prices_nguyen_nguyen.preprocess import process_data


def load_model(path: str) -> (xgb.XGBRegressor, OneHotEncoder, StandardScaler):
    """
    Load the model, encoder, and scaler
    :param path: path to the model
    :return: xgboost model, sklearn OneHotEncoder, sklearn StandardScaler
    """
    model = joblib.load(f"{path}/model.joblib")
    encoder = joblib.load(f"{path}/encoder.joblib")
    scaler = joblib.load(f"{path}/scaler.joblib")

    return model, encoder, scaler


def _make_predictions(
        df: pd.DataFrame,
        cols_for_encode: list[str],
        cols_for_scale: list[str],
        cols_no_transform: list[str],
        model_path: str
) -> np.ndarray:
    """
    Make prediction
    :param df: pandas DataFrame
    :param cols_for_encode: list of columns to encode
    :param cols_for_scale: list of columns to scale
    :param cols_no_transform: list of columns that should not be processed
    :param model_path: path to the model
    :return: The prediction
    """
    (model, one_hot_encoder, scaler) = load_model(model_path)
    X_processed = process_data(
        df[cols_for_encode + cols_for_scale + cols_no_transform],
        one_hot_encoder,
        scaler,
        cols_for_encode,
        cols_for_scale,
        cols_no_transform
    )

    return model.predict(X_processed)


def make_predictions(
        df: pd.DataFrame,
        cols_for_encode: Optional[list[str]] = ["HouseStyle", "BldgType"],
        cols_for_scale: Optional[list[str]] =
        ["LotArea", "YearBuilt", "BedroomAbvGr"],
        cols_no_transform: Optional[list[str]] = ["OverallCond"],
        model_path: Optional[str] = "../models"
) -> pd.DataFrame:
    """
    Run make prediction
    :return: pandas DataFrame with predicted sale price
    """
    y_pred = _make_predictions(df, cols_for_encode, cols_for_scale,
                               cols_no_transform, model_path)
    y_inference_pred_df = pd.DataFrame(y_pred, columns=["PredictedSalePrice"])
    df_inference = df[cols_for_encode + cols_for_scale + cols_no_transform]

    return pd.concat([df_inference.reset_index(drop=True),
                      y_inference_pred_df], axis=1)
