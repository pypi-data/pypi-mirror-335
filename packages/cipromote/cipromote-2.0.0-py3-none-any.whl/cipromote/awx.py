import os
from awxkit import api, config, utils, cli
from awxkit.api import ApiV2, job_templates
from awxkit.api.resources import resources


def auth_awx_get_resources():
    """ Authenticate with token to AWX and get API resources """
    awx_host = os.getenv("AWX_HOST")
    awx_token = os.getenv("AWX_TOKEN")
    config.base_url = awx_host
    awx_api_client = ApiV2()
    awx_api_client.connection.login(token=awx_token)
    awx_api_client.get(resources)
    return awx_api_client


def get_awx_template_by_id(awx_template_id):
    """ Authenticates to AWX and gets a template by ID """
    awx_api_client = auth_awx_get_resources()
    test_template_object_by_id = awx_api_client.job_templates.get(id=awx_template_id).results[0]
    return test_template_object_by_id
