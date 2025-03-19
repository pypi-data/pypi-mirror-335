"""
Functions to perform sampling
"""

import itertools
import warnings
import numpy as np
import cvxpy as cp


def set_rng(rng: np.random.Generator | None) -> np.random.Generator:
    """Sets the random number generator"""
    if rng is None:
        out = np.random.default_rng()
    else:
        out = rng
    return out


def srswor(n: int, N: int, rng: np.random.Generator = None) -> np.array:
    """
    Performs a simple random sampling without replacement
    according to Algorithm 4.5 Random sort procedure for SRSWOR
    from "Sampling algorithms" by Y. Tillé.
    An analogous result can be obtained by using np.random.choice,
    but getting the mask requires more code.

    :param n: int, the number of units in the sample
    :param N: int, the number of units in the population
    :param rng: np.random.Generator, a random number generator
    :return:
    """
    rng = set_rng(rng)
    w = rng.uniform(low=0, high=1, size=N)
    msk = (np.argsort(w) < n).astype(int)
    return msk


def srswr(n: int, N: int, rng: np.random.Generator = None) -> np.array:
    """
    Simple random sample with replacement
    :param n: int dimension of the sample
    :param N: int, dimension of the population
    :param rng: optional, np.random.Generator
    :return: np.array a mask with value 1 for the sampled units
    """
    rng = set_rng(rng)
    s = rng.choice(np.arange(N), size=n)
    out = np.array([np.count_nonzero(s == elem) for elem in np.arange(N)])
    return out


def systematic_sampling(n: int, N: int, rng: np.random.Generator = None) -> np.array:
    """
    Performs a systematic sampling
    :param n: the number of units in the sample
    :param N: the number of units in the population
    :param rng: optional, np.random.Generator
    :return: np.array a mask with value 1 for the sampled units
    """
    rng = set_rng(rng)
    arr = np.arange(N)
    k = N // n
    start = rng.choice(np.arange(k))
    v = arr[start::k][:n]
    msk = np.array([1 if elem in v else 0 for elem in arr])
    return msk


def cluster_sampling(
    n: int, clusters: np.array, rng: np.random.Generator = None
) -> np.array:
    """
    Randomly select n clusters from those listed in clusters
    :param n: number of clusters to be sampled
    :param clusters: array containing the cluster of each unit of the population
    :param rng: optional, np.random.Generator
    :return: np.array a mask with value 1 for the sampled units
    """
    rng = set_rng(rng)
    cluster_list = np.unique(clusters)
    sampled_clusters = rng.choice(np.unique(cluster_list), size=n, replace=False)
    return np.isin(clusters, sampled_clusters).astype(int)


