# python binding for wildlfy management http/json api

import requests
from requests.auth import HTTPDigestAuth
import json
import logging

# setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class Wildfly:

  DEFAULT_MANAGEMENT_PORT = '9990'
  DEFAULT_MANAGEMENT_USER = 'admin'
  DEFAULT_MANAGEMENT_PWD = 'admin'

  def __init__(self, host, port=DEFAULT_MANAGEMENT_PORT,
               username=DEFAULT_MANAGEMENT_USER, password=DEFAULT_MANAGEMENT_PWD, timeout=5000):

    self.username = username
    self.password = password
    self.host = host
    self.port = port
    self.endpoint = 'http://{}:{}/management'.format(self.host, self.port)

  def disconnect(self):
    # not currently reusing/caching session/connection so no need for this
    pass
  
  def _post(self, request):

    logger.debug('Request: {}'.format(request))
    headers = {'content-type': 'application/json'}
    response = requests.post(self.endpoint, headers=headers,
                             auth=HTTPDigestAuth(self.username, self.password),
                             data=json.dumps(request))
    if response.status_code in [200, 204]:
      logger.debug('Response Status Code: {}: {}'.format(response.status_code, response.reason))
    else:
      logger.debug('Response Status Code: {}: {}'.format(response.status_code, response.reason))
      response.raise_for_status()
    logger.debug('Response: {}'.format(response.json()))
    return response

  def execute(self, operation, parameters={}, address=[]):
    """ Execute operation on resource. """

    request = {'address': address, 'operation': operation}
    request.update(parameters)
    response = self._post(request)
    return response
  
  def add(self, address, parameters=None):
    """ Creates a new management resource. """

    response = self.execute('add', parameters, address)
    return response

  def remove(self, address):
    """ Removes an existing resource. """

    response = self.execute('remove', address=address)
    return response
    
  def read_attribute(self, name, address=[], include_defaults=True):
    """ Read attribute of resource. """

    request = {'address': address, 'operation': 'read-attribute',
               'name': name, 'include-defaults': include_defaults}
    response = self._post(request)
    return response.json()['result']

  def write_attribute(self, name, value, address=[]):
    """ Write value of attribute of resource. """

    request = {'address': address, 'operation': 'write-attribute',
               'name': name, 'value': value}
    response = self._post(request)
    return response
  
  def read_children_names(self, child_type, address=[]):
    """ Returns a list of the names of all child resources of a given type. """

    request = {'address': address, 'operation': 'read-children-names',
               'child-type': child_type}
    response = self._post(request)
    return response.json()['result']
    
  # read-resource
  
  def version(self):
    """ Prints version of WildFly. """
    
    result = self.read_attribute('release-version')
    return result

  def _server_operation(self, operation, server_group=None, blocking=False):
    if server_group:
      address = [{'server-group': server_group}]
    else:
      address = []
    return self.execute(operation, {'blocking': blocking}, address)

  def start_servers(self, server_group=None, blocking=False):
    """ Starts all configured servers in domain or server_group that are not currently running. """
    return self._server_operation('start-servers', server_group, blocking)

  def stop_servers(self, server_group=None, blocking=False):
    """ Stops all servers currently running in the domain or server_group. """
    return self._server_operation('stop-servers', server_group, blocking)

  def reload_servers(self, server_group=None, blocking=False):
    """ Reloads all servers currently running in the domain. """
    return self._server_operation('reload-servers', server_group, blocking)
    
  def restart_servers(self, server_group=None, blocking=False):
    """ Restart all servers currently running in the domain or server_group. """
    return self._server_operation('restart-servers', server_group, blocking)

  def pull(self, groupId, artifactId, version, type='war', server_groups='A',
           path=None, nexus_host='nexus.cenx.localnet', nexus_port='8081'):
    """ Pull artifact from artifact repository into wildfly content repository. """
    self.deploy(groupId, artifactId, version, type, server_groups,
                path, enabled=False, nexus_host=nexus_host, nexus_port=nexus_port)
    
  def deploy(self, groupId, artifactId, version, type='war', server_groups='A',
             path=None, enabled=True,
             nexus_host='nexus.cenx.localnet', nexus_port='8081'):

    # TODO support new deploy and redeploy
    # TODO if deploy fails then show tail of logs
    # TODO if deploy fails then rollback to previous

    if path is None:
      
      # deploy application from nexus
      NEXUS_BASE_URL = 'http://{}:{}/nexus' \
                       '/service/local/repo_groups/public/content'.format(nexus_host,
                                                                          nexus_port)
      url = '{0}/{1}/{2}/{3}/{2}-{3}.{4}'.format(NEXUS_BASE_URL,
                                                 groupId.replace('.', '/'),
                                                 artifactId, version, type)
      
      # upload artifact to deployment content repository
      response = self.execute('upload-deployment-url', {'url': url})

    else:
      # deploy application from local file path
      # files = {'file': open(path.format(artifactId, 'rb')}
      files = {'file': open(path, 'rb')}
      # logger.debug('Request: {}'.format(request))
      response = requests.post(self.endpoint + '/add-content', files=files,
                               auth=HTTPDigestAuth(self.username, self.password))
      logger.debug('Response Status Code: {}: {}'.format(response.status_code, response.reason))
      logger.debug('Response: {}'.format(response.json()))

    # add artifact to content repository
    byte_value = response.json()['result']['BYTES_VALUE']
    request = {"content": [{"hash": {"BYTES_VALUE": byte_value}}],
               "address": [{"deployment": "{}.{}".format(artifactId, type)}],
               "operation": "add"}
    response = self._post(request)
 
    # add artifact to server-group(s)
    address = [{'server-group': server_groups},
               {'deployment': '{}.{}'.format(artifactId, type)}]
    response = self.execute('add', {'enabled': enabled}, address)

  def deployment_info(self, name=None, server_group=None):
    """ Displays information about deployments. """

    # name, runtime_name, enabled, status
    # request = {'operation': 'read-children-names', 'child-type': 'deployment')
    response = self.execute('read-children-resources', {'child-type': 'deployment'})
    result = response.json()['result']
    artifacts = {}
    for artifact in result.keys():
      artifacts[result[artifact]['name']] = {'runtime-name': result[artifact]['runtime-name']}
    return artifacts
      
  def undeploy(self, artifactId, type='war', server_groups='A'):

    # remove artifact from server-group(s)
    address = [{'server-group': server_groups},
               {'deployment': "{}.{}".format(artifactId, type)}]
    self.execute('remove', {}, address)

    # remove artifact from content repository
    address = [{"deployment": "{}.{}".format(artifactId, type)}]
    self.execute('remove', {}, address)
    
  def read_log_file(self, host=None):
    """ Reads the contents of a log file.
    The file must be in the jboss.server.log.dir and must be defined as
    a file-handler, periodic-rotating-file-handler or size-rotating-file-handler. """

    if host is None:
      response = self.execute('read-children-names', {'child-type': 'host'})
      host = response.json()['result'][0]
      
    address = [{'host': host},
               {'server': '{}-0'.format(host)},
               {'subsystem': 'logging'}]
    parameters = {'name': 'server.log', 'tail': 'true', 'lines': '100'}
    response = self.execute('read-log-file', parameters, address)
    return response.json()['result']

  def add_datasource():
   pass

  def remove_datasource():
    pass

  def add_jms_destination():
    pass

  def remove_jms_destination():
    pass
