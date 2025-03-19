'''
Example queries using GraphiQL API
'''

GET_INSTANCES = '''
query instancesQuery{
    instances {
        edges{
            node{
                id
                name
                namespaces{
                    name
                    id
                }
            }
        }
    }
}
'''
'''
Query for retrieving instances that can be logged into.
Used in instances.get_instances_default()
'''

GET_UNVERSIONED_INSTANCES = '''
query instancesQuery{
    unversionedInstances {
        edges{
            node{
                id
                name
                namespaces{
                    name
                    id
                }
            }
        }
    }
}
'''
'''
Query for retrieving instances that can be logged into.
Used in instances.get_instances_default()
'''

GET_INSTANCE_ID = '''
query instanceIdQuery($instanceName: String!){
  instances(filter:{name:{equals:$instanceName}}){
    edges{
      node{
        id
      }
    }
  }
}
'''
'''
Query for retrieving instance id.
Used in instances.get_instance_id(instance_name)
'''
GET_UNVERSIONED_INSTANCE_ID = '''
query instanceIdQuery($instanceName: String!){
  unversionedInstances(filter:{name:{equals:$instanceName}}){
    edges{
      node{
        id
      }
    }
  }
}
'''
'''
Query for retrieving instance id.
Used in instances.get_instance_id(instance_name)
'''

GET_PROJECTS_LS = '''
query projectQuery{
  instances {
    edges{
      node{
        projects{
          edges{
          node{
            id
            name
            description
            }
          }
        }
      }
    }
  }
}
'''
'''
Query for retrieving all available projects.
Used in projects.get_projects_default()
'''

GET_PROJECTS_LS_INSTANCE = '''
query projectQueryInstance($instanceName: String){
  instances(filter:{name:{equals:$instanceName}}){
    edges{
      node{
        projects{
          edges{
            node{
              id
              name
              description
            }
          }
        }
      }
    }
  }
}
'''
'''
Query for retrieving specific projects.
Used in projects.get_projects_specific(instance_name)
'''

GET_PROJECTS_LS_INSTANCE_ID = '''
query projectQueryInstance($instanceId: [Long]){
  instances(filter:{id:{in:$instanceId}}){
    edges{
      node{
        projects{
          edges{
            node{
              id
              name
              description
            }
          }
        }
      }
    }
  }
}
'''
'''
Query for retrieving specific projects.
Used in projects.get_valid_projects(instance_id)
'''

GET_PROJECT_ID = '''
query projectIdQuery($instanceId: [Long], $projectName: String){
  instances(filter:{id:{in:$instanceId}}){
    edges{
      node{
        projects(filter:{name:{equals:$projectName}}){
          edges{
            node{
              id
            }
          }
        }
      }
    }
  }
}
'''
'''
Query for retrieving project id.
Used in projects.get_project_id(source_instance_id, project_name)
'''

GET_LABEL_ID = '''
query labelIdQuery($projectId: Long!, $labelName: String){
  project(id:$projectId){
    labels(filter:{name:{equals:$labelName}}){
      edges{
        node{
          id
        }
      }
    }
  }
}
'''
'''
Query for retrieving label id.
Used in labels.get_label_id(project_id, label_name)
'''

CREATE_LABEL = '''
mutation createLabelMutation($projectId: Long!, $labelName: String!, $versionedItemIds: [Long!]){
  createLabel(input:{projectId:$projectId, name:$labelName, versionedItemIds:$versionedItemIds}){
    name
    description
    id
  }
}
'''
'''
Mutation for creating label.
Used in labels.create_label(project_id, label_name, versioned_item_ids)
'''

DEPLOY_LABEL = '''
mutation deploy($input: DeploymentInput!){
    deploy(input: $input){
        deployment{
          id: id
        }
    }
}
'''



'''
Mutation for promoting a label to a versioned instance.
Used in label_versions.promote_label_version_call(target_instance_id, label_version_id)
'''

GET_VERSION_ID = '''
query versionIdQuery($labelId: Long!){
  label(id:$labelId){
    labelVersions{
     edges{
      node{
        id
        version
      }
     }
    }
  }
}
'''
'''
Query for retrieving latest label version id.
Used in label_versions.get_version_id_default(label_id) and
label_versions.get_version_id_specific(label_id, label_version)
'''

GET_NON_DEL_VERSION = '''
query nonDeletedVersionItems($projectId: Long!, $versionItemPath: String){
    project(id:$projectId){
      versionedItems(currentOnly: true, filter:{path:{starts:$versionItemPath}}) {
        edges {
          node {
            id
          }
        }
      }
    }
}'''
'''
Query for retrieving non-deleted version items.
Used in label_versions.get_version_ids(project_id, search_path)
'''

GET_DEPLOYMENT_STATE = '''
query deploymentState($id: Long!){
  deployment(id: $id){
    state
  }
}
'''
'''
Query for promotion status.
Used in label_versions.promotion_monitoring(promotion_id)
'''