def stratified_sampling(
    n: int,
    strata: np.array,
    method: str = "proportional",
    proba: np.array = None,
    rng: np.random.Generator = None,
):
    """
    Performs a stratified sampling
    :param n: total number of desired elements
    :param strata: Array or matrix containing the categorical
                variables to perform the stratification
    :param method: if "proportional" performs a proportional
                sampling, if "equal_size" performs an
                equal size stratification, if "custom" then the probabilities
                are assigned by the user with the "proba" parameter.
    :param proba: np.array|None optional array for the sampling probabilities.
                Only considered if "method" is "custom".
    :param rng: np.random.Generatior optional.
    :return: np.array
    """
    rng = set_rng(rng)
    cats, counts = np.unique(strata, axis=0, return_counts=True)
    cat_codes = [
        k * np.array([(elem == cat).all().astype(bool) for elem in strata]).astype(int)
        for k, cat in enumerate(cats)
    ]
    out = np.sum(cat_codes, axis=0)
    result = np.zeros(len(out))
    if method != "custom":
        proba = counts / np.sum(counts)
    ni = [0] * len(counts)
    if method not in ["proportional", "equal_size", "custom"]:
        raise ValueError(
            "Valid values for 'method' are 'proportional', 'equal_size' or 'custom'"
        )
    match method:
        case "proportional":
            ni = (proba * n).astype(int)
        case "equal_size":
            ni = np.array([n // len(counts)] * len(counts))
        case "custom":
            if proba is not None:
                ni = (proba * n).astype(int)
            else:
                raise ValueError("If method is set to custom, proba must be specified.")
    if not np.min(ni):
        warnings.warn(
            "At least one category has no elements. Consider choosing another sampling strategy."
        )

    for k, cnt in enumerate(ni):
        di = srswor(cnt, counts[k], rng=rng)
        result[out == k] = di
    return result


def _filter_integer(pi: np.array, X: np.array, eps: float = 1e-11) -> tuple:
    """
    Splits pi into non-integer values and integer (0 or 1) values
    and splits X accordingly.
    :param pi: numpy 1d array of probabilities with size n
    :param X: numpy 2d array of shape(n, p)
    :param eps: float defines the numerical approximation to define pi as integer
    :return: w0 (indices with pi integer) w1 (indices with pi non-integer),
    pi0 (pi components with pi integer), pi1 (pi components with pi non-integer)
    X0 (X rows for pi integer), X1 (X rows for pi non-integer)
    """
    # w1 = np.argwhere((pi > eps) & (pi < 1.0 - eps)).reshape(-1)
    # w0 = np.setdiff1d(np.arange(len(pi)), w1, assume_unique=True)
    # w1 = np.argwhere(pi*(1-pi)>eps).reshape(-1)
    w1 = np.where(pi * (1 - pi) > eps)[0]
    w0 = np.setdiff1d(np.arange(len(pi)), w1, assume_unique=True)
    pi0 = pi[w0]
    X0 = X[w0, :]
    pi1 = pi[w1]
    X1 = X[w1, :]

    return w0, w1, pi0, pi1, X0, X1


def _get_ker_vector(X: np.array, eps: float = 1e-6) -> tuple:
    """
    If possible, selects one vector from the null space of X.
    :param X: np.array of shape(n, p)
    :param eps: float, the numerical precision required to set an eigenvalue
        to 0 in the rank computation.
    :return: tuple of dimension 2. The second component is the status.
    If the status is 1, then the first component is a numpy array of size
        n belonging to the kernel of X,
    otherwise it's the zero vector of size n.
    """
    try:
        mat = X.copy().T
        _, s, vt = np.linalg.svd(mat, full_matrices=True)
        eig = vt[-1]
        rnk = np.sum(s > eps)
        n = mat.shape[1]  #
        if rnk < n:
            return eig, 1
        return np.zeros(len(eig)), 0
    except IndexError:
        return np.zeros(np.shape(X)[0]), 0


def _get_update_vector(
    pi1: np.array, vec: np.array, mask: np.array, rng: np.random.Generator = None
) -> np.array:
    """
    Randomly selects a vector psi = lam*vec
     such that the components of pi1[maks]+lam*vec are between 0 and 1
    and either the smaller component is 0 or the largest is 1.
    Uses the procedure defined by Tillé.
    :param pi1: starting vector
    :param vec: the update vector
    :param mask: mask for the non-integer elements of pi1
    :param rng: optional random number generator
    :return:
    """
    rng = set_rng(rng)
    denom = vec[mask]
    num = pi1[mask]
    vec_1 = (1.0 - num) / denom
    vec_2 = num / denom

    l1 = np.min(np.concatenate([vec_1[vec_1 > 0], -vec_2[-vec_2 > 0]]))
    l2 = -np.min(np.concatenate([-vec_1[-vec_1 > 0], vec_2[vec_2 > 0]]))

    q = l2 / (l1 + l2)
    s = rng.uniform()
    if s < q:
        lam = l1
    else:
        lam = l2

    return pi1 + lam * vec


def _flight_phase_step(
    pi: np.array, X: np.array, eps: float = 1e-11, rng: np.random.Generator = None
) -> tuple:
    """
    1. Filter non-integer components
    2. Get vector in kernel
    3. Update computing lam1 and lam2
    :param pi: np.array
    :param X: np.array
    :param eps: float
    :param rng: np.random.Generator
    :return: tuple
    """

    w0, w1, pi0, pi1, _, X1 = _filter_integer(pi, X, eps)

    vec, status = _get_ker_vector(X1, eps)
    if status:
        mask = vec != 0
        update = _get_update_vector(pi1, vec, mask, rng)
        pi1 = update
        out = np.zeros(len(pi))
        out[w0] = pi0
        out[w1] = pi1
    else:
        out = np.zeros(len(pi))
        out[w0] = pi0
        out[w1] = pi1

    return out, status


def _flight_phase_fast_step(pi, X, eps: float = 1e-11, rng=None):
    """
    Exactly as flight_phase, but only acts on the first p+1 components
    of pi and X at each step, where p is the number of columns of X.
     Whenever one of the reduced vectors is 0 or 1,
    it does the same with the first non-integer element

    :param pi:
    :param X:
    :param eps:
    :param rng:
    :return:
    """

    w0, w1, pi0, pi1, _, _ = _filter_integer(pi, X, eps)
    p = np.shape(X)[1]
    ind = w1[: p + 1]
    psi = pi1[: p + 1]
    A = X[ind]

    status = True
    while status:
        psi_old = psi
        psi, status = _flight_phase_step(psi_old, A, eps, rng)
    pi1[: p + 1] = psi
    out = np.zeros(len(pi))
    out[w0] = pi0
    out[w1] = pi1
    return out, status, 1


def _flight_phase(pi, X, eps: float = 1e-11, rng=None):
    z_old, status, cond = _flight_phase_fast_step(pi, X, eps, rng)
    ind = np.argwhere((z_old > eps) & (z_old < 1.0 - eps)).reshape(-1)
    z = z_old
    while cond:
        z, status, cond = _flight_phase_fast_step(z_old, X, eps, rng)
        ind_new = np.argwhere((z > eps) & (z < 1.0 - eps)).reshape(-1)
        if set(ind) == set(ind_new):
            cond = False
        else:
            z_old = z
            ind = ind_new
    return z, status


def _cube_flight(
    pi0: np.array,
    X0: np.array,
    eps: float = 1e-11,
    rng: np.random.Generator = None,
    order: str = None,
    landing: int = None,
    method: str = "best",
):

    rng = set_rng(rng)
    if landing is None:
        landing = len(pi0)
    ind = np.arange(len(pi0))
    rev_ind = ind
    match order:
        case "init":
            pass
        case "random":
            rng.shuffle(ind)
            rev_ind = np.argwhere([ind == elem for elem in np.arange(len(pi0))])[:, 1]
        case "absmean":
            ind = np.argsort(np.mean(np.abs(X0 - np.mean(X0, axis=0)).T * pi0, axis=0))[
                ::-1
            ]
            rev_ind = np.argwhere([ind == elem for elem in np.arange(len(pi0))])[:, 1]
    pi = pi0.copy()[ind]
    X = X0.copy()[ind]
    z = pi.copy()
    z, status = _flight_phase(z, X, eps, rng)
    z[z < eps] = 0
    z[z > 1 - eps] = 1
    ind_rem = np.argwhere((z > eps) & (z < 1.0 - eps)).reshape(-1)
    n_rem = len(ind_rem)
    p = 0
    out = None

    if landing <= 0:
        while p < n_rem:
            z, status = _flight_phase(z, X, eps, rng)
            z[z < eps] = 0
            z[z > 1 - eps] = 1
            ind_rem = np.argwhere((z > eps) & (z < 1.0 - eps)).reshape(-1)
            n_rem = len(ind_rem)
            p = len(z) - n_rem
    else:
        pi_rem = pi[ind_rem]
        X_rem = X[ind_rem]

        if method == "best":
            smpl = np.array(list(itertools.product((0, 1), repeat=len(ind_rem))))
            loss = np.array(
                [
                    np.mean(
                        (
                            ((X_rem.T @ elem - X_rem.T @ pi_rem) / (X_rem.T @ pi_rem))
                            ** 2
                        )
                    )
                    for elem in smpl
                ]
            )
            sel = np.argmin(loss)
            out = smpl[sel]
        elif method == "mc":
            smpl = rng.choice((0, 1), size=(landing, len(ind_rem)))
            loss = 1 / (
                1
                + np.array(
                    [
                        np.mean(
                            (
                                (
                                    (X_rem.T @ elem - X_rem.T @ pi_rem)
                                    / (X_rem.T @ pi_rem)
                                )
                                ** 2
                            )
                        )
                        for elem in smpl
                    ]
                )
            )
            loss /= np.sum(loss)
            np.nan_to_num(loss, nan=0.0, copy=False)
            ind = np.arange(len(loss))
            sel = rng.choice(ind, p=loss)
            out = smpl[sel]
        elif method == "linear":
            x = cp.Variable(len(pi_rem), boolean=True)
            b = X_rem.T @ pi_rem
            loss = cp.sum_squares(X_rem.T @ x - b)
            objective = cp.Minimize(loss)
            prob = cp.Problem(objective, [])
            prob.solve()
            out = x.value

        z[ind_rem] = out
    return z[rev_ind], status


def cube_sample(
    pi0: np.array,
    X0: np.array,
    eps: float = 1e-11,
    rng: np.random.Generator = None,
    order: str = "random",
    landing: int = 1,
    n_rep: int = None,
    method: str = "linear",
) -> np.array:
    """
    High level function to perform the cube sampling, taken from Tillé.
    :param pi0:
    :param X0:
    :param eps:
    :param rng:
    :param order:
    :param landing:
    :param n_rep:
    :param method:
    :return:
    """
    if n_rep is None:
        n_rep = len(pi0)
    out = np.array(
        [
            _cube_flight(pi0, X0, eps, rng, order, landing, method)[0]
            for _ in range(n_rep)
        ]
    )
    if method in ["best", "linear"]:
        loss = np.array(
            [
                np.mean((((X0.T @ elem - X0.T @ pi0) / (X0.T @ pi0)) ** 2))
                for elem in out
            ]
        )
        return out[np.argmin(loss)]
    if method == "mc":
        loss = 1.0 / (
            1.0
            + np.array(
                [
                    np.mean((((X0.T @ elem - X0.T @ pi0) / (X0.T @ pi0)) ** 2))
                    for elem in out
                ]
            )
        )
        loss /= np.sum(loss)
        np.nan_to_num(loss, nan=0.0, copy=False)
        ind = np.arange(len(loss))
        sel = rng.choice(ind, p=loss)
        return out[sel]
    raise ValueError(
        '''Value not legal for "method" parameter.
     Allowed values are "mc", "linear" or "best"'''
    )
