from typing import Any

from .generated_types import DatasetEvent


DEFAULT_IS_LEGACY_DATASET = False


def ensure_dataset_record(r: DatasetEvent, legacy: bool) -> dict[str, Any]:
    if legacy:
        return ensure_legacy_dataset_record(r)
    else:
        return ensure_new_dataset_record(r)


def ensure_legacy_dataset_record(r: DatasetEvent) -> dict[str, Any]:
    if "output" in r:
        return {**r}
    row: dict[str, Any] = {**r}
    row["output"] = row.pop("expected")
    return row


def ensure_new_dataset_record(r: DatasetEvent) -> dict[str, Any]:
    if "expected" in r:
        return {**r}
    row: dict[str, Any] = {**r}
    row["expected"] = row.pop("output")
    return row
