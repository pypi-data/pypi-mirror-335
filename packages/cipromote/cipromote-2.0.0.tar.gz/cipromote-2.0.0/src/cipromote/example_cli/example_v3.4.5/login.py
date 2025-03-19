import constants
import requests


def login_init(login_instance_info):
    response = requests.post(constants.LOGIN_URL, data=login_instance_info)
    return response.headers.get("x-auth-token")
