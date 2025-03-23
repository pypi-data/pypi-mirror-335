from liquid_earth_api.core.output import AvailableProject
from liquid_earth_api.modules.rest_client._utils import handle_response
from liquid_earth_api.core.data.schemas import AddNewSpacePostData, AddDataPostData, DeleteSpacePostData
import requests
from dataclasses import asdict
from liquid_earth_api.config import BASE_URL


def get_deep_link(post_data: AddDataPostData, token: str) -> any:
    response = requests.post(
        url=f"{BASE_URL}/GetDeepLinkFromSpace",
        json=asdict(post_data),
        headers={"Authorization": f"{token}"}
    )
    return handle_response(response)  # Use helper to process the response


def post_add_data_to_space(post_data: AddDataPostData, token: str) -> dict:
    response = requests.post(
        url=f"{BASE_URL}/AddDataToSpace",
        json=asdict(post_data),
        headers={"Authorization": f"{token}"}
    )
    return handle_response(response)


def get_available_projects(token: str) -> list:
    response = requests.get(
        url=f"{BASE_URL}/GetAvailableProjects",
        headers={"Authorization": f"{token}"},
        timeout=60
    )
    data: list = handle_response(response)
    foo: list[AvailableProject] = [AvailableProject(**item) for item in data]
    
    return foo


def post_create_space(add_new_space: AddNewSpacePostData, token: str) -> dict:
    response = requests.post(
        url=f"{BASE_URL}/AddNewSpace/v2",
        json=asdict(add_new_space),
        headers={"Authorization": f"{token}"}
    )
    return handle_response(response)


def delete_space(delete_space_post_data: DeleteSpacePostData, token: str) -> dict:
    response = requests.delete(
        url=f"{BASE_URL}/DeleteSpace",
        json=asdict(delete_space_post_data),
        headers={"Authorization": f"{token}"}
    )
    return handle_response(response)


def get_dev_tokens(user_id: str, login_token: str) -> dict:
    response = requests.get(
        url=f"{BASE_URL}/apikeys",
        params={"user_id": user_id},
        headers={"Authorization": f"{login_token}"}
    )
    return handle_response(response)


def generate_dev_token(user_id: str, token_name: str, login_token: str) -> dict:
    response = requests.post(
        url=f"{BASE_URL}/apikeys/generate",
        params={"user_id": user_id},
        json={"name": token_name},
        headers={"Authorization": f"{login_token}"}
    )
    return handle_response(response)


def revoke_dev_token(user_id: str, token_id: str, login_token: str) -> dict:
    response = requests.post(
        url=f"{BASE_URL}/apikeys/revoke",
        params={"user_id": user_id},
        json={"keyId": token_id},
        headers={"Authorization": f"{login_token}"}
    )
    return handle_response(response)
