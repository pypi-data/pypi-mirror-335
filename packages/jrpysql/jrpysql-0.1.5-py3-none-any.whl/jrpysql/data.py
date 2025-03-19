"""Functions for loading external data"""
from seaborn import load_dataset
from shutil import copyfile
import jrpyintroduction as jrpy
import pandas as pd
import pkg_resources


def load_diamonds() -> pd.DataFrame:
    """Load the seaborn diamonds dataset

    return: pandas DataFrame with the diamonds data
    """
    return load_dataset("diamonds")


def load_movies() -> pd.DataFrame:
    """Load the jrpyintroduction movies dataset

    return: pandas DataFrame with the movies data
    """
    return jrpy.data.load("movies")


def populate_csv():
    """Generate example CSV file
    """
    abs_path = pkg_resources.resource_filename(__name__, "data/people.csv")
    copyfile(abs_path, "people.csv")
    print("\nCreated file people.csv in current directory.\n")
