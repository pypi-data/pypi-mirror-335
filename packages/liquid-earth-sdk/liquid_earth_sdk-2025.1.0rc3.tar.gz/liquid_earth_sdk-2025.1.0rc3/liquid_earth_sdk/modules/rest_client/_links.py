from dataclasses import asdict

import requests

from liquid_earth_sdk.core.data import AddDataPostData
from liquid_earth_sdk.config import BASE_URL


def get_deep_link(post_data: AddDataPostData, token: str):
    response = requests.post(
        url=f"{BASE_URL}/GetDeepLinkFromSpace",
        json=asdict(post_data),
        headers={
                "Authorization": f"{token}"
        }
    )

    # if request 200 return the deep link from text/plain
    if response.status_code == 200:
        return response.text
    else:
        print("Error getting deep link")
        return False
