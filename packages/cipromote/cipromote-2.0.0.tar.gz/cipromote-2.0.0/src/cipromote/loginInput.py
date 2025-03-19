import requests
import os
import cipromote.constants as constants
import cipromote.queries as queries

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
    try:
        response = requests.post(constants.GRAPH_URL, #headers={'x-auth-token': constants.X_AUTH_TOKEN},
                                 json={'query': queries.GET_INSTANCES}, verify=False, timeout=300)
    except requests.exceptions.RequestException as e:
        print(f"Failed to send POST to API Server, Error: {e}")
        exit(1)
    instance_array = response.json()["data"]["instances"]["edges"]
    for instance in instance_array:
        node_name = instance["node"]["name"]
        valid_instance_names.update({instance["node"]["name"]: instance["node"]["id"]})
        space_list = []
        for namespace in instance["node"]["namespaces"]:
            node_spaces = {namespace["name"]: namespace["id"]}
            space_list.append(node_spaces)
        valid_namespace_names.update({node_name: space_list})
    return


# Get Namespace ID for Namespace name
def get_namespace_id(instance_name, namespace_name):
    get_instance_info_from_server()
    instance_input = instance_name
    namespace_input = namespace_name
    namespaces = valid_namespace_names.get(instance_input)
    print(f"Namespaces in {instance_input}: {namespaces}")
    for space in namespaces:
        if namespace_name in space:
            space_id = space[namespace_name]
    print(f"Namespace ID selected: {space_id}")
    return space_id


# Ask the user to input necessary info for logging in. Returns credential string to ci-cli.
def get_login_from_user(source_instance_name, target_instance_name, namespace_name):
    get_instance_info_from_server()
    credentials = ""
    firstCred = True
    # Allow user to input credentials only two times.
    for i in range(2):
        if firstCred:
            instance_input = source_instance_name #instance_input = input("Enter instanceName: ")
        else:
            instance_input = target_instance_name
        space_id = get_namespace_id(instance_input, namespace_name)
        usernameInput = os.getenv('MOTIOCI_USERNAME') #input("Enter username: ")
        passwordInput = os.getenv('MOTIOCI_PASSWORD') #getpass()
        if firstCred:
            credentials = starting_str + login_str.format(namespaceIn=space_id,
                                                          usernameIn=usernameInput,
                                                          passwordIn=passwordInput,
                                                          instanceIn=valid_instance_names.get(instance_input))
            firstCred = False
        else:
            credentials = credentials + comma_str + login_str.format(
                namespaceIn=space_id,
                usernameIn=usernameInput,
                passwordIn=passwordInput,
                instanceIn=valid_instance_names.get(instance_input))
        print("Login instance saved!")

    if credentials != "":
        print("Logging in...")
        credentials = credentials + ending_str
        return credentials
    return
