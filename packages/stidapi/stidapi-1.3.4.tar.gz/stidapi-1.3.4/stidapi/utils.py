import json
import logging
import requests
from types import SimpleNamespace
from msal_bearer import BearerAuth, get_user_name


logger = logging.getLogger(__name__)


def get_api_url():
    return "https://stidapi.equinor.com/"


def get_auth():
    tenantID = "3aa4a235-b6e2-48d5-9195-7fcf05b459b0"
    clientID = "1a35a8df-b48d-40df-987b-267968b1b198"  # stidapi-python
    scopes = ["1734406c-3449-4192-a50d-7c3a63d3f57d/user_impersonation"]
    auth = BearerAuth.get_auth(
        tenantID=tenantID,
        clientID=clientID,
        scopes=scopes,
        username=f"{get_user_name()}@equinor.com",
    )

    return auth


def get_object_from_json(text: str):
    if isinstance(text, list):
        obj = [json.loads(x, object_hook=lambda d: SimpleNamespace(**d)) for x in text]
    else:
        obj = json.loads(text, object_hook=lambda d: SimpleNamespace(**d))
    return obj


def get_json(url: str, raise_for_status=False):
    response = requests.get(url, auth=get_auth())

    if raise_for_status:
        response.raise_for_status()

    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            logger.warning(
                f"Warning: {str(url)} returned successfully, but not with a valid json response"
            )
    else:
        logger.warning(
            f"Warning: {str(url)} returned status code {response.status_code}"
        )

    return []
