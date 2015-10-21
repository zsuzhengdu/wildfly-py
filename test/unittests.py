#!/usr/bin/env python

import os
import unittest
from wildfly import Wildfly
from requests import HTTPError


DEFAULT_GROUP_ID = 'org.jboss.mod_cluster'
DEFAULT_ARTIFACT_ID = 'mod_cluster-demo-server'
DEFAULT_ARTICT_VERSiON = '1.2.6.Final'

wildfly = None


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
  # use docker-py to create wildfly service fixture
  pass

  
def remove_wildfly_service(mode='domain'):
  # use docker-py to remove wildfly service fixture
  pass


def setUpModule():
  create_wildfly_service()
  wildfly_host = os.environ['DOCKER_HOST'].split(':')[1].replace('//', '')
  global wildfly
  wildfly = Wildfly(wildfly_host)

  
def tearDownModule():
  global wildfly
  wildfly.disconnect()
  remove_wildfly_service()
    
    
class ExecuteTest(unittest.TestCase):

  global wildfly
  
  def test_execute_parms(self):
    operation = 'read-children-resources'
    parameters = {'child-type': 'host', 'include-runtime': 'true'}
    wildfly.execute(operation=operation, parameters=parameters)

  def test_execute_defaults(self):
    operation = 'read-resource'
    wildfly.execute(operation=operation)

  def test_execute_address(self):
    operation = 'read-resource'
    address = [{'server-group': 'A'}]
    wildfly.execute(operation=operation, address=address)


class AddTest(unittest.TestCase):

  def test_add(self):
    self.fail()

    
class RemoveTest(unittest.TestCase):

  def test_remove(self):
    self.fail()

    
class ReadResourceTest(unittest.TestCase):

  global wildfly

  def test_read_resource(self):
    result = wildfly.read_resource([])
    self.assertEqual(result.json()['outcome'], 'success')

    
class ReadAttributeTest(unittest.TestCase):

  global wildfly
    
  def test_read_attribute(self):
    result = wildfly.read_attribute(address=[], name='process-type')
    self.assertEqual(result, 'Domain Controller')

    
class WriteAttributeTest(unittest.TestCase):

  global wildfly

  def test_read_attribute(self):
    result = wildfly.read_attribute(address=[], name='process-type')
    self.assertEqual(result, 'Domain Controller')

    
class ReadChildrenNamesTest(unittest.TestCase):

  global wildfly
    
  def test_read_children_names(self):
    result = wildfly.read_children_names(address=[], child_type='server-group')
    self.assertIsNotNone(result)
    self.assertEquals(result[0], 'A')

    
class VersionTest(unittest.TestCase):

  global wildfly
  
  def test_version(self):

    try:
      result = wildfly.version()
    except Exception as e:
      self.fail('version raised exception unexpectedly! Exception: {}.'.format(e))
    self.assertEqual(result, '8.2.0.Final')


class PullTest(unittest.TestCase):

  global wildfly
  groupId = DEFAULT_GROUP_ID
  artifactId = DEFAULT_ARTIFACT_ID
  version = DEFAULT_ARTICT_VERSiON
    
  def test_pull(self):

    wildfly.pull(self.groupId, self.artifactId, self.version)
    wildfly.undeploy(self.artifactId)

    
class DeployTest(unittest.TestCase):

  global wildfly
  groupId = DEFAULT_GROUP_ID
  artifactId = DEFAULT_ARTIFACT_ID
  version = DEFAULT_ARTICT_VERSiON
    
  def test_deploy_url(self):

    try:
      wildfly.deploy(self.groupId, self.artifactId, self.version)
    except Exception as e:
      self.fail('deploy raised exception unexpectedly! Exception: {}.'.format(e))
      
    result = wildfly.read_attribute('enabled',
                                    [{'server-group': 'A'},
                                     {'deployment': '{}.war'.format(self.artifactId)}])
    self.assertTrue(result)
    wildfly.undeploy(self.artifactId)

  def test_deploy_file(self):

    try:
      wildfly.deploy(self.groupId, self.artifactId, self.version,
                     path='/transport/{}-{}.war'.format(self.artifactId, self.version))
    except Exception as e:
      self.fail('deploy raised exception unexpectedly! Exception: {}.'.format(e))
      
    result = wildfly.read_attribute('enabled',
                                    [{'server-group': 'A'},
                                     {'deployment': '{}.war'.format(self.artifactId)}])
    self.assertTrue(result)
    wildfly.undeploy(self.artifactId)

    
