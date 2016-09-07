from wildfly.client import Client
from .. import base

try:
    from unittest import mock
except ImportError:
    import mock


class HostApiMixinTest(base.BaseTestCase):

	@mock.patch('wildfly.client.Client.read_children_names')
	def test_hosts(self, mock_read_children_names):
		mock_read_children_names.return_value = 'hosts'
		client = Client('hostname')
		self.assertEqual('hosts',  client.hosts())
		mock_read_children_names.assert_called_with('host')



