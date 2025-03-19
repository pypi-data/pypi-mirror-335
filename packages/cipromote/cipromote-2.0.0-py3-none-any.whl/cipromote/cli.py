""" Core module with cli """
import click
import json
import sys
import os
import time
import requests
import cipromote.awx as awx
import cipromote.constants as constants
import cipromote.instances as instances
import cipromote.queries as queries
import cipromote.loginInput as loginInput
import cipromote.login as login
import cipromote.labels as labels
import cipromote.label_versions as label_versions
import cipromote.projects as projects
import cipromote.deployment as deployment
import logging
from termcolor import cprint
from pprint import pprint
from requests import Session
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
session = Session()
session.verify = False
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
session = Session()
session.verify = False
project_name = 'Admin'

@click.group()
def main():
    """
    This is a cli for promoting motioci labels

    Example:

    "$> cipromote get-instances 'https://server.example.com'"


    Example:

    "$> cipromote get-instances-token "New Dev" "New QA" "BillingCenter""

    """


@main.command("check-env", short_help="Check required environment variables")
def check_env():
    """Prints out the current necessary environment variables"""
    motioci_username = os.getenv("MOTIOCI_USERNAME")
    motioci_password = os.getenv("MOTIOCI_PASSWORD")
    motioci_server = os.getenv("MOTIOCI_SERVERURL")
    motioci_token = os.getenv("MOTIOCI_TOKEN")
    awx_host = os.getenv("AWX_HOST")
    awx_token = os.getenv("AWX_TOKEN")
    print(f"Your environment has {motioci_username} for the variable MOTIOCI_USERNAME")
    print(f"Your environment has {motioci_password} for the variable MOTIOCI_PASSWORD")
    print(f"Your environment has {motioci_server} for the variable MOTIOCI_SERVERURL")
    print(f"Your environment has {motioci_token} for the variable MOTIOCI_TOKEN")
    print(f"Your environment has {awx_host} for the variable AWX_HOST")
    print(f"Your environment has {awx_token} for the variable AWX_TOKEN")


@main.command("get-instances", short_help="Get a list of instances")
def get_instances():
    """Gets a list of instances"""
    server_url = os.getenv("MOTIOCI_SERVERURL")
    constants.CI_URL = server_url
    constants.GRAPH_URL = constants.CI_URL + constants.GRAPH_URL
    print('Sending query to the following url')
    print(constants.GRAPH_URL)
    instance_object = instances.get_instances_default()
    pprint(instance_object)
    return instance_object


@main.command("get-instance", short_help="Get an instance by name")
@click.argument("instance-name")
def get_instance(instance_name):
    """ Get a particular instance by name """
    server_url = os.getenv("MOTIOCI_SERVERURL")
    constants.CI_URL = server_url
    constants.GRAPH_URL = constants.CI_URL + constants.GRAPH_URL
    print('Sending query to the following url')
    print(constants.GRAPH_URL)
    instance_object = instances.get_instances_default()
    for instance in instance_object:
        if instance['node']['name'].lower() == instance_name.lower():
            target_instance = instance['node']
            print(f"The target instance is {target_instance['name']}")
            pprint(target_instance)
    return target_instance


@main.command("get-awx-job-template-by-id", short_help="Get AWX Job Template by ID")
@click.argument("awx-job-template-id")
def get_awx_job_template_by_id(awx_job_template_id):
    """ Gets an AWX Job Template by ID """
    awx_host = os.getenv("AWX_HOST")
    awx_token = os.getenv("AWX_TOKEN")
    job_info = awx.get_awx_template_by_id(awx_job_template_id)
    print(job_info)
    return job_info


@main.command("set-awx-job-template-vars", short_help="Set AWX Job Template vars")
@click.argument("awx-job-template-id")
@click.argument("awx-job-template-vars")
def set_awx_job_template_vars(awx_job_template_id, awx_job_template_vars):
    """ Set an AWX Job Template's default extra variables """
    awx_host = os.getenv("AWX_HOST")
    awx_token = os.getenv("AWX_TOKEN")
    job_template = awx.get_awx_template_by_id(awx_job_template_id)
    job_template.extra_vars = awx_job_template_vars
    job_template.put()
    return job_template


