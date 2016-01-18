import socket
from . import base
from wildfly.api.deployment import DEFAULT_SERVER_GROUP


class ServerTest(base.BaseTestCase):

  def test_list_servers(self):
    servers = self.client.servers()
    self.assertIn('{}-0'.format(socket.gethostbyname(base.WILDFLY_CONTAINER_NAME)), servers)

  def test_list_servers_in_group(self):
    servers = self.client.servers(server_group=DEFAULT_SERVER_GROUP)
    self.assertIn('{}-0'.format(socket.gethostbyname(base.WILDFLY_CONTAINER_NAME)), servers)
    
    
class StartServersTest(base.BaseTestCase):
  
  def test_start_servers(self):
    self.client.start_servers(blocking=True)
    servers = self.client.servers()
    for key in servers:
      self.assertEqual(servers[key]['status'], 'running')
    
  def test_start_server_group(self):
    self.client.start_servers(server_group=DEFAULT_SERVER_GROUP, blocking=True)
    servers = self.client.servers(server_group=DEFAULT_SERVER_GROUP)
    for key in servers:
      self.assertEqual(servers[key]['status'], 'running')

    
class StopServersTest(base.BaseTestCase):

  def test_stop_servers(self):
    self.client.stop_servers(blocking=True)
    servers = self.client.servers()
    for key in servers:
      self.assertEqual(servers[key]['status'], 'STOPPED')
    self.client.start_servers(blocking=True)

  def test_stop_server_group(self):
    self.client.stop_servers(server_group=DEFAULT_SERVER_GROUP, blocking=True)
    servers = self.client.servers(server_group=DEFAULT_SERVER_GROUP)
    for key in servers:
      self.assertEqual(servers[key]['status'], 'STOPPED')
    self.client.start_servers(server_group=DEFAULT_SERVER_GROUP, blocking=True)

    
class ReloadServersTest(base.BaseTestCase):

  def test_reload_servers(self):
    self.client.reload_servers(blocking=True)
    servers = self.client.servers()
    for key in servers:
      self.assertEqual(servers[key]['status'], 'running')

  def test_reload_server_group(self):
    self.client.reload_servers(server_group=DEFAULT_SERVER_GROUP, blocking=True)
    servers = self.client.servers(server_group=DEFAULT_SERVER_GROUP)
    for key in servers:
      self.assertEqual(servers[key]['status'], 'running')

      
class RestartServersTest(base.BaseTestCase):

  def test_restart_servers(self):
    self.client.restart_servers(blocking=True)
    servers = self.client.servers()
    for key in servers:
      self.assertEqual(servers[key]['status'], 'running')
      self.assertLess(servers[key]['uptime'], 15000)

  def test_restart_server_group(self):
    self.client.restart_servers(server_group=DEFAULT_SERVER_GROUP, blocking=True)
    servers = self.client.servers(server_group=DEFAULT_SERVER_GROUP)
    for key in servers:
      self.assertEqual(servers[key]['status'], 'running')
      self.assertLess(servers[key]['uptime'], 15000)

    
class ReadLogFileTest(base.BaseTestCase):

  def test_log_file(self):

    logs = self.client.read_log_file()
    self.assertIsNotNone(logs)
