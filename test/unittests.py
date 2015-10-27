#!/usr/bin/env python

import os
import errno
import unittest
import wildfly
from wildfly import Wildfly
import requests
from requests import HTTPError


DEFAULT_NEXUS_HOST = 'nexus.cenx.localnet'
DEFAULT_NEXUS_PORT = '8081'

DEFAULT_GROUP_ID = 'org.jboss.mod_cluster'
DEFAULT_ARTIFACT_ID = 'mod_cluster-demo-server'
DEFAULT_ARTIFACT_VERSION = '1.2.6.Final'

client = None


def suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.TestLoader().loadTestsFromTestCase(ExecuteTest))
  suite.addTest(unittest.TestLoader().loadTestsFromTestCase(ReadAttributeTest))
  suite.addTest(unittest.TestLoader().loadTestsFromTestCase(WriteAttributeTest))
  suite.addTest(unittest.TestLoader().loadTestsFromTestCase(ReadChildrenNamesTest))
  suite.addTest(unittest.TestLoader().loadTestsFromTestCase(VersionTest))
  suite.addTest(unittest.TestLoader().loadTestsFromTestCase(PullTest))
  suite.addTest(unittest.TestLoader().loadTestsFromTestCase(DeployTest))
  suite.addTest(unittest.TestLoader().loadTestsFromTestCase(UndeployTest))
  suite.addTest(unittest.TestLoader().loadTestsFromTestCase(DeploymentInfoTest))
  suite.addTest(unittest.TestLoader().loadTestsFromTestCase(StartServersTest))
  suite.addTest(unittest.TestLoader().loadTestsFromTestCase(StopServersTest))
  suite.addTest(unittest.TestLoader().loadTestsFromTestCase(ReloadServersTest))
  suite.addTest(unittest.TestLoader().loadTestsFromTestCase(RestartServersTest))
  suite.addTest(unittest.TestLoader().loadTestsFromTestCase(ReadLogFileTest))
  return suite


def create_wildfly_service(mode='domain'):
  # use docker-py to create wildfly service (container) fixture
  pass

  
def remove_wildfly_service(mode='domain'):
  # use docker-py to remove wildfly service (container) fixture
  pass


def setUpModule():
  create_wildfly_service()
  global client
  wildfly_host = os.environ['DOCKER_HOST'].split(':')[1].replace('//', '')
  client = Wildfly(wildfly_host)

  
def tearDownModule():
  global client
  client.disconnect()
  remove_wildfly_service()
    
    
class ExecuteTest(unittest.TestCase):

  global client
  
  def test_execute_parms(self):
    operation = 'read-children-resources'
    parameters = {'child-type': 'host', 'include-runtime': 'true'}
    client.execute(operation=operation, parameters=parameters)

  def test_execute_defaults(self):
    operation = 'read-resource'
    client.execute(operation=operation)

  def test_execute_address(self):
    operation = 'read-resource'
    address = [{'server-group': 'A'}]
    client.execute(operation=operation, address=address)


class AddTest(unittest.TestCase):
  def test_add(self):
    self.fail()

    
class RemoveTest(unittest.TestCase):

  def test_remove(self):
    self.fail()

    
class ReadResourceTest(unittest.TestCase):

  global client

  def test_read_resource(self):
    result = client.read_resource([])
    self.assertEqual(result.json()['outcome'], 'success')

    
class ReadAttributeTest(unittest.TestCase):

  global client
    
  def test_read_attribute(self):
    result = client.read_attribute(address=[], name='process-type')
    self.assertEqual(result, 'Domain Controller')

    
class WriteAttributeTest(unittest.TestCase):

  global client

  def test_write_attribute(self):
    current_value = client.read_attribute(address=[], name='name')
    result = client.write_attribute(address=[], name='name', value='test')
    result = client.read_attribute(address=[], name='name')
    self.assertEqual(result, 'test')
    client.write_attribute(address=[], name='name', value=current_value)

    
class ReadChildrenNamesTest(unittest.TestCase):

  global client
    
  def test_read_children_names(self):
    result = client.read_children_names(address=[], child_type='server-group')
    self.assertIsNotNone(result)
    self.assertEquals(result[0], 'A')

    