@main.command("monitor-instance", short_help="Check an instance by name every X seconds")
@click.argument("instance-name")
@click.argument("seconds")
def monitor_instance(instance_name, seconds):
    """ Check a particular instance by name every X seconds """
    server_url = os.getenv("MOTIOCI_SERVERURL")
    constants.CI_URL = server_url
    constants.GRAPH_URL = constants.CI_URL + constants.GRAPH_URL
    print('Sending query to the following url')
    print(constants.GRAPH_URL)
    while True:
        instance_object = instances.get_instances_default()
        for instance in instance_object:
            if instance['node']['name'].lower() == instance_name.lower():
                target_instance = instance['node']
                print(f"The target instance is {target_instance['name']}")
                pprint(target_instance)
                time.sleep(int(seconds))
    return target_instance


@main.command("monitor-namespace-notify", short_help="Check namespace instance and notify")
@click.argument("instance-name")
@click.argument("namespaces")
@click.argument("seconds")
@click.argument("awx-job-template-id")
def monitor_instance_namespaces(instance_name, namespaces, seconds, awx_job_template_id):
    """ Check a particular instance by name every X seconds

        Example: cipromote monitor-instance-namespaces Dev InfoCenter,BillingCenter 30
        Args:
            instance-name: The name of the node/instance to monitor
            namespaces: A single string or comma separated strings
            seconds: The number of seconds between each check
            awx_job_template_id: The ID of the template to launch on failure

    """
    awx_host = os.getenv("AWX_HOST")
    awx_token = os.getenv("AWX_TOKEN")
    server_url = os.getenv("MOTIOCI_SERVERURL")
    constants.CI_URL = server_url
    constants.GRAPH_URL = constants.CI_URL + constants.GRAPH_URL
    svc_names = namespaces.split(",")
    consecutive_ups = 0
    consecutive_downs = 0
    logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S')
    while True:
        instance_object = instances.get_instances_default()
        for instance in instance_object:
            if instance['node']['name'].lower() == instance_name.lower():
                target_instance = instance['node']
                up = []
                for ns in target_instance['namespaces']:
                    up.append(ns['name'].lower())
                for svc in svc_names:
                    if svc.lower() in up:
                        consecutive_ups += 1
                        logging.info(f"{svc} is up in {target_instance['name']} for {consecutive_ups} times in a row.")
                        consecutive_downs = 0
                    else:
                        consecutive_downs += 1
                        logging.error(f"{svc} is down in {target_instance['name']} for {consecutive_downs} times in a row.")
                        if consecutive_downs == 10:
                            awx_job_template_vars = {'namespace': svc, 'env': target_instance['name']}
                            json_vars = json.dumps(awx_job_template_vars)
                            job_template = awx.get_awx_template_by_id(awx_job_template_id)
                            job_template.extra_vars = json_vars
                            job_template.put()
                            job_template.launch()
                        consecutive_ups = 0
                time.sleep(int(seconds))
    return target_instance


@main.command("check-instance-namespace", short_help="Check if a particular namespace is present")
@click.argument("instance-name")
@click.argument("namespace-name")
def check_instance_namespace(instance_name, namespace_name):
    """ Check if a particular namespace is present in a particular instance """
    server_url = os.getenv("MOTIOCI_SERVERURL")
    constants.CI_URL = server_url
    constants.GRAPH_URL = constants.CI_URL + constants.GRAPH_URL
    print('Sending query to the following url')
    print(constants.GRAPH_URL)
    instance_object = instances.get_instances_default()
    for instance in instance_object:
        if instance['node']['name'].lower() == instance_name.lower():
            target_instance = instance['node']
            print(f"The target instance is {target_instance['name']}")
            namespaces = target_instance['namespaces']
            namespace_names = []
            for ns in namespaces:
                namespace_names.append(ns['name'].lower())
    try:
        namespace_names
    except NameError:
        print(f"No matching instance for {instance_name} was found.")
        sys.exit(1)
    print(f"Found the following namespaces {namespace_names}")
    if namespace_name.lower() in namespace_names:
        print(f"{namespace_name} was found in the list of connections")
        return namespace_names
    else:
        print(f"No connection found with the name {namespace_name}")
        sys.exit(1)


