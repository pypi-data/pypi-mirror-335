import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def get_encoder(
        X_train: pd.DataFrame,
        columns_for_encoding: list[str]
) -> OneHotEncoder:
    """
    Fit OneHotEncoder on the training data
    :param X_train: pandas DataFrame
    :param columns_for_encoding: list of columns to encode
    :return: sklearn OneHotEncoder object
    """
    one_hot_encoder = OneHotEncoder()
    one_hot_encoder.fit(X_train[columns_for_encoding])

    return one_hot_encoder


def encode_category_features(
        df_to_encode: pd.DataFrame,
        one_hot_encoder: OneHotEncoder,
        columns_for_encoding: list[str]
) -> pd.DataFrame:
    """
    Encode categorical features using OneHotEncoder
    :param df_to_encode: pandas DataFrame
    :param one_hot_encoder: sklearn OneHotEncoder object
    :param columns_for_encoding: list of columns to encode
    :return: pandas DataFrame with encoded features
    """
    encoded_data = one_hot_encoder.transform(
        df_to_encode[columns_for_encoding]
    )
    encoded_columns = one_hot_encoder.get_feature_names_out()

    return pd.DataFrame(
        encoded_data.toarray(),
        columns=encoded_columns
    )


def get_scaler(
        X_train: pd.DataFrame,
        columns_for_scaling: list[str]
) -> StandardScaler:
    """
    Fit StandardScaler on the training data
    :param X_train: pandas DataFrame
    :param columns_for_scaling: list of columns to scale
    :return: sklearn StandardScaler object
    """
    scaler = StandardScaler()
    scaler.fit(X_train[columns_for_scaling])

    return scaler


def scale_continuous_features(
        df_to_scale: pd.DataFrame,
        scaler: StandardScaler,
        columns_for_scaling: list[str]
) -> pd.DataFrame:
    """
    Scale continuous features using StandardScaler
    :param df_to_scale: pandas DataFrame
    :param scaler: sklearn StandardScaler object
    :param columns_for_scaling: list of columns to scale
    :return: pandas DataFrame with scaled features
    """
    scaled_data = scaler.transform(df_to_scale[columns_for_scaling])

    return pd.DataFrame(scaled_data, columns=columns_for_scaling)


def concate_processed_features(
        encoded_df: pd.DataFrame,
        scaled_df: pd.DataFrame,
        df: pd.DataFrame,
        non_processed_columns: list[str]
) -> pd.DataFrame:
    """
    Concatenate encoded, scaled, and non-processed features
    :param encoded_df: pandas DataFrame with encoded features
    :param scaled_df: pandas DataFrame with scaled features
    :param df: pandas DataFrame with non-processed features
    :param non_processed_columns: list of columns that should not be processed
    :return: pandas DataFrame with all features
    """
    processed_df = pd.concat([encoded_df, scaled_df], axis=1)
    for col in non_processed_columns:
        processed_df[col] = df[col].values

    return processed_df


def process_data(
        df: pd.DataFrame,
        one_hot_encoder: OneHotEncoder,
        scaler: StandardScaler,
        cols_for_encode: list[str],
        cols_for_scale: list[str],
        cols_no_transform: list[str]
) -> pd.DataFrame:
    """
    Process data by encoding categorical features,
    scaling continuous features,
    and concatenating all features
    :param df: pandas DataFrame
    :param one_hot_encoder: sklearn OneHotEncoder object
    :param scaler: sklearn StandardScaler object
    :param cols_for_encode: list of columns to encode
    :param cols_for_scale: list of columns to scale
    :param cols_no_transform: list of columns that should not be processed
    :return: pandas DataFrame with all processed,
    and features that should not be processed
    """
    encoded_df = encode_category_features(df, one_hot_encoder, cols_for_encode)
    scaled_df = scale_continuous_features(df, scaler, cols_for_scale)
    X_processed_df = concate_processed_features(
        encoded_df,
        scaled_df,
        df,
        cols_no_transform
    )

    return X_processed_df
