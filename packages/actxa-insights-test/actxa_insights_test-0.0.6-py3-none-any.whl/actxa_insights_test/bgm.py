import requests
from .config import get_url


def predict_bgm_range_app(
    env: str,
    application_id: str,
    device_id: str,
    serial_number: str,
    user_id: int,
    req_body,
):
    response_access_token = requests.post(
        get_url(env)
        + "/client-subscription/api/v1/key-secret/application-access-token",
        json={"application_id": application_id},
    )
    if response_access_token.status_code != 200:
        return {"error": "Failed to fetch client data"}

    response_jwt_user = requests.post(
        get_url(env) + "/user/api/v3/user/refreshToken",
        headers={"access-token": response_access_token.json()["data"]["access_token"]},
        json={"userID": user_id},
    )
    if response_jwt_user.status_code != 200:
        return {"error": "Failed to fetch user data"}

    response_bgm_range = requests.post(
        get_url(env) + "/bgem/api/v4_1/analysis",
        headers={
            "access-token": response_access_token.json()["data"]["access_token"],
            "device-id": device_id,
            "device-serial-number": serial_number,
            "Authorization": "Bearer " + response_jwt_user.json()["data"]["token"],
        },
        json=req_body,
    )
    if response_bgm_range.status_code != 200:
        return {"error": "error prediction"}

    return response_bgm_range.json()


def predict_bgm_classification_app(
    env: str,
    application_id: str,
    device_id: str,
    serial_number: str,
    user_id: int,
    req_body,
):
    response_access_token = requests.post(
        get_url(env)
        + "/client-subscription/api/v1/key-secret/application-access-token",
        json={"application_id": application_id},
    )
    if response_access_token.status_code != 200:
        return {"error": "Failed to fetch client data"}

    response_jwt_user = requests.post(
        get_url(env) + "/user/api/v3/user/refreshToken",
        headers={"access-token": response_access_token.json()["data"]["access_token"]},
        json={"userID": user_id},
    )
    if response_jwt_user.status_code != 200:
        return {"error": "Failed to fetch user data"}

    response_bgm_range = requests.post(
        get_url(env) + "/bgem/api/v5/analysis",
        headers={
            "access-token": response_access_token.json()["data"]["access_token"],
            "device-id": device_id,
            "device-serial-number": serial_number,
            "Authorization": "Bearer " + response_jwt_user.json()["data"]["token"],
        },
        json=req_body,
    )
    if response_bgm_range.status_code != 200:
        return {"error": "error prediction"}

    return response_bgm_range.json()


def bgm_range_result(
    env: str,
    application_id: str,
    device_id: str,
    serial_number: str,
    user_id: int,
    measurement_id: str,
):
    response_access_token = requests.post(
        get_url(env)
        + "/client-subscription/api/v1/key-secret/application-access-token",
        json={"application_id": application_id},
    )
    if response_access_token.status_code != 200:
        return {"error": "Failed to fetch client data"}

    response_jwt_user = requests.post(
        get_url(env) + "/user/api/v3/user/refreshToken",
        headers={"access-token": response_access_token.json()["data"]["access_token"]},
        json={"userID": user_id},
    )
    if response_jwt_user.status_code != 200:
        return {"error": "Failed to fetch user data"}

    response_bgm_range = requests.get(
        get_url(env) + "/bgem/api/v4_1/measurement/" + measurement_id,
        headers={
            "access-token": response_access_token.json()["data"]["access_token"],
            "device-id": device_id,
            "device-serial-number": serial_number,
            "Authorization": "Bearer " + response_jwt_user.json()["data"]["token"],
        },
    )
    if response_bgm_range.status_code != 200:
        return {"error": "Failed to fetch measurement data"}

    return response_bgm_range.json()


def bgm_classification_result(
    env: str,
    application_id: str,
    device_id: str,
    serial_number: str,
    user_id: int,
    measurement_id: str,
):
    response_access_token = requests.post(
        get_url(env)
        + "/client-subscription/api/v1/key-secret/application-access-token",
        json={"application_id": application_id},
    )
    if response_access_token.status_code != 200:
        return {"error": "Failed to fetch client data"}

    response_jwt_user = requests.post(
        get_url(env) + "/user/api/v3/user/refreshToken",
        headers={"access-token": response_access_token.json()["data"]["access_token"]},
        json={"userID": user_id},
    )
    if response_jwt_user.status_code != 200:
        return {"error": "Failed to fetch user data"}

    response_bgm_range = requests.get(
        get_url(env) + "/bgem/api/v5/measurement/" + measurement_id,
        headers={
            "access-token": response_access_token.json()["data"]["access_token"],
            "device-id": device_id,
            "device-serial-number": serial_number,
            "Authorization": "Bearer " + response_jwt_user.json()["data"]["token"],
        },
    )
    if response_bgm_range.status_code != 200:
        return {"error": "Failed to fetch measurement data"}

    return response_bgm_range.json()