@main.command("get-labels", short_help="Get a list of available labels")
def get_labels():
    """Gets a lit of available labels"""
    server_url = os.getenv("MOTIOCI_SERVERURL")
    constants.CI_URL = server_url
    constants.GRAPH_URL = constants.CI_URL + constants.GRAPH_URL
    existing_token = os.getenv("MOTIOCI_TOKEN", '""')
    if (os.getenv("MOTIOCI_TOKEN") == "") or (os.getenv("MOTIOCI_TOKEN") == None):
        print(f"You need a valid token defined in your environment.\n"
                f"You should try check-env to check your environment."
                )
        raise SystemExit(1)
    else:
        constants.X_AUTH_TOKEN = os.getenv("MOTIOCI_TOKEN")
    labels_object = labels.get_labels_default()
    if labels_object == 'None':
        print(f"No labels found, maybe your token is expired?")
        raise SystemExit(1)
    return labels_object


@main.command("get-specific-label", short_help="Get a specific label by name")
@click.argument("instance-name")
@click.argument("namespace-name")
@click.argument("label-name")
def get_specific_label(instance_name, namespace_name, label_name):
    """Gets a specific label by name"""
    server_url = os.getenv("MOTIOCI_SERVERURL")
    constants.CI_URL = server_url
    constants.GRAPH_URL = constants.CI_URL + constants.GRAPH_URL
    existing_token = os.getenv("MOTIOCI_TOKEN", '""')
    if (os.getenv("MOTIOCI_TOKEN") == "") or (os.getenv("MOTIOCI_TOKEN") == None):
        print(f"You need a valid token defined in your environment.\n"
                f"You should try check-env to check your environment."
                )
        raise SystemExit(1)
    else:
        constants.X_AUTH_TOKEN = os.getenv("MOTIOCI_TOKEN")
    labels_object = labels.get_label_specific(instance_name, namespace_name, label_name)
    if labels_object == 'None':
        print(f"No labels found, maybe your token is expired?")
        raise SystemExit(1)
    return labels_object


@main.command("get-instances-token", short_help="Authenticate to two instances")
@click.argument("source-instance-name")
@click.argument("target-instance-name")
@click.argument("namespace-name")
def get_instances_token(source_instance_name, target_instance_name, namespace_name):
    """Authenticate against two instances and generates a token"""
    server_url = os.getenv("MOTIOCI_SERVERURL")
    constants.CI_URL = server_url
    constants.LOGIN_URL = constants.CI_URL + constants.LOGIN_URL
    constants.LOGOUT_URL = constants.CI_URL + constants.LOGOUT_URL
    constants.GRAPH_URL = constants.CI_URL + constants.GRAPH_URL
    motioci_username = os.getenv("MOTIOCI_USERNAME")
    motioci_password = os.getenv("MOTIOCI_PASSWORD")
    motioci_server = os.getenv("MOTIOCI_SERVERURL")
    print(
        f'The source instance is "{source_instance_name}". The target instance'
        f' is "{target_instance_name}". The namespace is "{namespace_name}".'
    )
    existing_token = os.getenv("MOTIOCI_TOKEN", '""')
    if (os.getenv("MOTIOCI_TOKEN") == "") or (os.getenv("MOTIOCI_TOKEN") == None):
        credentials = loginInput.get_login_from_user(
            source_instance_name, target_instance_name, namespace_name
        )
        #print(credentials)
        auth_token = login.login_init(credentials)
        if auth_token is None:
            print("Invalid credentials. Login aborted!")
        else:
            #print("Credentials: ", credentials)
            print("Login successful!")
            print("x-auth_token: ", auth_token)
            #os.environ.setdefault('MOTIOCI_TOKEN', auth_token)
            #os.environ['MOTIOCI_TOKEN'] = auth_token
            #print(os.getenv('MOTIOCI_TOKEN'))
            constants.X_AUTH_TOKEN = os.getenv("MOTIOCI_TOKEN")
    else:
        print(
            f"Found a token in environment variable MOTIOCI_TOKEN. {os.getenv('MOTIOCI_TOKEN')}\n"
            f"If you want to get a new token, clear your environment variable."
        )
        constants.X_AUTH_TOKEN = os.getenv("MOTIOCI_TOKEN")


