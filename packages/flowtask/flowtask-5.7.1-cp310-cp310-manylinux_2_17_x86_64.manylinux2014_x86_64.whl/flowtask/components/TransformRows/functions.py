"""
Functions.

Tree of TransformRows functions.

"""
from typing import List, Optional
import requests
import numpy as np
import pandas
from ...conf import BARCODELOOKUP_API_KEY
from ...utils.executor import getFunction


def apply_function(
    df: pandas.DataFrame,
    field: str,
    fname: str,
    column: Optional[str] = None,
    **kwargs
) -> pandas.DataFrame:
    """
    Apply any scalar function to a column in the DataFrame.

    Parameters:
    - df: pandas DataFrame
    - field: The column where the result will be stored.
    - fname: The name of the function to apply.
    - column: The column to which the function is applied (if None, apply to `field` column).
    - **kwargs: Additional arguments to pass to the function.
    """

    # Retrieve the scalar function using getFunc
    try:
        func = getFunction(fname)
    except Exception:
        raise

    # If a different column is specified, apply the function to it,
    # but save result in `field`
    try:
        if column is not None:
            df[field] = df[column].apply(lambda x: func(x, **kwargs))
        else:
            if field not in df.columns:
                # column doesn't exist
                df[field] = None
            # Apply the function to the field itself
            df[field] = df[field].apply(lambda x: func(x, **kwargs))
    except Exception as err:
        print(
            f"Error in apply_function for field {field}:", err
        )
    return df


def get_product(row, field, columns):
    """
    Retrieves product information from the Barcode Lookup API based on a barcode.

    :param row: The DataFrame row containing the barcode.
    :param field: The name of the field containing the barcode.
    :param columns: The list of columns to extract from the API response.
    :return: The DataFrame row with the product information.
    """

    barcode = row[field]
    url = f'https://api.barcodelookup.com/v3/products?barcode={barcode}&key={BARCODELOOKUP_API_KEY}'
    response = requests.get(url)
    result = response.json()['products'][0]
    for col in columns:
        try:
            row[col] = result[col]
        except KeyError:
            row[col] = None
    return row


def upc_to_product(
    df: pandas.DataFrame,
    field: str,
    columns: list = ['barcode_formats', 'mpn', 'asin', 'title', 'category', 'model', 'brand']
) -> pandas.DataFrame:
    """
    Converts UPC codes in a DataFrame to product information using the Barcode Lookup API.

    :param df: The DataFrame containing the UPC codes.
    :param field: The name of the field containing the UPC codes.
    :param columns: The list of columns to extract from the API response.
    :return: The DataFrame with the product information.
    """
    try:
        df = df.apply(lambda x: get_product(x, field, columns), axis=1)
        return df
    except Exception as err:
        print(f"Error on upc_to_product {field}:", err)
        return df

def day_of_week(
    df: pandas.DataFrame,
    field: str,
    column: str,
    locale: str = 'en_US.utf8'
) -> pandas.DataFrame:
    """
    Extracts the day of the week from a date column.

    :param df: The DataFrame containing the date column.
    :param field: The name of the field to store the day of the week.
    :param column: The name of the date column.
    :return: The DataFrame with the day of the week.
    """
    try:
        df[field] = df[column].dt.day_name(locale=locale)
        return df
    except Exception as err:
        print(f"Error on day_of_week {field}:", err)
        return df

def duration(
    df: pandas.DataFrame,
    field: str,
    columns: List[str],
    unit: str = 's'
) -> pandas.DataFrame:
    """
    Converts a duration column to a specified unit.

    :param df: The DataFrame containing the duration column.
    :param field: The name of the field to store the converted duration.
    :param column: The name of the duration column.
    :param unit: The unit to convert the duration to.
    :return: The DataFrame with the converted duration.
    """
    try:
        if unit == 's':
            _unit = 1.0
        if unit == 'm':
            _unit = 60.0
        elif unit == 'h':
            _unit = 3600.0
        elif unit == 'd':
            _unit = 86400.0
        # Calculate duration in minutes as float
        df[field] = (
            (df[columns[1]] - df[columns[0]]).dt.total_seconds() / _unit
        )
        return df
    except Exception as err:
        print(f"Error on duration {field}:", err)
        return df


def get_moment(
    df: pandas.DataFrame,
    field: str,
    column: str,
    moments: List[tuple] = None,
) -> pandas.DataFrame:
    """
    df: pandas DataFrame
    column: name of the column to compare (e.g. "updated_hour")
    ranges: list of tuples [(label, (start, end)), ...]
            e.g. [("night",(0,7)), ("morning",(7,10)), ...]
    returns: a Series of labels corresponding to each row
    """
    if not moments:
        moments = [
            ("night", (0, 7)),   # >= 0 and < 7
            ("morning", (7, 10)),  # >= 7 and < 10
            ("afternoon", (10, 16)),  # >= 10 and < 16
            ("evening", (16, 20)),  # >= 16 and < 20
            ("night", (20, 24)),  # >= 20 and < 24 (or use float("inf") for open-ended)
        ]
    conditions = [
        (df[column] >= start) & (df[column] < end)
        for _, (start, end) in moments
    ]
    df[field] = np.select(conditions, [label for label, _ in moments], default=None)
    return df


def fully_geoloc(
    df: pandas.DataFrame,
    field: str,
    columns: List[tuple],
    inverse: bool = False
) -> pandas.DataFrame:
    """
    Adds a boolean column (named `field`) to `df` that is True when,
    for each tuple in `columns`, all the involved columns are neither NaN nor empty.

    Parameters:
        df (pd.DataFrame): The DataFrame.
        field (str): The name of the output column.
        columns (list of tuple of str): List of tuples, where each tuple
            contains column names that must be valid (non-null and non-empty).
            Example: [("start_lat", "start_long"), ("end_lat", "end_log")]

    Returns:
        pd.DataFrame: The original DataFrame with the new `field` column.
    """
    # Start with an initial mask that's True for all rows.
    mask = pandas.Series(True, index=df.index)

    # Loop over each tuple of columns, then each column in the tuple.
    for col_group in columns:
        for col in col_group:
            if inverse:
                mask &= df[col].isna() | (df[col] == "")
            else:
                mask &= df[col].notna() & (df[col] != "")

    df[field] = mask
    return df


def any_tuple_valid(
    df: pandas.DataFrame,
    field: str,
    columns: List[tuple]
) -> pandas.DataFrame:
    """
    Adds a boolean column (named `field`) to `df` that is True when
    any tuple in `columns` has all of its columns neither NaN nor empty.

    Parameters:
        df (pd.DataFrame): The DataFrame.
        field (str): The name of the output column.
        columns (list of tuple of str): List of tuples, where each tuple
            contains column names that must be checked.
            Example: [("start_lat", "start_long"), ("end_lat", "end_log")]

    Returns:
        pd.DataFrame: The original DataFrame with the new `field` column.
    """
    # Start with an initial mask that's False for all rows
    result = pandas.Series(False, index=df.index)

    # Loop over each tuple of columns
    for col_group in columns:
        # For each group, assume all columns are valid initially
        group_all_valid = pandas.Series(True, index=df.index)

        # Check that all columns in this group are non-null and non-empty
        for col in col_group:
            group_all_valid &= df[col].notna() & (df[col] != "")

        # If all columns in this group are valid, update the result
        result |= group_all_valid

    df[field] = result
    return df
