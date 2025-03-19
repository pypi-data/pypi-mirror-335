import requests
import cipromote.constants as constants
import cipromote.queries as queries


# Query for all available projects.
def get_projects_default():
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_PROJECTS_LS}, verify=False)
    instance_array = response.json()["data"]["instances"]["edges"]
    for instance in instance_array:
        project_list = instance["node"]["projects"]["edges"]
        for project_item in project_list:
            print(project_item)
    return


# Query for specific projects given instance_name
def get_projects_specific(instance_name):
    variables = {'instanceName': instance_name}
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_PROJECTS_LS_INSTANCE, 'variables': variables}, verify=False)
    project_list = response.json()["data"]["instances"]["edges"][0]["node"]["projects"]["edges"]
    for project_item in project_list:
        print(project_item)
    return


# Retrieve project_id when given source_instance_id and project_name.
def get_project_id(source_instance_id, project_name):
    variables = {'instanceId': source_instance_id, 'projectName': project_name}
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_PROJECT_ID, 'variables': variables}, verify=False)
    project_id = response.json()["data"]["instances"]["edges"][0]["node"]["projects"]["edges"][0]["node"]["id"]
    return project_id


# Query for all projects valid given an instance_id. Used for validating user inputted project ids/names
def get_valid_projects(instance_id):
    variables = {'instanceId': instance_id}
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_PROJECTS_LS_INSTANCE_ID, 'variables': variables}, verify=False)
    project_list = response.json()["data"]["instances"]["edges"][0]["node"]["projects"]["edges"]
    return project_list


# Print available projects. Used to prompt user about available projects.
def print_projects(project_list):
    for project in project_list:
        print("[Name:", project["node"]["name"], " ID:", project["node"]["id"], "]", end=" ")
    return


# Check if project_id is valid in project_list
def check_if_valid_project_id(project_list, project_id):
    for project in project_list:
        if project_id == project["node"]["id"]:
            return True
    return False


# Check if project_name is valid in project_list
def check_if_valid_project_name(project_list, project_name):
    for project in project_list:
        if project_name == project["node"]["name"]:
            return True
    return False
