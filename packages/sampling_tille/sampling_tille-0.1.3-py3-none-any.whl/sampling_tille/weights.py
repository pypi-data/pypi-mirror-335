"""
Routines to compute stratification weights.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression


def get_weights(mask: np.array) -> np.array:
    """
    Computes the design weights for a simple random sampling design
    :param mask: np.array the mask obtained from the sample
    :return: np.array the weights for each population unit
    """
    out = mask.astype(float)
    out *= len(mask) / np.sum(mask)
    return out


def get_stratified_weights(
    df: pd.DataFrame, mask: np.array, columns: list[str]
) -> np.array:
    """
    Computes the design weights for a stratified random sampling design
    :param df: pd.DadaFrame the population dataframe
    :param mask: np.array the mask obtained from the sample
    :param columns: list[str] the list containing the columns
            to perform the stratification
    :return: np.array the weights for each population unit
    """
    out = mask.astype(float)
    for _, col in df[columns].drop_duplicates().iterrows():
        cond = True
        cond_strat = True
        for col_name in columns:
            cond &= df[col_name] == col[col_name]
            cond_strat &= df[mask][col_name] == col[col_name]
        df_red = df[cond]
        df_strat_red = df[mask][cond_strat]
        val = (
            df_red.groupby(columns).count().values[0][0]
            / df_strat_red.groupby(columns).count().values[0][0]
        )
        out[cond] *= val
    return out


def get_cluster_weights(mask: np.array) -> np.array:
    """
    The weights for a cluster sampling.
    :param mask: np.array the mask obtained from the sampling procedure
    :return:
            np.array a numpy array containing the weights
    """
    # Each cluster has the same probability of being selected, regardless on the composition
    # So we can assign to each unit the same probability.
    # As usual, we finally normalize to the total number of elements in the population
    return mask / np.sum(mask) * len(mask)


def get_propensity_weight(
    df: pd.DataFrame, mask: np.array, cols: list[str], responded: str
) -> np.array:
    """
    We compute the non-responding probability based on a propensity
    score matching using a logistic regression
    :param df: pd.DataFrame the population dataframe.
    :param mask: np.array the mask obtained from the sampling procedure
    :param cols: list[str] the list of columns which will be used as covariates
            in the logistic regressor
    :param responded:
            the column which indicates which sample unit responded and which didn't
    :return:
            np.array a numpy array containing the weights
    """

    df_sampled = df[mask]
    out = np.zeros(len(df))
    X = pd.get_dummies(df_sampled[cols], drop_first=True)
    y = df_sampled[responded].astype(int)
    lr = LogisticRegression()
    lr.fit(X, y)
    Xr = X[df_sampled[responded].astype(bool)]
    p = lr.predict_proba(Xr)
    out[(df[responded].astype(int) * mask.astype(int)).astype(bool)] = 1.0 / p.T[1]
    return out
