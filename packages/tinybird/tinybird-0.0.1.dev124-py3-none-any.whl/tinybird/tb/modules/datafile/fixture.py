from pathlib import Path
from typing import Any, Dict, List, Union

from tinybird.tb.modules.common import format_data_to_ndjson


def get_fixture_dir(folder: str) -> Path:
    fixture_dir = Path(folder) / "fixtures"
    fixture_dir.mkdir(exist_ok=True)
    return fixture_dir


def persist_fixture_sql(fixture_name: str, sql: str, folder: str) -> Path:
    fixture_dir = get_fixture_dir(folder)
    fixture_file = fixture_dir / f"{fixture_name}.sql"
    fixture_file.write_text(sql)
    return fixture_file


def persist_fixture(fixture_name: str, data: Union[List[Dict[str, Any]], str], folder: str, format="ndjson") -> Path:
    fixture_dir = get_fixture_dir(folder)
    fixture_file = fixture_dir / f"{fixture_name}.{format}"
    fixture_file.write_text(data if isinstance(data, str) else format_data_to_ndjson(data))
    return fixture_file


def load_fixture(
    fixture_name: str,
    folder: str,
    format="ndjson",
) -> Union[Path, None]:
    fixture_dir = get_fixture_dir(folder)
    fixture_file = fixture_dir / f"{fixture_name}.{format}"
    if not fixture_file.exists():
        return None
    return fixture_file
