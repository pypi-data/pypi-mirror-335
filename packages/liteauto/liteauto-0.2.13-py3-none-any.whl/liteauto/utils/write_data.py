from typing import Optional, Union, Any, Dict
from pathlib import Path
import pandas as pd
import json


def handle_json(path: Path, data: dict, encoding: str = 'utf-8', **kwargs: Any) -> None:
    """Handle JSON file writing"""
    if path is None or not isinstance(path, Path):
        raise ValueError("Path must be a valid Path object")
    if data is None or not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")
    if encoding is None or not isinstance(encoding, str):
        raise ValueError("Encoding must be a string")

    with open(path, 'w', encoding=encoding) as file:
        json.dump(data, file, **kwargs)


def handle_text(path: Path, data: str, encoding: str = 'utf-8', **kwargs: Any) -> None:
    """Handle text file writing"""
    if path is None or not isinstance(path, Path):
        raise ValueError("Path must be a valid Path object")
    if data is None or not isinstance(data, str):
        raise ValueError("Data must be a string")
    if encoding is None or not isinstance(encoding, str):
        raise ValueError("Encoding must be a string")

    with open(path, 'w', encoding=encoding) as file:
        file.write(data)


def handle_csv(
    path: Path,
    data: pd.DataFrame,
    encoding: str = 'utf-8',
    delimiter: str = ',',
    **kwargs: Any
) -> None:
    """Handle CSV file writing"""
    if path is None or not isinstance(path, Path):
        raise ValueError("Path must be a valid Path object")
    if data is None or not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be a pandas DataFrame")
    if encoding is None or not isinstance(encoding, str):
        raise ValueError("Encoding must be a string")
    if delimiter is None or not isinstance(delimiter, str):
        raise ValueError("Delimiter must be a string")

    data.to_csv(path, sep=delimiter, encoding=encoding, **kwargs)


def handle_excel(
    path: Path,
    data: pd.DataFrame,
    sheet_name: Optional[str] = 'Sheet1',
    engine: Optional[str] = None,
    **kwargs: Any
) -> None:
    """Handle Excel file writing"""
    if path is None or not isinstance(path, Path):
        raise ValueError("Path must be a valid Path object")
    if data is None or not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be a pandas DataFrame")
    if sheet_name is None or not isinstance(sheet_name, str):
        raise ValueError("Sheet name must be a string")

    with pd.ExcelWriter(path, engine=engine) as writer:
        data.to_excel(writer, sheet_name=sheet_name, **kwargs)


def handle_parquet(
    path: Path,
    data: pd.DataFrame,
    compression: Optional[str] = 'snappy',
    **kwargs: Any
) -> None:
    """Handle Parquet file writing"""
    if path is None or not isinstance(path, Path):
        raise ValueError("Path must be a valid Path object")
    if data is None or not isinstance(data, pd.DataFrame):
        raise ValueError("Data must be a pandas DataFrame")

    data.to_parquet(path, compression=compression, **kwargs)


def write_data(
    path: Union[str, Path],
    data: Any,
    encoding: str = 'utf-8',
    delimiter: str = ',',
    sheet_name: Optional[Union[str, int]] = None,
    engine: Optional[str] = None,
    compression: Optional[str] = 'snappy',
    **kwargs: Any
) -> None:
    """Write data to a file in the appropriate format"""
    if path is None or not isinstance(path, Path):
        raise ValueError("Path must be a valid Path object")
    if encoding is None or not isinstance(encoding, str):
        raise ValueError("Encoding must be a string")

    path = Path(path)
    if path.suffix == '.json':
        handle_json(path, data, encoding, **kwargs)
    elif path.suffix == '.txt':
        handle_text(path, data, encoding, **kwargs)
    elif path.suffix == '.csv':
        handle_csv(path, data, encoding, delimiter, **kwargs)
    elif path.suffix == '.xlsx':
        handle_excel(path, data, sheet_name, engine, **kwargs)
    elif path.suffix == '.parquet':
        handle_parquet(path, data, compression, **kwargs)
    else:
        raise ValueError(
            f"Unsupported file format: {path.suffix}. Supported formats: .json, .txt, .csv, .xlsx, .parquet")