@main.command("promote-label", short_help="Promote a label to a new instance")
@click.argument("source-instance-name")
@click.argument("target-instance-name")
@click.argument("namespace-name")
@click.argument("label-name")
def promote_label(source_instance_name, target_instance_name, namespace_name, label_name):
    """Promote a label from one instance to another"""
    global project_name
    server_url = os.getenv("MOTIOCI_SERVERURL")
    constants.CI_URL = server_url
    constants.LOGIN_URL = constants.CI_URL + constants.LOGIN_URL
    constants.LOGOUT_URL = constants.CI_URL + constants.LOGOUT_URL
    constants.GRAPH_URL = constants.CI_URL + constants.GRAPH_URL
    motioci_username = os.getenv("MOTIOCI_USERNAME")
    motioci_password = os.getenv("MOTIOCI_PASSWORD")
    existing_token = os.getenv("MOTIOCI_TOKEN", '""')
    if (os.getenv("MOTIOCI_TOKEN") == "") or (os.getenv("MOTIOCI_TOKEN") == None):
        print(f"You need a valid token defined in your environment"
                f"You should try check-env to check your environment."
                )
        raise SystemExit(1)
    else:
        print(
            f"Found a token in environment variable MOTIOCI_TOKEN. {os.getenv('MOTIOCI_TOKEN')}\n"
            f"If you want to get a new token, clear your environment variable and run get-instances-token command."
        )
        constants.X_AUTH_TOKEN = os.getenv("MOTIOCI_TOKEN")
    source_instance_id = instances.get_instance_id(source_instance_name)
    print(f"Instance {source_instance_name} has an ID of {source_instance_id}.")
    target_instance_id = instances.get_instance_id(target_instance_name)
    print(f"Instance {target_instance_name} has an ID of {target_instance_id}.")
    project_id = projects.get_project_id(source_instance_id, project_name)
    print(f"The project {project_name} has an ID of {project_id}.")
    label_list = labels.get_label_id(project_id, label_name)
    try:
        label_id = label_list[0]['node']['id']
        print(f"The label {label_name} has an ID of {label_id}.")
    except TypeError:
        print("The label was not found.")
        exit(1)
    except Exception as error:
        print("An error occurred: ", error)
        exit(1)
    try:
        label_version_id = label_versions.get_version_id_default(label_id)
        print(f"The Label ID {label_id} has a version of {label_version_id}.")
    except Exception as error:
        print("Failed to get the version ID of the label.", error)
        exit(1)
    namespace_id = loginInput.get_namespace_id(source_instance_name, namespace_name)
    try:
        print(f"Making the label version promote call")
        #print(f"target_instance_id {target_instance_id}")
        #print(f"label_version_id {label_version_id}")
        #print(f"namespace_id {namespace_id}")
        #print(f"motioci_username {motioci_username}")
        #print(f"motioci_password {motioci_password}")
        source_label_input = {'labelId': label_id}
        #print(f"source_label_input: {source_label_input}")
        #print(f"source_instance_id: {source_instance_id}")
        deployment_target_input = {'instance': {'id': target_instance_id, 'authentication': {'password': {'namespaceId': namespace_id,
                                                                                                          'username': motioci_username,
                                                                                                          'password': motioci_password}},
                                                'labelName': label_name}}
        #print(f"deployment_target_input: {deployment_target_input}")
        #label_versions.promote_label_version_call_standard_auth(target_instance_id, label_version_id, namespace_id, motioci_username, motioci_password)
        deployment.deploy(source_label_input, source_instance_id, deployment_target_input)
    except Exception as error:
        print("Failed to promote the label", error)
    return
