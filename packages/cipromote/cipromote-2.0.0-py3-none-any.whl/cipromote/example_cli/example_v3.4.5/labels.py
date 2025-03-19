import pprint
import requests
import queries
import constants
import ast
import projects
import instances


# Query for label id when given project_id and label_name.
def get_label_id(project_id, label_name):
    variables = {'projectId': project_id, 'labelName': label_name}
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_LABEL_ID, 'variables': variables})
    label_list = response.json()["data"]["project"]["labels"]["edges"]

    if len(label_list) == 0:
        return None
    return label_list


# Check if label exists. If it does, return id. Else, create new label.
def create_label_if_not_exist(project_id, target_label_name, versioned_item_ids):
    label_id = get_label_id(project_id, target_label_name)
    if label_id is None:
        label_id = create_label(project_id, target_label_name, versioned_item_ids)
    return label_id


# Mutation for creating a label with a project_id, label_name, and versioned_item_ids.
def create_label(project_id, label_name, versioned_item_ids):
    versioned_item_ids_list = []
    if versioned_item_ids is not None:
        versioned_item_ids_list = versioned_item_ids
        if isinstance(versioned_item_ids, str):
            versioned_item_ids_list = ast.literal_eval(versioned_item_ids)
    variables = {'projectId': int(project_id), 'labelName': label_name, 'versionedItemIds': versioned_item_ids_list}
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.CREATE_LABEL, 'variables': variables})
    label_id = response.json()["data"]["createLabel"]["id"]
    return label_id


# Convert names to ids then calls helper create_label
def create_label_init(instance_name, project_name, label_name, versioned_item_ids):
    instance_id = instances.get_instance_id(instance_name)
    project_id = projects.get_project_id(instance_id, project_name)
    create_label(project_id, label_name, versioned_item_ids)
    return


# Query for all available labels.
def get_labels_default():
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_ALL_LABELS})
    instance_array = response.json()["data"]["instances"]["edges"]
    for instance in instance_array:
        project_array = instance["node"]["projects"]["edges"]
        for project in project_array:
            pprint.pprint(project)
    return


# Query for specific labels given an instance_name and project_name.
def get_labels_specific(instance_name, project_name):
    variables = {'instanceName': instance_name, 'projectName': project_name}
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_LABELS_SPECIFIC, 'variables': variables})
    label_array = response.json()["data"]["instances"]["edges"][0]["node"]["projects"]["edges"][0]["node"]["labels"][
        "edges"]
    for label in label_array:
        print(label)
    return


# Query for a specific label given instance_name, project_name, and label_name
def get_label_specific(instance_name, project_name, label_name):
    variables = {'instanceName': instance_name, 'projectName': project_name, 'labelName': label_name}
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_LABEL_SPECIFIC, 'variables': variables})
    pprint.pprint(response.json())
    return

