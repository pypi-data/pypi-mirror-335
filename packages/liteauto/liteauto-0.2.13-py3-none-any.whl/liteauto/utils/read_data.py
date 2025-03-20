from typing import Optional, Union, Any, Dict
from pathlib import Path
import pandas as pd
import json


def handle_json(path: Path, encoding: str, **kwargs: Any) -> dict:
    """Handle JSON file reading"""
    if path is None or not isinstance(path, Path):
        raise ValueError("Path must be a valid Path object")
    if encoding is None or not isinstance(encoding, str):
        raise ValueError("Encoding must be a string")

    with open(path, 'r', encoding=encoding) as file:
        return json.load(file)


def handle_text(path: Path, encoding: str, **kwargs: Any) -> str:
    """Handle text file reading"""
    if path is None or not isinstance(path, Path):
        raise ValueError("Path must be a valid Path object")
    if encoding is None or not isinstance(encoding, str):
        raise ValueError("Encoding must be a string")

    with open(path, 'r', encoding=encoding) as file:
        return file.read()


def handle_csv(
    path: Path,
    encoding: str,
    delimiter: str,
    skiprows: Optional[int],
    header: Optional[int],
    names: Optional[list[str]],
    **kwargs: Any
) -> pd.DataFrame:
    """Handle CSV file reading"""
    if path is None or not isinstance(path, Path):
        raise ValueError("Path must be a valid Path object")
    if encoding is None or not isinstance(encoding, str):
        raise ValueError("Encoding must be a string")
    if delimiter is None or not isinstance(delimiter, str):
        raise ValueError("Delimiter must be a string")

    return pd.read_csv(
        path,
        encoding=encoding,
        delimiter=delimiter,
        skiprows=skiprows,
        header=header,
        names=names,
        **kwargs
    )


def handle_excel(path: Path, sheet_name: Optional[str], skiprows: Optional[int], header: Optional[int],
                 names: Optional[list[str]], **kwargs: Any) -> pd.DataFrame:
    """Handle Excel file reading"""
    if path is None or not isinstance(path, Path):
        raise ValueError("Path must be a valid Path object")
    if sheet_name is None or not isinstance(sheet_name, (str, int)):
        raise ValueError("Sheet name must be a string or an integer")

    return pd.read_excel(
        path,
        sheet_name=sheet_name,
        skiprows=skiprows,
        header=header,
        names=names,
        **kwargs
    )


def handle_parquet(path: Path, **kwargs: Any) -> pd.DataFrame:
    """Handle Parquet file reading"""
    if path is None or not isinstance(path, Path):
        raise ValueError("Path must be a valid Path object")

    return pd.read_parquet(path, **kwargs)


def read_data(
    path: Union[str, Path],
    encoding: str = 'utf-8',
    delimiter: str = ',',
    sheet_name: Optional[Union[str, int]] = None,
    skiprows: Optional[int] = None,
    header: Optional[int] = None,
    names: Optional[list[str]] = None,
    **kwargs: Any
) -> pd.DataFrame | dict:
    """Read data from a file in the appropriate format"""
    if encoding is None or not isinstance(encoding, str):
        raise ValueError("Encoding must be a string")

    path = Path(path) if not isinstance(path, Path) else path
    if not path.exists():
        raise FileNotFoundError(f"The file {path} does not exist")

    if path.suffix == '.json':
        return handle_json(path, encoding, **kwargs)
    elif path.suffix == '.txt':
        return handle_text(path, encoding, **kwargs)
    elif path.suffix == '.csv':
        return handle_csv(path, encoding, delimiter, skiprows, header, names, **kwargs)
    elif path.suffix == '.xlsx':
        return handle_excel(path, sheet_name, skiprows, header, names, **kwargs)
    elif path.suffix == '.parquet':
        return handle_parquet(path, **kwargs)
    else:
        raise ValueError(
            f"Unsupported file format: {path.suffix}. Supported formats: .json, .txt, .csv, .xlsx, .parquet")
