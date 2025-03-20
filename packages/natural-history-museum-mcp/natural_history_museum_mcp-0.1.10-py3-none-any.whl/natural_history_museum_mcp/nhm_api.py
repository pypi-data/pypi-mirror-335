from pyportal.constants import resources, URLs
import requests


# Data contract
def data_object(records: list, msg: str | None, success: bool) -> dict:
    return {
        "records": records,
        "message": msg,
        "success": success,
        "record_count": len(records)
    }


def get_by_query(query: str, limit: int) -> dict:
    url = f"{URLs.base_url}/action/datastore_search?resource_id={resources.specimens}&q={query}&limit={limit}"

    response = requests.get(url)

    if response.status_code != 200:
        return data_object([], f"Request to natural history museum API failed with status code {response.status_code}", False)

    data = response.json()

    records = data["result"]["records"]

    if len(records) == 0:
        return data_object([], "Received OK from natural history museum API, but received no records", False)

    return data_object(records, None, True)