class VersionTest(unittest.TestCase):

  global client
  
  def test_version(self):

    try:
      result = client.version()
    except Exception as e:
      self.fail('version raised exception unexpectedly! Exception: {}.'.format(e))
    self.assertEqual(result, '8.2.0.Final')


class PullTest(unittest.TestCase):

  global client
    
  def test_pull(self):

    client.pull(DEFAULT_GROUP_ID, DEFAULT_ARTIFACT_ID, DEFAULT_ARTIFACT_VERSION)
    client.undeploy(DEFAULT_ARTIFACT_ID)

    
class DeployTest(unittest.TestCase):

  global client
    
  def test_deploy_url(self):

    try:
      client.deploy(DEFAULT_GROUP_ID, DEFAULT_ARTIFACT_ID, DEFAULT_ARTIFACT_VERSION)
    except Exception as e:
      self.fail('deploy raised exception unexpectedly! Exception: {}.'.format(e))
      
    result = client.read_attribute('enabled',
                                   [{'server-group': 'A'},
                                    {'deployment': '{}.war'.format(DEFAULT_ARTIFACT_ID)}])
    self.assertTrue(result)
    client.undeploy(DEFAULT_ARTIFACT_ID)

  def test_deploy_file(self):

    NEXUS_BASE_URL = 'http://{}:{}/nexus' \
                     '/service/local/repo_groups/public/content'.format(DEFAULT_NEXUS_HOST,
                                                                        DEFAULT_NEXUS_PORT)
    url = '{0}/{1}/{2}/{3}/{2}-{3}.{4}'.format(NEXUS_BASE_URL,
                                               DEFAULT_GROUP_ID.replace('.', '/'),
                                               DEFAULT_ARTIFACT_ID, DEFAULT_ARTIFACT_VERSION,
                                               'war')
    response = requests.get(url)
          
    if response.status_code not in [200, 204]:
      print('Response Status Code: {}: {}'.format(response.status_code, response.reason))
      response.raise_for_status()

    with open("{}-{}.war".format(DEFAULT_ARTIFACT_ID, DEFAULT_ARTIFACT_VERSION), "wb") as artifact:
      artifact.write(response.content)
    
    try:
      client.deploy(DEFAULT_GROUP_ID, DEFAULT_ARTIFACT_ID, DEFAULT_ARTIFACT_VERSION,
                    path='{}-{}.war'.format(DEFAULT_ARTIFACT_ID,
                                            DEFAULT_ARTIFACT_VERSION))
    except Exception as e:
      self.fail('deploy raised exception unexpectedly! Exception: {}.'.format(e))
      
    result = client.read_attribute('enabled',
                                   [{'server-group': 'A'},
                                    {'deployment': '{}.war'.format(DEFAULT_ARTIFACT_ID)}])
    self.assertTrue(result)
    client.undeploy(DEFAULT_ARTIFACT_ID)
    os.remove("{}-{}.war".format(DEFAULT_ARTIFACT_ID, DEFAULT_ARTIFACT_VERSION))

  def test_deploy_file_not_exist(self):

    with self.assertRaises(IOError) as cm:
      client.deploy(DEFAULT_GROUP_ID, DEFAULT_ARTIFACT_ID, DEFAULT_ARTIFACT_VERSION,
                    path='no-file-at-path')
    exception = cm.exception
    self.assertEqual(exception.errno, errno.ENOENT)
    self.assertEqual(exception.strerror, os.strerror(exception.errno))

  def test_deploy_url_not_exist(self):

    with self.assertRaisesRegexp(HTTPError, "Not Found for url"):
      client.deploy('fake', 'fake', 'fake')

  @unittest.skip("still working on this one")
  def test_redeploy_url(self):

    pass
    try:
      client.deploy(DEFAULT_GROUP_ID, DEFAULT_ARTIFACT_ID, DEFAULT_ARTIFACT_VERSION)
    except Exception as e:
      self.fail('deploy raised exception unexpectedly! Exception: {}.'.format(e))
      
    result = client.read_attribute('enabled',
                                   [{'server-group': 'A'},
                                    {'deployment': '{}.war'.format(DEFAULT_ARTIFACT_ID)}])
    self.assertTrue(result)

    try:
      client.deploy(DEFAULT_GROUP_ID, DEFAULT_ARTIFACT_ID, DEFAULT_ARTIFACT_VERSION)
    except Exception as e:
      self.fail('deploy raised exception unexpectedly! Exception: {}.'.format(e))
      
    result = client.read_attribute('enabled',
                                   [{'server-group': 'A'},
                                    {'deployment': '{}.war'.format(DEFAULT_ARTIFACT_ID)}])
    self.assertTrue(result)

    client.undeploy(DEFAULT_ARTIFACT_ID)
    
    
