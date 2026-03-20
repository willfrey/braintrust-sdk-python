from typing import Any, cast

from braintrust import init_dataset
from braintrust._generated_types import RunEvalData, RunEvalData1, RunEvalData2
from braintrust.logger import BraintrustState


async def get_dataset_by_id(state: BraintrustState, dataset_id: str) -> dict[str, str]:
    """Fetch dataset information by ID."""
    # Make API call to get dataset info
    conn = state.api_conn()
    # Note: The Python SDK doesn't have async API calls yet, so we use sync
    response = conn.get_json(f"v1/dataset/{dataset_id}")

    if response is None:
        raise ValueError(f"Dataset with id {dataset_id} not found")

    # Extract project_id and dataset name from response
    return {
        "project_id": response.get("project_id"),
        "dataset": response.get("name"),
    }


# NOTE: To make this performant, we'll have to make these functions work with async i/o
async def get_dataset(state: BraintrustState, data: RunEvalData | RunEvalData1 | RunEvalData2 | dict[str, Any]) -> Any:
    """
    Get dataset from various data sources.

    Handles:
    - Dataset reference by project_name/dataset_name
    - Dataset reference by dataset_id
    - Inline data array
    """
    # Handle dict-based data (common case)
    if isinstance(data, dict):
        data_dict = cast(dict[str, Any], data)
        if "project_name" in data_dict and "dataset_name" in data_dict:
            # Dataset reference by name
            return init_dataset(
                state=state,
                project=data_dict["project_name"],
                name=data_dict["dataset_name"],
                # _internal_btql is optional
                **({"_internal_btql": data_dict["_internal_btql"]} if "_internal_btql" in data_dict else {}),
            )
        elif "dataset_id" in data_dict:
            # Dataset reference by ID
            dataset_info = await get_dataset_by_id(state, data_dict["dataset_id"])
            return init_dataset(
                state=state,
                project_id=dataset_info["project_id"],
                name=dataset_info["dataset"],
                # _internal_btql is optional
                **({"_internal_btql": data_dict["_internal_btql"]} if "_internal_btql" in data_dict else {}),
            )
        elif "data" in data_dict:
            # Inline data
            return data_dict["data"]

    # If it's not a dict, assume it's inline data
    return data
