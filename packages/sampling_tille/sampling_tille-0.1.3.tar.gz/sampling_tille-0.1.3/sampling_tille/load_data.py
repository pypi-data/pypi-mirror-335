"""
Utilities to load data
"""

import os
import importlib.resources
import pandas as pd
import geopandas as gpd

SAMPLING_PROJECT_NAME = "sampling_tille"
DATA_DIR = "data"

base_path = importlib.resources.files(SAMPLING_PROJECT_NAME)

FILE_NAMES = {
    "fertility": "aer_fertility.csv",
    "Switzerland": "swissmunicipalities.csv",
    "Belgium": "belgianmunicipalities.csv",
    "MissingFile": "missingfile.csv",  # For testing purposes only, does not exist
}

GEOFILE_NAMES = {"Italy": "Com01012025_g_WGS84.dbf"}


def load_data(file_name: str) -> pd.DataFrame:
    """
    loads one of the datasets present in the library.
    :param file_name: str the name of one of the files.
    Allowed vaues are fertility, loan, Switzerland or Belgium
    :return: pd.DataFrame The corresponding dataframe

    :raise:
    ValueError if file_name is not in the list of allowed names.
    FileNotFoundError if the file does not exist.

    >>> from sampling_tille.load_data import load_data
    >>> df = load_data('fertility')
    >>> df.head()
       rownames morekids gender1 gender2  age afam hispanic other  work
    0         1       no    male  female   27   no       no    no     0
    1         2       no  female    male   30   no       no    no    30
    2         3       no    male  female   27   no       no    no     0
    3         4       no    male  female   35  yes       no    no     0
    4         5       no  female  female   30   no       no    no    22
    """
    if file_name in FILE_NAMES:
        name = FILE_NAMES[file_name]
        path = os.path.join(base_path, DATA_DIR, name)
        if os.path.isfile(path):
            df = pd.read_csv(path)
            return df
        raise FileNotFoundError(f"There is no file at {path}")
    if file_name in GEOFILE_NAMES:
        name = GEOFILE_NAMES[file_name]
        path = os.path.join(base_path, DATA_DIR, name)
        if os.path.isfile(path):
            gdf = gpd.read_file(path)
            return gdf
        raise FileNotFoundError(f"There is no file at {path}")
    raise ValueError(
        f"""{file_name} not present in data.
Allowed values are {','.join(list(FILE_NAMES)[:-1])} or {','.join(list(GEOFILE_NAMES)[:-1])}"""
    )
