import requests
import constants
import queries
import time

# Query for all label versions available
def get_label_version_default():
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_LABEL_VERSIONS})
    instance_array = response.json()["data"]["instances"]["edges"]
    for instance in instance_array:
        project_array = instance["node"]["projects"]["edges"]
        for project in project_array:
            label_array = project["node"]["labels"]["edges"]
            for label_version_item in label_array:
                print(label_version_item)
    return


# Query for specific label versions given source_instance_name, project_name, and label_name
def get_label_version_specific(source_instance_name, project_name, label_name):
    variables = {'sourceInstanceName': source_instance_name, 'projectName': project_name, 'labelName': label_name}
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_LABEL_VERSIONS_SPECIFIC, 'variables': variables})
    label_version_list = response.json()["data"]["instances"]["edges"][0]["node"]["projects"]["edges"][0]["node"][
        "labels"]["edges"]
    for label_version_item in label_version_list:
        print(label_version_item)
    return


# Query for latest label version id given a label id
def get_version_id_default(label_id):
    variables = {'labelId': label_id}
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_VERSION_ID, 'variables': variables})
    node = response.json()["data"]["label"]["labelVersions"]["edges"][-1]["node"]
    print("label version " + str(node["version"]))
    return node["id"]


# Query for specific label version id given a label id and label version
def get_version_id_specific(label_id, label_version):
    variables = {'labelId': label_id}
    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.GET_VERSION_ID, 'variables': variables})
    node_list = response.json()["data"]["label"]["labelVersions"]["edges"]
    for node in node_list:
        if node["node"]["version"] == label_version:
            return node["node"]["id"]
    return None


# Retrieves versioned item ids when given a search path and outputs the ids found.
def get_version_ids(project_id, search_path):
    startCursor = None
    print("version item ids:", end=" ")
    ans = "["
    for path_item in search_path:
        for cur_path in path_item:
            variables = {'projectId': project_id, 'versionItemPath': cur_path, 'startCursor': startCursor}
            response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                                     json={'query': queries.GET_NON_DEL_VERSION_PAGE, 'variables': variables})
            while True:
                has_more = response.json()["data"]["project"]["versionedItems"]["pageInfo"]["hasNextPage"]
                endCursor = response.json()["data"]["project"]["versionedItems"]["pageInfo"]["endCursor"]
                variables = {'projectId': project_id, 'versionItemPath': cur_path, 'startCursor': endCursor}

                ##get every ID and put it in the label
                ##map collect for getting specific values in json
                items = response.json()["data"]["project"]["versionedItems"]["edges"]
                for item in items:
                    item_id = item["node"]["id"]
                    ans += str(item_id) + ","

                response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                                         json={'query': queries.GET_NON_DEL_VERSION_PAGE, 'variables': variables})

                if has_more == False:
                    break

    if ans[-1] != "[":
        ans = ans[:-1]
    ans += "]"
    print(ans)
    return ans