GET_VERSION_ITEM_LS = '''
query getVersionItemLs{
    instances {
        edges {
            node {
                versionedItems {
                    edges {
                        node { 
                        id
                        instanceId
                        prettyPath
                        type
                        version
                        revisionType
                        clientMajor
                        dateTime
                        comment
                        }
                    }
                }
            }
        }
    }
}
'''
'''
Query for retrieving all versioned items.
Used by versioned_items.get_versioned_items_default()
'''

GET_VERSION_ITEM_LS_SPECIFIC = '''
query getVersionItemLsSpecific($instanceName:String, $projectName:String, $path:StringExpression, $currentOption:Boolean){
    instances(filter:{name:{equals:$instanceName}}) {
          edges {
            node {
              projects(filter:{name:{equals:$projectName}}) {
                edges {
                  node {
                    versionedItems(currentOnly:$currentOption, filter:{path:$path}) {
                      edges {
                        node {
                          id
                          prettyPath
                          type
                          version
                          revisionType
                          clientMajor
                          dateTime
                          comment
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
'''
'''
Query for retrieving specific versioned items.
Used by versioned_items.get_versioned_items_specific(instance_name, project_name, search_path, current_only)
'''

GET_LABEL_VERSIONS_SPECIFIC = '''
query getLabelVersionSpecific($sourceInstanceName:String, $projectName:String, $labelName: String){
        instances(filter:{name:{equals:$sourceInstanceName}}) {
          edges {
            node {
              projects(filter:{name:{equals:$projectName}}) {
                edges {
                  node {
                    labels(filter:{name:{equals:$labelName}}){
                    edges{
                      node{
                        name
                        labelVersions{
                            edges{
                                node{
                                  version
                                  id
                                  comment
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
'''
'''
Query for retrieving specific label version.
Used in label_versions.get_label_version_specific(source_instance_name, project_name, label_name)
'''

GET_LABEL_VERSIONS = '''
query getLabelVersion{
        instances {
              edges {
                node {
                  projects {
                    edges {
                      node {
                        labels{
                        edges{
                      node{
                        name
                        labelVersions{
                                edges{
                            node{
                              version
                              id
                              comment
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
'''
'''
Query for retrieving all label version.
Used in label_versions.get_label_version_default()
'''

GET_ALL_LABELS = '''
query getAllLabels{
  instances {
    edges {
      node {
        projects {
          edges {
            node {
              name
                labels {
                      edges {
                        node {
                          id
                        name
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
'''
'''
Query for retrieving all labels.
Used in labels.get_labels_default()
'''

GET_LABELS_SPECIFIC = '''
query getLabelsSpecific($instanceName: String!, $projectName: String){
  instances(filter:{name:{equals:$instanceName}}) {
    edges{
      node{
        projects(filter:{name:{equals:$projectName}}){
        edges{
            node{
              labels{
                edges{
                  node{
                    name
                    id
                    description
                    labelType
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
'''
'''
Query for retrieving specific labels.
Used in labels.get_labels_specific(instance_name, project_name)
'''

GET_LABEL_SPECIFIC = '''
query getLabelSpecific($instanceName: String, $projectName: String, $labelName: String){
  instances(filter:{name:{equals:$instanceName}}) {
    edges{
      node{
        projects(filter:{name:{equals:$projectName}}){
        edges{
          node{
                labels(filter:{name:{equals:$labelName}}){
                  edges{
                    node{
                      name
                      id
                      description
                      labelVersions {
                        edges {
                          node {
                            versionedItems {
                              edges {
                                node {
                                  id
                                  path
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
    }
  }
}
'''
'''
Query for retrieving a specific label.
Used in labels.get_labels_specific(instance_name, project_name, label_name)
'''


GET_VERSIONED_ITEM_BY_ID = '''
query getVersionedItemById($id:Long!){
  versionedItem(id:$id){
    id
  }
}
'''
'''
Query for retrieving a specific versioned item id.
Used in versioned_item.get_versioned_item_by_id(id)
'''

GET_NON_DEL_VERSION_PAGE = '''
query nonDeletedVersionItemsPage($projectId: Long!, $versionItemPath: String, $startCursor: String) {
  project(id: $projectId) {
    versionedItems(
      after: $startCursor,
      currentOnly: true, filter: {path: {starts: $versionItemPath}}, sort: PATH_ASC) {
      pageInfo {
        startCursor
        endCursor
        hasNextPage
      }
      edges {
        cursor
        node {
          id
          path
        }
      }
    }
  }
}
'''

GET_VERSIONED_NAMESPACES = '''
query getVersionedNamespaces($id: Long!){
  instance(id:$id){
    namespaces{
      id
    }
  }
}
'''

GET_UNVERSIONED_NAMESPACES = '''
query getUnversionedNamespaces($id: Long!){
  unversionedInstance(id:$id){
    namespaces{
      id
    }
  }
}
'''