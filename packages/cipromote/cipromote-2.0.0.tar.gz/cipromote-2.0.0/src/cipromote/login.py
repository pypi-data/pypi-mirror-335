import os
import requests
import cipromote.constants as constants

def login_init(login_instance_info):
    server_url = os.getenv("MOTIOCI_SERVERURL")
    constants.CI_URL = server_url
    print(f"Logging in at {constants.LOGIN_URL}.")
    response = requests.post(constants.LOGIN_URL, data=login_instance_info, verify=False)
    print(f"The response from the API is \n{response}")
    #print(f"The content of the response is \n{(response.content).decode('utf-8')}")
    return response.headers.get("x-auth-token")
