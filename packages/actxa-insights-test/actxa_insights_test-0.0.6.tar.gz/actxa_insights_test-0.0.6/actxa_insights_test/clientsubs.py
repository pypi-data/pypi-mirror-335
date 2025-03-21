import requests
import json
from .config import get_url


def get_device_detail(
    env: str,
    x_api_key: str,
    email: str,
    password: str,
    device_id: str,
    # feature_code: str,
    # device_model: str,
    # client_name: str,
    # quota: int,
    # po_number: str,
):
    response_admin_login = requests.post(
        get_url(env) + "/client-subscription/api/v1/admin/login",
        headers={"X-API-KEY": x_api_key},
        json={"email": email, "password": password},
    )
    if response_admin_login.status_code != 200:
        return {"error": "Failed to fetch admin login credentials"}

    # response_register_license = requests.post(
    #     get_url(env) + "/client-subscription/api/v1/license/register",
    #     headers={
    #         "X-API-KEY": x_api_key,
    #         "Authorization": "Bearer " + response_admin_login.json()["data"]["token"],
    #     },
    #     json={
    #         "feature_code": json.loads(feature_code),
    #         "device_model": device_model,
    #         "client_name": client_name,
    #         "quota": quota,
    #         "po_number": po_number,
    #     },
    # )
    # if response_register_license.status_code != 200:
    #     return {"error": "Failed to Register License"}

    response_get_device_list_by_id = requests.get(
        f"{get_url(env)}/client-subscription/api/v1/device/{device_id}",
        headers={
            "X-API-KEY": x_api_key,
            "Authorization": "Bearer " + response_admin_login.json()["data"]["token"],
        },
    )
    if response_get_device_list_by_id.status_code != 200:
        return {"error": "Failed to get Device By ID"}

    return response_get_device_list_by_id.json()
