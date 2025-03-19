## GraphQL API

#### What is GraphQL?

* Getting started with GraphQL: https://graphql.org/

#### Using MotioCI's GraphQL API

* GraphiQL
   * MotioCI includes a GraphQL Web IDE that allows users to interact with the GraphQL API as well as view the documentation for the API.
   * To access it, go to (https://ciServerUrl/graphiql/index.html)

## MotioCI GraphQL API Samples

This is a sample GraphQL API client written in Python. This provides a simple command line interface allowing users to create and promote labels between Cognos environments. Samples are intended as a starting point and are provided as is.

### Prerequisites
* Minimum Python version 3.8.0 or higher
* Install Python at https://www.python.org/downloads **IMPORTANT: During installation, make sure to add Python to PATH and install pip**
* To verify installation, type `python` in a terminal and verify it returns version info.

### Troubleshooting

* If 'python --version' does not return 3.8.0 or higher, try using 'py -3' instead of 'python' for the CLI commands.

### Setup

1. Open a new terminal and cd to the CLI directory. Optionally: Move/Copy CLI folder to a different location.
2. Run the command:
```sh
pip install -r requirements.txt
```
3. Once that is completed, the MotioCI CLI tool is ready to run API commands.

### Example commands

#### Login Command

Purpose: Generate a xauthtoken which is needed to run commands using the CLI.

Information about instances and namespaces can be gathered through the GraphiQL Web IDE using this query:

```graphql
query getInstanceAndNamespaceInformation {
  instances {
    edges{
      node {
        id
        name
        namespaces {
          id
        }
      }
    }
  }
}
```

First, we'll need to create a credentials string to authenticate against CI/Cognos. This is a JSON array of credentials for 1 or more Cognos instances:

```json
[ 
    {
        "namespaceId":"xmlcap",
        "username":"jdoe",
        "password":"mYp@ssword",
        "instanceId":"1"},
    {
        "namespaceId":"xmlcap",
        "username":"jdoe",
        "password":"mYp@ssword",
        "instanceId":"2"},
    {
        "namespaceId":"xmlcap",
        "camPassportId":"123582103948340982134098l",
        "instanceId":"3"
    }
]
```

These can either be username/password credentials or a camPassport retrieved via the Cognos SDK.

**In all examples below, replace server parameter with your server URL and credentials parameter with your credentials.**

1. The login example below works on UNIX based systems.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" login --credentials '[{"namespaceId":"xmlcap","username":"jdoe","password":"mYp@ssword","instanceId":"1"},{"namespaceId":"xmlcap","username":"jdoe","password":"mYp@ssword","instanceId":"2"}]'
```
2. The login example below works on cmd on Windows.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" login --credentials [{\"namespaceId\":\"xmlcap\",\"username\":\"jdoe\",\"password\":\"mYp@ssword\",\"instanceId\":\"1\"},{\"namespaceId\":\"xmlcap\",\"username\":\"jdoe\",\"password\":\"mYp@ssword\",\"instanceId\":\"2\"}]
```
3. On either UNIX or Windows systems, instead of directly passing the credentials, the script prompts the user to enter credentials. Allows user to login up to two instances.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" login
```

#### Label Promotion Command

Purpose: Promote a label.

Information about projects and labels can be gathered through the GraphiQL Web IDE using this query:

```graphql
query getAllAvailableLabelVersions {
  instances {
    edges {
      node {
        __typename
        name
        id
        projects {
          edges {
            node {
              __typename
              name
              id
              labels {
                edges {
                  node {
                    __typename
                    name
                    id
                    labelVersions {
                      edges {
                        node {
                          __typename
                          id
                          version
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

**In all examples below, replace server parameter with your server URL and xauthtoken parameter with your valid xauthtoken from the login command.**

* Every argument after xauthtoken is optional, the script will query for user input.
* The following values can be provided and are optional: sourceInstanceName, targetInstanceName, projectName, searchPath, versionedItemId, labelName, label version, labelVersionId.
* When given a labelName that does not exist, the CLI will create a new label to promote.
* In order to promote between instances, user must be logged into source and target instances using the login command.
* Requires authentication for promotion. Use either Portal authentication (pass camPassportId parameter) or Standard authentication (pass namespaceId, username, and password parameters).
* The promote script assumes both the source and target project names are the same. If not, there will be a NoneType error thrown. This is a Python limitation and not a CLI limitation.
* When both searchPaths and versionedItemIds are provided, the script will create a new label with versioned items from both searchPaths and versionedItemIds.
* If both searchPaths and versionedItemIds are not provided, the script will ask for the user to input versionedItemIds. To stop entering versionedItemIds, press q to quit entering.

1. Promote given labelName and specific version of the label. Portal Authentication example.
   * If no version parameter is provided, CLI promotes the latest version of the label.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" labelVersion promote --xauthtoken=4a1a43e5-5ec2-40dd-94c3-1d6be05f2d3d --sourceInstanceName="Cognos Dev" --targetInstanceName="Cognos Prod" --projectName="Admin" --labelName="Shared Files Label" --version=1 --camPassportId="CAMPASSPORTID"
```
2. Promote given labelVersionId. Standard Authentication example.
   * The labelVersionId can be obtained only via running a label version script in the GraphiQL tool.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" labelVersion promote --xauthtoken=4a1a43e5-5ec2-40dd-94c3-1d6be05f2d3d --targetInstanceName="Cognos Prod" --labelVersionId=24 --namespaceId="NAMESPACEID" --username="jdoe" --password="mYp@ssword"
```
3. Promote given searchPath.
   * The searchPath parameter takes the value of the raw path of an object versioned in MotioCI.
   * Able to provide multiple space-seperated paths.
   * A path can point to a folder/report or any cognos object that can be promoted from a label.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" labelVersion promote --xauthtoken=4a1a43e5-5ec2-40dd-94c3-1d6be05f2d3d --sourceInstanceName="Cognos Dev" --targetInstanceName="Cognos Prod" --projectName="Admin" --labelName="Shared Files Label" --searchPath "/content/folder[@name='Motio Samples']" "/content/folder[@name='Motio Samples']/URL[@name='Test URL']" --camPassportId="CAMPASSPORTID"
```
4. Promote given versionedItemIds.
   * The versionedItemIds is the id of a specific version of an object.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" labelVersion promote --xauthtoken=4a1a43e5-5ec2-40dd-94c3-1d6be05f2d3d --sourceInstanceName="Cognos Dev" --targetInstanceName="Cognos Prod" --projectName="Admin" --labelName="Shared Files Label" --versionedItemIds="[11, 12]" --camPassportId="CAMPASSPORTID"
```
5. Promote given all optional parameters given including searchPath and versionedItemIds.
   * If label exists, promotes existing label. If label does not exist, creates a new label with searchPath and versionedItemIds then promotes that new label.
   * searchPath and the versionedItemId does not have to be of the same object.
   * versionedItemIds value can be for different objects to be promoted.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" labelVersion promote --xauthtoken=4a1a43e5-5ec2-40dd-94c3-1d6be05f2d3d --sourceInstanceName="Cognos Dev" --targetInstanceName="Cognos Prod" --projectName="Admin" --labelName="Shared Files Label" --searchPath "/content/folder[@name='Motio Samples']" "/content/folder[@name='Motio Samples']/URL[@name='Test URL']" --versionedItemIds="[11, 12]" --camPassportId="CAMPASSPORTID"
```
6. Promote given no parameters except xauthtoken and credentials. Prompts user to input all critical information.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" labelVersion promote --xauthtoken=4a1a43e5-5ec2-40dd-94c3-1d6be05f2d3d --camPassportId="CAMPASSPORTID"
```

#### Help Commands

Purpose: Provide information over available commands and parameters that are integrated in the CLI.

* To access the additional information, add the -h flag to the command.
* Must provide a server URL but does not require a xauthtoken.
1. If user wants more information on available subjects such as login, logout, instance, etc.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" -h
```
2. If user wants more information on available verbs such as ls, promote (labelVersion only), etc.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" label -h
```
3. If user wants more information on available arguments to pass for a specific command.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" label create -h
```

#### GraphiQL Queries
* Raw GraphiQL queries used for the CLI are available to view in the queries.txt file.
  --s
### Additional Commands

**In all examples below, replace server parameter with your server URL and xauthtoken parameter with your valid xauthtoken from the login command.**

#### Project ls Command
Purpose: Long listing of projects.

1. List all projects.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" project ls --xauthtoken=87a2470f-cb62-4662-98cf-c0e2bfc92184
```

2. List all projects for a specific instance.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" project ls --xauthtoken=87a2470f-cb62-4662-98cf-c0e2bfc92184 --instanceName="Cognos Dev"
```

#### Label ls Command
Purpose: Long listing of labels.

1. List all labels.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" label ls --xauthtoken=87a2470f-cb62-4662-98cf-c0e2bfc92184
```

2. List all labels for a specific instance and project
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" label ls --xauthtoken=87a2470f-cb62-4662-98cf-c0e2bfc92184 --instanceName="Cognos Dev" --projectName="Admin"
```

#### Label Create Command
Purpose: Create a label with versionedItemIds.

```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" label create --xauthtoken=87a2470f-cb62-4662-98cf-c0e2bfc92184 --instanceName="Cognos Dev" --projectName="Admin" --name="Cheese" --versionedItemIds="[11,12]"
```

#### Label Version ls Command
Purpose: Long listing of label versions.

```sh
1. List all label versions.
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" labelVersion ls --xauthtoken=87a2470f-cb62-4662-98cf-c0e2bfc92184
```

2. List all label versions for a specific instance, project, and label.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" labelVersion ls --xauthtoken=87a2470f-cb62-4662-98cf-c0e2bfc92184 --instanceName="Cognos Dev" --projectName="Admin" --labelName="Shared Files Label"
```

#### Versioned Item ls Command
Purpose: Long listing of versioned items.
```sh
1. List all versioned items.
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" versionedItems ls --xauthtoken=87a2470f-cb62-4662-98cf-c0e2bfc92184
```

2. List all versioned items for a specific instance, project, and searchPath. The user can choose to display only non-deleted versioned items by setting currentOnly to true.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" versionedItems ls --xauthtoken=87a2470f-cb62-4662-98cf-c0e2bfc92184 --instanceName="Cognos Dev" --projectName="Admin" --searchPath="starts:/content/" --currentOnly=True
```

#### Logout Command
Purpose: Logout out of CI/Cognos instances.
* After execution, the provided xauthtoken will no longer be valid.
```sh
python ci-cli.py --server="http://ci-docker.dallas.motio.com:8080" logout --xauthtoken=87a2470f-cb62-4662-98cf-c0e2bfc92184
```
