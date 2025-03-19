import requests
import cipromote.constants as constants
import cipromote.queries as queries

# Query for all available instances.
def get_instances_default():
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_INSTANCES}, verify=False)
    instance_array = response.json()["data"]["instances"]["edges"]
    return instance_array


def get_unversioned_instances_default():
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_UNVERSIONED_INSTANCES}, verify=False)
    instance_array = response.json()["data"]["unversionedInstances"]["edges"]
    return instance_array


# Print instances name and id only. Used to prompt user about available instances.
def print_instances(instance_array):
    for instance in instance_array:
        print("[Name:", instance["node"]["name"], " ID:", instance["node"]["id"], "]", end=" ")
    return


# Query for specific instance id by instance_name.
def get_instance_id(instance_name):
    variables = {'instanceName': instance_name}
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_INSTANCE_ID, 'variables': variables}, verify=False)
    print(response)
    instance_id = response.json()["data"]["instances"]["edges"][0]["node"]["id"]
    return instance_id


# Query for specific instance id by instance_name.
def get_unversioned_instance_id(instance_name):
    variables = {'instanceName': instance_name}
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_UNVERSIONED_INSTANCE_ID, 'variables': variables}, verify=False)
    instance_id = response.json()["data"]["unversionedInstances"]["edges"][0]["node"]["id"]
    return instance_id


# Check if instance_id is valid in instance_array
def check_if_valid_instance_id(instance_array, instance_id):
    for instance in instance_array:
        if instance_id == instance["node"]["id"]:
            return True
    return False


# Check if instance_name is valid in instance_array
def check_if_valid_instance_name(instance_array, instance_name):
    for instance in instance_array:
        if instance_name == instance["node"]["name"]:
            return True
    return False
