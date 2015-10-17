#!/usr/bin/env python

import os
import unittest
from wildfly import Wildfly


def suite():
  suite = unittest.TestSuite()
  suite.addTest(PullTest('test_pull'))
  return suite


def create_wildfly_service(mode='domain'):
  # use docker-py to create wildfly service fixture
  pass

  
def remove_wildfly_service(mode='domain'):
  # use docker-py to remove wildfly service fixture
  pass


def setUpModule():
  create_wildfly_service()
  

def tearDownModule():
  remove_wildfly_service()

  
class VersionTest(unittest.TestCase):

  wildfly = None
  
  def setUp(self):

    wildfly_host = os.environ['DOCKER_HOST'].split(':')[1].replace('//', '')
    self.wildfly = Wildfly(wildfly_host)
    
  def tearDownM(self):

    self.wildfly.disconnect()

  def test_version(self):

    try:
      result = self.wildfly.version()
    except Exception as e:
      self.fail('version raised exception unexpectedly! Exception: {}.'.format(e))
    self.assertEqual(result, '8.2.0.Final')


class PullTest(unittest.TestCase):

  wildfly = None
    
  def setUp(self):

    wildfly_host = os.environ['DOCKER_HOST'].split(':')[1].replace('//', '')
    self.wildfly = Wildfly(wildfly_host)
    
  def tearDownM(self):

    self.wildfly.disconnect()

  def test_pull(self):

    self.wildlfly.deploy('cenx', 'apollo', '1.0.0', 'A')

    
class DeployTest(unittest.TestCase):

  wildfly = None
    
  def setUp(self):

    wildfly_host = os.environ['DOCKER_HOST'].split(':')[1].replace('//', '')
    self.wildfly = Wildfly(wildfly_host)
    
  def tearDownM(self):

    self.wildfly.disconnect()

  def test_deploy_url(self):

    self.wildfly.deploy('org.jboss.mod_cluster', 'mod_cluster-demo-server',
                        '1.2.6.Final', 'war', 'A', 'thirdparty')
    self.wildfly.undeploy('mod_cluster-demo-server')

  def test_deploy_file(self):

    self.wildfly.deploy('org.jboss.mod_cluster', 'mod_cluster-demo-server',
                        '1.2.6.Final', 'war', 'A', 'thirdparty', path='/transport/x.war')
    self.wildfly.undeploy('mod_cluster-demo-server')

    
class UndeployTest(unittest.TestCase):

  wildfly = None
    
  def setUp(self):

    wildfly_host = os.environ['DOCKER_HOST'].split(':')[1].replace('//', '')
    self.wildfly = Wildfly(wildfly_host)
    
  def tearDownM(self):

    self.wildfly.disconnect()

  def test_undeploy(self):

    self.wildfly.deploy('org.jboss.mod_cluster', 'mod_cluster-demo-server',
                        '1.2.6.Final', 'war', 'A', 'thirdparty')
    self.wildfly.undeploy('mod_cluster-demo-server')


class DeploymentInfoTest(unittest.TestCase):

  wildfly = None
    
  def setUp(self):
    wildfly_host = os.environ['DOCKER_HOST'].split(':')[1].replace('//', '')
    self.wildfly = Wildfly(wildfly_host)
    self.wildfly.deploy('org.jboss.mod_cluster', 'mod_cluster-demo-server',
                        '1.2.6.Final', 'A', 'thirdparty')

  def tearDownM(self):
    self.wildfly.undeploy('mod_cluster-demo-server')
    self.wildfly.disconnect()
    
  def test_deployment_info(self):

    info = self.wildfly.deployment_info()
    expected = {'mod_cluster-demo-server.war': {'runtime-name': 'mod_cluster-demo-server.war'}}
    self.assertEqual(info, expected)
    
    
class ExecuteTest(unittest.TestCase):

  wildfly = None
    
  def setUp(self):
    wildfly_host = os.environ['DOCKER_HOST'].split(':')[1].replace('//', '')
    self.wildfly = Wildfly(wildfly_host)
    
  def tearDownM(self):
    self.wildfly.disconnect()

  def test_execute_parms(self):
    operation = 'read-children-resources'
    parameters = {'child-type': 'host', 'include-runtime': 'true'}
    self.wildfly.execute(operation=operation, parameters=parameters)

  def test_execute_defaults(self):
    operation = 'read-resource'
    self.wildfly.execute(operation=operation)

  def test_execute_address(self):
    operation = 'read-resource'
    address = [{'server-group': 'A'}]
    self.wildfly.execute(operation=operation, address=address)
    
    
