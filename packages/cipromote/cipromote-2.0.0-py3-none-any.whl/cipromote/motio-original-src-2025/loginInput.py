import requests
import constants
import queries
from getpass import getpass

# Available options:
valid_instance_names = {}
valid_namespace_names = {}

# String literals
login_str = "{{"'"namespaceId"'":"'"{namespaceIn}"'","'"username"'":"'"{usernameIn}"'","'"password"'":"'"{passwordIn}"'","'"instanceId"'":"'"{instanceIn}"'"}}"""
comma_str = ", "
starting_str = "["
ending_str = "]"


# Set the instances and namespaces that the user can log in to based on their server link.
def get_instance_info_from_server():
    response = requests.post(constants.GRAPH_URL,
                             json={'query': queries.GET_INSTANCES}, verify=False)
    instance_array = response.json()["data"]["instances"]["edges"]
    for instance in instance_array:
        valid_instance_names.update({instance["node"]["name"]: instance["node"]["id"]})
        for namespace in instance["node"]["namespaces"]:
            valid_namespace_names.update({namespace["name"]: namespace["id"]})
    return


# Ask the user to input necessary info for logging in. Returns credential string to ci-cli.
def get_login_from_user():
    get_instance_info_from_server()
    print("Enter credentials below. Press q to stop.")
    credentials = ""
    firstCred = True
    # Allow user to input credentials only two times.
    for i in range(2):
        instanceInput = input("Enter instanceName: ")
        while instanceInput not in valid_instance_names and instanceInput != "q":
            print("Invalid instance. Available instances: ",
                  ', '.join(str(key) for key, _ in valid_instance_names.items()))
            instanceInput = input("Enter instanceName: ")
        if instanceInput == "q":
            break
        namespaceNameInput = input("Enter namespaceName: ")
        while namespaceNameInput not in valid_namespace_names and namespaceNameInput != "q":
            print("Invalid namespace. Available namespaces: ",
                  ', '.join(str(key) for key, _ in valid_namespace_names.items()))
            namespaceNameInput = input("Enter namespaceName: ")
        if namespaceNameInput == "q":
            break
        usernameInput = input("Enter username: ")
        if usernameInput == "q":
            break
        # nonecho password entry
        passwordInput = getpass()
        if passwordInput == "q":
            break
        if firstCred:
            credentials = starting_str + login_str.format(namespaceIn=valid_namespace_names.get(namespaceNameInput),
                                                          usernameIn=usernameInput,
                                                          passwordIn=passwordInput,
                                                          instanceIn=valid_instance_names.get(instanceInput))
            firstCred = False
        else:
            credentials = credentials + comma_str + login_str.format(
                namespaceIn=valid_namespace_names.get(namespaceNameInput),
                usernameIn=usernameInput,
                passwordIn=passwordInput,
                instanceIn=valid_instance_names.get(instanceInput))
        print("Login instance saved!")

    if credentials != "":
        print("Logging in...")
        credentials = credentials + ending_str
        return credentials
    return
