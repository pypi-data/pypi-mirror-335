import pytest

from liquid_earth_sdk.modules.rest_client.rest_interface import get_dev_tokens, generate_dev_token, revoke_dev_token
import dotenv
import os
import requests

dotenv.load_dotenv()

pytestmark = pytest.mark.skip(reason="Requires Liquid Earth API credentials")

def test_login_with_credentials():
    endpoint = os.getenv("LOGIN_URL")
    subscription_key = os.getenv("LOGIN_SUBSCRIPTION_KEY")  # Add this line
    headers = {
            "Content-Type"             : "application/x-www-form-urlencoded",
            "X-App-Version"            : "1.0.8.1",
            "Ocp-Apim-Subscription-Key": subscription_key  # Add this line
    }

    payload = os.getenv("LOGIN_PAYLOAD")

    response = requests.post(endpoint, headers=headers, data=payload)
    result = response.json()
    print(result)


def test_get_user_dev_tokens():
    val = get_dev_tokens(
        user_id=os.getenv("TEST_USER_ID"),
        login_token="Bearer " + os.getenv("TEST_LOGIN_TOKEN")
    )
    print(val)


def test_generate_dev_token():
    val = generate_dev_token(
        token_name="test_token",
        user_id=os.getenv("TEST_USER_ID"),
        login_token=os.getenv("TEST_LOGIN_TOKEN")
    )
    print(val)


def test_revoke_dev_token():
    val = revoke_dev_token(
        user_id="7c775179-437b-4269-8cf7-8e6a419f1b00",
        token_id="le-8b4c9d33528a4e7492583871f6545ea4IAmNqhThFXeIKMQTzummp0Zdyhejwnqh1iSteK1A55I",
        login_token="unused_in_local_dev"
    )
    print(val)