class StartServersTest(unittest.TestCase):

  wildfly = None
    
  def setUp(self):
    wildfly_host = os.environ['DOCKER_HOST'].split(':')[1].replace('//', '')
    self.wildfly = Wildfly(wildfly_host)
    
  def tearDownM(self):
    self.wildfly.disconnect()

  def test_start_servers(self):
    self.wildfly.start_servers(blocking=True)
    # self.wildfly.server_info()
    # TODO assert that all servers are started
    # /host=172.17.0.72/server=172.17.0.72-0:read-attribute(name=server-state) = running
    
  def test_start_server_group(self):
    self.wildfly.start_servers(server_group='A', blocking=True)
    # TODO assert that servers in group started

    
class StopServersTest(unittest.TestCase):

  wildfly = None
    
  def setUp(self):
    wildfly_host = os.environ['DOCKER_HOST'].split(':')[1].replace('//', '')
    self.wildfly = Wildfly(wildfly_host)
    
  def tearDownM(self):
    self.wildfly.disconnect()

  def test_stop_servers(self):
    self.wildfly.stop_servers(blocking=True)
    # TODO assert that all servers are stopped
    self.wildfly.execute('read-children-resources',
                         {'child-type': 'host', 'include-runtime': 'true'})
    # /:read-children-resources(child-type=host, include-runtime=true)
    # /host=172.17.0.72:read-children-resources(child-type=server, include-runtime=true)
    # /host=172.17.0.72/server=172.17.0.72-0:read-attribute(name=server-state) = STOPPED
    # /host=172.17.0.72:read-children-resources(child-type=server-config, include-runtime=true)
    # /host=172.17.0.72/server-config=172.17.0.72-0:read-attribute(name=status) = STOPPED
    # /host=172.17.0.72/server-config=172.17.0.72-0:read-attribute(name=group)
    self.wildfly.start_servers(blocking=True)

  def test_stop_server_group(self):
    self.wildfly.stop_servers(server_group='A', blocking=True)
    # TODO assert that all servers are stopped
    self.wildfly.start_servers(server_group='A', blocking=True)

    
class ReloadServersTest(unittest.TestCase):

  wildfly = None
    
  def setUp(self):
    wildfly_host = os.environ['DOCKER_HOST'].split(':')[1].replace('//', '')
    self.wildfly = Wildfly(wildfly_host)
    
  def tearDownM(self):
    self.wildfly.disconnect()

  def test_reload_servers(self):
    self.wildfly.reload_servers(blocking=True)
    # TODO assert that all servers are reloaded

  def test_reload_server_group(self):
    self.wildfly.reload_servers(server_group='A', blocking=True)
    # TODO assert that all servers are reloaded

    
class RestartServersTest(unittest.TestCase):

  wildfly = None
    
  def setUp(self):
    wildfly_host = os.environ['DOCKER_HOST'].split(':')[1].replace('//', '')
    self.wildfly = Wildfly(wildfly_host)
    
  def tearDownM(self):
    self.wildfly.disconnect()

  def test_restart_servers(self):
    self.wildfly.restart_servers(blocking=True)
    # TODO assert that all servers are restarted

  def test_restart_server_group(self):
    self.wildfly.restart_servers(server_group='A', blocking=True)
    # TODO assert that all servers in group are restarted

    
class ReadLogFileTest(unittest.TestCase):

  wildfly = None
    
  def setUp(self):
    wildfly_host = os.environ['DOCKER_HOST'].split(':')[1].replace('//', '')
    self.wildfly = Wildfly(wildfly_host)
    
  def tearDownM(self):
    self.wildfly.disconnect()

  def test_log_file(self):

    logs = self.wildfly.read_log_file()
    self.assertIsNotNone(logs)

    
if __name__ == '__main__':
  unittest.main()
