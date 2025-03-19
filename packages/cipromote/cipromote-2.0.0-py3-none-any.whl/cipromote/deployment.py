import requests
import time
import cipromote.constants as constants
import cipromote.queries as queries


# Mutation for promoting a label given target_instance_id and label_version_id.
# Calls deployment monitoring to prompt user about deployment progress.

def deploy(source_label_input, source_instance_id, deployment_target_input):

    variables = {'input':{'source': {'instanceId': source_instance_id, 'label': source_label_input},
                          'target':deployment_target_input}}

    response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                             json={'query': queries.DEPLOY_LABEL, 'variables': variables}, verify=False)
    print_deployment_response(response.json())

# Calls promotion monitoring to prompt user about promotion progress.
def print_deployment_response(response_json):
    if "errors" in response_json:
        print("Error performing the deployment:\n ", response_json["errors"])
    else:
        deployment_id = response_json["data"]["deploy"]["deployment"]["id"]
        print("deploymentID: " + str(deployment_id))
        deployment_monitoring(deployment_id)
        print("Deployed!")


# Prompts user about promotion progress.
def deployment_monitoring(deployment_id):
    deployment_status = ""
    while deployment_status != "DISALLOWED" and deployment_status != "EXECUTED":
        variables = {'id': deployment_id}
        response = requests.post(constants.GRAPH_URL, headers={'x-auth-token': constants.X_AUTH_TOKEN},
                                 json={'query': queries.GET_DEPLOYMENT_STATE, 'variables': variables}, verify=False)
        deployment_status = str(response.json()["data"]["deployment"]["state"])
        print("deployment result: " + deployment_status)
        time.sleep(6)
    return
