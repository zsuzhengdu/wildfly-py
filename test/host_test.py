import socket
from . import base
from wildfly.api.deployment import DEFAULT_SERVER_GROUP


class HostTest(base.BaseTestCase):

  def test_list_hosts(self):
    hosts = self.client.hosts()
    self.assertIn(socket.gethostbyname(base.WILDFLY_CONTAINER_NAME), hosts)

  def test_list_hosts_in_group(self):
    hosts = self.client.hosts(server_group=DEFAULT_SERVER_GROUP)
    self.assertIn(socket.gethostbyname(base.WILDFLY_CONTAINER_NAME), hosts)
    
