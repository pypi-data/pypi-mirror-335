import queries
import constants
import requests
import pprint


# Query for all available versioned items and print.
def get_versioned_items_default():
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_VERSION_ITEM_LS}, verify=False)
    instance_array = response.json()["data"]["instances"]["edges"]
    for instance in instance_array:
        versioned_item_array = instance["node"]["versionedItems"]
        if versioned_item_array is not None:
            for versioned_item in versioned_item_array["edges"]:
                pprint.pprint(versioned_item["node"])
                print()
    return


# Query for specific non-deleted versioned items and print.
def get_versioned_items_specific(instance_name, project_name, search_path, current_only):
    option, path = get_option_and_path(search_path)
    variables = {
        'instanceName': instance_name,
        'projectName': project_name,
        'path': {option: path},
        'currentOption': current_only
    }
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_VERSION_ITEM_LS_SPECIFIC, 'variables': variables}, verify=False)
    versioned_item_array = response.json()["data"]["instances"]["edges"][0]["node"]["projects"]["edges"][0]["node"][
        "versionedItems"]
    for versioned_item in versioned_item_array["edges"]:
        pprint.pprint(versioned_item["node"])
        print()
    return


# Query for specific non-deleted versioned items and print.
def get_option_and_path(search_path):
    first_colon = search_path.find(':')
    return search_path[0:first_colon], search_path[first_colon + 1:]


def get_versioned_item_by_id(id):
    variables = {
        'id': id
    }
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_VERSIONED_ITEM_BY_ID, 'variables': variables}, verify=False)
    return response.json()
