from aiohttp import ClientSession
from webbrowser import open_new
from numpy import ndarray
from pandas import DataFrame, RangeIndex
from scipy.sparse import spmatrix
from gooder_ai.types import GetScoreColumnNamesParams, Data
import logging


def launch_browser(base_url: str, view_id: str):
    url = f"{base_url}{view_id}"
    open_new(url)


async def validate_config(validation_url: str, config: dict) -> dict:
    async with ClientSession() as session:
        output = None
        async with session.post(validation_url, json=config) as response:
            if response.status == 200:
                output = await response.json()
            else:
                error = await response.text()
                logging.error(f"Validation failed with {response.status}: {error}")
                raise Exception(f"Validation failed with {response.status}: {error}")
        return output


def get_dataset_column_names(dataset: ndarray, column_names: list[str]) -> list[str]:
    column_count = (
        len(dataset) if dataset.ndim == 1 else len(dataset[0])
    )  # ndim checks the dimensions of numpy array
    # If column names mismatch, log warning
    if len(column_names) != column_count:
        logging.warning(
            f"Mismatch: Dataset has {column_count} columns, but {len(column_names)} column names were provided."
        )

    # Ensure dataset_column_names has enough names, filling missing ones
    output = column_names[:column_count] + [
        f"column-{i+1}" for i in range(len(column_names), column_count)
    ]

    return output


# TODO: Verify if need to handle multi output classifiers.
def get_score_column_names(params: GetScoreColumnNamesParams) -> list[str]:
    column_names = params["column_names"]
    scores = params["scores"]
    model_name = params["model_name"]

    column_names_count = len(column_names)
    scores_count = len(scores)

    # Log warning if there's a mismatch
    if column_names_count != scores_count:
        logging.warning(
            f"Mismatch: Scores has {scores_count} possible values, but {column_names_count} column names were provided."
        )

    # Ensure output has enough names, filling missing ones
    output = [f"{model_name}-{name}" for name in column_names[:scores_count]] + [
        f"{model_name}-score-class-{column_name}"
        for column_name in scores[column_names_count:]
    ]

    return output


def get_scorer_functions(models_count: int, scorers: list[str]) -> list[str]:
    if models_count != len(scorers):
        logging.warning(
            f"Mismatch:  {models_count} Models, but {len(scorers)} scoring functions were provided."
        )

    output = (
        scorers[:models_count]
        + ["predict_proba" for _ in range(len(scorers), models_count)]
        if models_count != len(scorers)
        else scorers
    )

    return output


# Add column names to dataframe
def transform_dataframe(data: DataFrame, column_names: list[str]) -> DataFrame:
    transformed_dataframe = data.copy()

    # Get existing column names
    default_column_names = transformed_dataframe.columns
    column_count = transformed_dataframe.shape[1]
    final_column_names = []

    if len(column_names) != column_count:
        logging.warning(
            f"Mismatch: DataFrame has {column_count} columns, but {len(column_names)} column names were provided."
        )

    if len(column_names) == column_count:
        # Priority 1: Use provided column names
        final_column_names = column_names
    elif isinstance(default_column_names, RangeIndex) == False:
        # Priority 2: Use existing column names if not RangeIndex
        final_column_names = default_column_names
    else:
        # Priority 3: Generate default names if no names available
        final_column_names = column_names[:column_count] + [
            f"column-{i+1}" for i in range(len(column_names), column_count)
        ]

    # Assign final column names
    transformed_dataframe.columns = final_column_names

    return transformed_dataframe


def transform_unstructured_numpy_array(
    data: ndarray, column_names: list[str]
) -> DataFrame:
    logging.warning("Unstructured numpy array does not have any column name")
    numpy_array = data.copy()
    final_column_names = []

    if numpy_array.ndim == 1:
        if len(column_names) == 0:
            logging.warning(
                "Mismatch: Numpy array has 1 column, but 0 column names were provided."
            )
        final_column_names = (
            [column_names[0]] if len(column_names) > 0 else ["column-1"]
        )
    elif numpy_array.ndim == 2:
        _, column_count = data.shape
        if len(column_names) != column_count:
            logging.warning(
                f"Mismatch: Numpy array has {column_count} columns, but {len(column_names)} column names were provided."
            )
        final_column_names = column_names[:column_count] + [
            f"column-{i+1}" for i in range(len(column_names), column_count)
        ]
    else:
        raise ValueError("Input data must be a 1D or 2D NumPy array.")
    output = DataFrame(numpy_array, columns=final_column_names)
    return output


def transform_structured_numpy_array(
    data: ndarray, column_names: list[str]
) -> DataFrame:
    numpy_array = data.copy()
    final_column_names = []
    default_column_names = list(data.dtype.names)

    if numpy_array.ndim == 1:
        if len(column_names) == 1:
            final_column_names = [column_names[0]]
        else:
            logging.warning(
                "Mismatch: Numpy array has 1 column, but 0 column names were provided."
            )
            final_column_names = (
                [default_column_names[0]]
                if len(default_column_names) > 0
                else ["column-1"]
            )

    elif numpy_array.ndim == 2:
        _, column_count = data.shape
        if len(column_names) != column_count:
            logging.warning(
                f"Mismatch: Numpy array has {column_count} columns, but {len(column_names)} column names were provided."
            )
        if len(column_names) == column_count:
            final_column_names = column_names
        else:
            final_column_names = column_names[:column_count] + [
                f"column-{i+1}" for i in range(len(column_names), column_count)
            ]
    else:
        raise ValueError("Input data must be a 1D or 2D NumPy array.")
    output = DataFrame(numpy_array, columns=final_column_names)
    return output


def transform_list(
    data: (
        list[str]
        | list[int]
        | list[float]
        | list[list[str]]
        | list[list[int]]
        | list[list[float]]
    ),
    column_names: list[str],
) -> DataFrame:
    logging.warning("List does not have any column name.")
    data_list = data.copy()
    final_column_names = []

    # 1D list handling.
    if isinstance(data_list[0], (str, int, float)):
        data_list = [[value] for value in data_list]
        final_column_names = column_names[:1] if column_names else ["column-1"]

    elif isinstance(data_list[0], list):
        column_count = len(data_list[0])
        if len(column_names) != column_count:
            logging.warning(
                f"Mismatch: DataFrame has {column_count} columns, but {len(column_names)} column names were provided."
            )
        final_column_names = column_names[:column_count] + [
            f"column-{i+1}" for i in range(len(column_names), column_count)
        ]

    else:
        raise ValueError("Input data must be a 1D or 2D list.")

    # Create DataFrame
    output = DataFrame(data_list, columns=final_column_names)
    return output


def get_transformed_data(data: Data, column_names: list[str]) -> DataFrame:
    output = DataFrame()
    if isinstance(data, DataFrame):
        output = transform_dataframe(data, column_names)
    elif isinstance(data, ndarray) and data.dtype.names is None:
        output = transform_unstructured_numpy_array(data, column_names)
    elif isinstance(data, ndarray) and data.dtype.names is not None:
        transform_structured_numpy_array(data, column_names)
    elif isinstance(data, list):
        output = transform_list(data, column_names)
    elif isinstance(data, spmatrix):
        """
        scipy has multiple types of matrix all of them are extending spmatrix
        Ref: https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.spmatrix.html#spmatrix
        """
        numpy_array = data.toarray()
        output = transform_unstructured_numpy_array(numpy_array, column_names)

    if isinstance(output.columns, RangeIndex):
        raise ValueError("Invalid columns")
    return output