class UndeployTest(unittest.TestCase):

  global wildfly
  groupId = DEFAULT_GROUP_ID
  artifactId = DEFAULT_ARTIFACT_ID
  version = DEFAULT_ARTICT_VERSiON
    
  def test_undeploy(self):

    wildfly.deploy(self.groupId, self.artifactId, self.version)
    wildfly.undeploy(self.artifactId)

  def test_undeploy_not_deployed(self):

    with self.assertRaises(HTTPError):
      wildfly.undeploy(self.artifactId)

    
class DeploymentInfoTest(unittest.TestCase):

  global wildfly
  groupId = DEFAULT_GROUP_ID
  artifactId = DEFAULT_ARTIFACT_ID
  version = DEFAULT_ARTICT_VERSiON
    
  def setUp(self):
    wildfly.deploy(self.groupId, self.artifactId, self.version)

  def tearDown(self):
    wildfly.undeploy('mod_cluster-demo-server')
    
  def test_deployment_info(self):

    info = wildfly.deployment_info()
    expected = {'{}.war'.format(self.artifactId):
                {'runtime-name': '{}.war'.format(self.artifactId)}}
    self.assertEqual(info, expected)
    
    
class StartServersTest(unittest.TestCase):

  global wildfly
    
  def test_start_servers(self):
    wildfly.start_servers(blocking=True)
    # self.wildfly.server_info()
    # TODO assert that all servers are started
    # /host=172.17.0.72/server=172.17.0.72-0:read-attribute(name=server-state) = running
    
  def test_start_server_group(self):
    wildfly.start_servers(server_group='A', blocking=True)
    # TODO assert that servers in group started

    
class StopServersTest(unittest.TestCase):

  global wildfly
    
  def test_stop_servers(self):
    wildfly.stop_servers(blocking=True)
    # TODO assert that all servers are stopped
    wildfly.execute('read-children-resources',
                    {'child-type': 'host', 'include-runtime': 'true'})
    # /host=172.17.0.72:read-children-resources(child-type=server, include-runtime=true)
    # /host=172.17.0.72/server=172.17.0.72-0:read-attribute(name=server-state) = STOPPED
    # /host=172.17.0.72:read-children-resources(child-type=server-config, include-runtime=true)
    # /host=172.17.0.72/server-config=172.17.0.72-0:read-attribute(name=status) = STOPPED
    # /host=172.17.0.72/server-config=172.17.0.72-0:read-attribute(name=group)
    wildfly.start_servers(blocking=True)

  def test_stop_server_group(self):
    wildfly.stop_servers(server_group='A', blocking=True)
    # TODO assert that all servers are stopped
    wildfly.start_servers(server_group='A', blocking=True)

    
class ReloadServersTest(unittest.TestCase):

  global wildfly
    
  def test_reload_servers(self):
    wildfly.reload_servers(blocking=True)
    # TODO assert that all servers are reloaded

  def test_reload_server_group(self):
    wildfly.reload_servers(server_group='A', blocking=True)
    # TODO assert that all servers are reloaded

    
class RestartServersTest(unittest.TestCase):

  global wildfly
    
  def test_restart_servers(self):
    wildfly.restart_servers(blocking=True)
    # TODO assert that all servers are restarted

  def test_restart_server_group(self):
    wildfly.restart_servers(server_group='A', blocking=True)
    # TODO assert that all servers in group are restarted

    
class ReadLogFileTest(unittest.TestCase):

  global wildfly
    
  def test_log_file(self):

    logs = wildfly.read_log_file()
    self.assertIsNotNone(logs)

    
if __name__ == '__main__':
  unittest.main(verbosity=2)