class UndeployTest(unittest.TestCase):

  global client
    
  def test_undeploy(self):

    client.deploy(DEFAULT_GROUP_ID, DEFAULT_ARTIFACT_ID, DEFAULT_ARTIFACT_VERSION)
    client.undeploy(DEFAULT_ARTIFACT_ID)

  def test_undeploy_not_deployed(self):

    with self.assertRaises(HTTPError):
      client.undeploy(DEFAULT_ARTIFACT_ID)

    
class DeploymentInfoTest(unittest.TestCase):

  global client
    
  def setUp(self):
    client.deploy(DEFAULT_GROUP_ID, DEFAULT_ARTIFACT_ID, DEFAULT_ARTIFACT_VERSION)

  def tearDown(self):
    client.undeploy('mod_cluster-demo-server')
    
  def test_deployment_info(self):

    info = client.deployment_info()
    expected = {'{}.war'.format(DEFAULT_ARTIFACT_ID):
                {'runtime-name': '{}.war'.format(DEFAULT_ARTIFACT_ID)}}
    self.assertEqual(info, expected)
    
    
class StartServersTest(unittest.TestCase):

  global client
    
  def test_start_servers(self):
    client.start_servers(blocking=True)
    # self.client.server_info()
    # TODO assert that all servers are started
    # /host=172.17.0.72/server=172.17.0.72-0:read-attribute(name=server-state) = running
    
  def test_start_server_group(self):
    client.start_servers(server_group='A', blocking=True)
    # TODO assert that servers in group started

    
class StopServersTest(unittest.TestCase):

  global client
    
  def test_stop_servers(self):
    client.stop_servers(blocking=True)
    # TODO assert that all servers are stopped
    client.execute('read-children-resources',
                    {'child-type': 'host', 'include-runtime': 'true'})
    # /host=172.17.0.72:read-children-resources(child-type=server, include-runtime=true)
    # /host=172.17.0.72/server=172.17.0.72-0:read-attribute(name=server-state) = STOPPED
    # /host=172.17.0.72:read-children-resources(child-type=server-config, include-runtime=true)
    # /host=172.17.0.72/server-config=172.17.0.72-0:read-attribute(name=status) = STOPPED
    # /host=172.17.0.72/server-config=172.17.0.72-0:read-attribute(name=group)
    client.start_servers(blocking=True)

  def test_stop_server_group(self):
    client.stop_servers(server_group='A', blocking=True)
    # TODO assert that all servers are stopped
    client.start_servers(server_group='A', blocking=True)

    
class ReloadServersTest(unittest.TestCase):

  global client
    
  def test_reload_servers(self):
    client.reload_servers(blocking=True)
    # TODO assert that all servers are reloaded

  def test_reload_server_group(self):
    client.reload_servers(server_group='A', blocking=True)
    # TODO assert that all servers are reloaded

    
class RestartServersTest(unittest.TestCase):

  global client
    
  def test_restart_servers(self):
    client.restart_servers(blocking=True)
    # TODO assert that all servers are restarted

  def test_restart_server_group(self):
    client.restart_servers(server_group='A', blocking=True)
    # TODO assert that all servers in group are restarted

    
class ReadLogFileTest(unittest.TestCase):

  global client
    
  def test_log_file(self):

    logs = client.read_log_file()
    self.assertIsNotNone(logs)

    
if __name__ == '__main__':
  unittest.main(verbosity=2)
