import responses
import json
from wildfly.client import Client
from .. import base

try:
    from unittest import mock
except ImportError:
    import mock


class ClientTest(base.BaseTestCase):

	def test_client_init_default(self):
		client = Client("hostname")
		self.assertEqual(client.username, 'admin')
		self.assertEqual(client.password, 'admin')
		self.assertEqual(client.host, "hostname")
		self.assertEqual(client.port, "9990")
		self.assertEqual(client.timeout, 5000)
		self.assertEqual(client.endpoint, 'http://hostname:9990/management')

	@mock.patch.object(Client, 'execute')
	def test_Client(self, mock_execute):
		mock_execute.return_value = 'executed'
		client = Client('hostname')
		client.execute('add')

		self.assertEqual(mock_execute.return_value, client.execute('add'))
		mock_execute.assert_called_with('add')

		client.execute('add', {})
		mock_execute.assert_called_with('add', {})

		client.execute("add", {}, [])
		mock_execute.assert_called_with('add', {}, [])

	@responses.activate
	def test_post_200(self):
		client = Client('host')

		responses.add(responses.POST, client.endpoint, json={}, status=200)
		resp = client._post(json.dumps({}))

		assert resp.status_code == 200
		assert resp.json() == {}
		assert responses.calls[0].request.url == client.endpoint
		assert responses.calls[0].response.text == '{}'

	@mock.patch('requests.Response.raise_for_status')
	@responses.activate
	def test_post_500(self, mock_raise_for_status):
		client = Client('host')
		responses.add(responses.POST, client.endpoint, json={}, status=500)

		client._post('hi')
		assert mock_raise_for_status.called

	@mock.patch('wildfly.client.Client._post')
	def test_execute_operation(self, mock_post):
		client = Client("hostname")

		client.execute("add")
		mock_post.assert_called_with({'operation': 'add', 'address': []})

		client.execute("add", address=['localhost'])
		mock_post.assert_called_with({'operation': 'add', 'address': ['localhost']})

		client.execute("add", parameters={"hello": "world"})
		mock_post.assert_called_with({'operation': 'add', 'hello': 'world', 'address': []})

	@mock.patch('wildfly.client.Client.execute')
	def test_add_address(self, mock_execute):
		client = Client("hostname")

		client.add('address')
		mock_execute.assert_called_with('add', None, 'address')

	@mock.patch('wildfly.client.Client.execute')
	def test_add_address_and_parameters(self, mock_execute):
		client = Client("hostname")
		mock_execute.return_value = 'added'
		response = client.add('address', 'parameters')
		mock_execute.assert_called_with('add', 'parameters', 'address')
		self.assertEqual(response, mock_execute.return_value)

	@mock.patch('wildfly.client.Client.remove')
	def test_remove(self, mock_remove):
		mock_remove.return_value = "removed"

		client = Client('hostname')
		client.remove('address')

		self.assertEqual(mock_remove.return_value, client.remove('address'))
		mock_remove.assert_called_with('address')

	@mock.patch('wildfly.client.Client.execute')
	def test_remove_return_value(self, mock_execute):
		mock_execute.return_value = None
		client = Client("hostname")

		self.assertIsNone(client.remove('address'))

	@mock.patch('wildfly.client.Client.read_resource')
	def test_read_resource(self, mock_read_resource):
		mock_read_resource.return_value = 'resource'

		client = Client('hostname')

		self.assertEqual(mock_read_resource.return_value, client.read_resource('address'))
		mock_read_resource.assert_called_with('address')

	@mock.patch('wildfly.client.Client.execute')
	def test_read_resource_return_value(self, mock_execute):
		mock_execute.return_value = None
		client = Client("hostname")

		self.assertIsNone(client.read_resource('address'))

	@mock.patch('wildfly.client.Client.read_attribute')
	def test_read_attribute(self, mock_read_attribute):
		mock_read_attribute.return_value = 'attribute'
		client = Client('hostname')

		self.assertEqual(mock_read_attribute.return_value, client.read_attribute('attribute_name'))
		mock_read_attribute.assert_called_with('attribute_name')

	@mock.patch('wildfly.client.Client.execute')
	def test_read_attribute_return_none(self, mock_execute):
		mock_execute.return_value = None
		client = Client('hostname')

		self.assertIsNone(client.read_attribute('attribute_name'))

	@mock.patch('wildfly.client.Client.write_attribute')
	def test_write_attribute(self, mock_write_attribute):
		mock_write_attribute.return_value = 'attribute_written'
		client = Client('hostname')

		self.assertEqual(mock_write_attribute.return_value, client.write_attribute('name', 'value'))
		mock_write_attribute.assert_called_with('name', 'value')

	@mock.patch('wildfly.client.Client.execute')
	def test_write_attribute_return_value(self, mock_execute):
		mock_execute.return_value = None

		client = Client('hostname')

		self.assertIsNone(client.write_attribute('name', 'value'))

	@mock.patch('wildfly.client.Client.unset_attribute')
	def test_unset_attribute(self, mock_unset_attribute):
		mock_unset_attribute.return_value = 'unset_attribute'
		client = Client('hostname')

		self.assertEqual(mock_unset_attribute.return_value, client.unset_attribute('name'))
		mock_unset_attribute.assert_called_with('name')

	@mock.patch('wildfly.client.Client.execute')
	def test_unset_attribute_return_none(self, mock_execute):
		mock_execute.return_value = None

		client = Client('hostname')

		self.assertIsNone(client.unset_attribute('name'))

	@mock.patch('wildfly.client.Client.read_children_names')
	def test_read_child_names(self, mock_read_children_names):
		mock_read_children_names.return_value = 'children_name'
		client = Client('hostname')

		self.assertEqual(mock_read_children_names.return_value, client.read_children_names('child_type'))
		mock_read_children_names.assert_called_with('child_type')

	@mock.patch('wildfly.client.Client.execute')
	def test_read_child_names_return_none(self, mock_execute):
		mock_execute.return_value = None

		client = Client('hostname')

		self.assertIsNone(client.read_children_names('child_type'))

	@mock.patch('wildfly.client.Client.read_children_resources')
	def test_read_children_resources(self, mock_read_children_resources):
		mock_read_children_resources.return_value = 'children_resources'
		client = Client('hostname')

		self.assertEqual(mock_read_children_resources.return_value, client.read_children_resources('child_type'))
		mock_read_children_resources.assert_called_with('child_type')

	@mock.patch('wildfly.client.Client.execute')
	def test_read_children_resources_return_none(self, mock_execute):
		mock_execute.return_value = None

		client = Client('hostname')

		self.assertIsNone(client.read_children_resources('child_type'))

	@mock.patch('wildfly.client.Client.read_operation_names')
	def test_read_operation_names(self, mock_read_operation_names):
		mock_read_operation_names.return_value = 'operation_name'
		client = Client("hostname")

		self.assertEqual(mock_read_operation_names.return_value, client.read_operation_names())
		mock_read_operation_names.assert_called_with()

	@mock.patch('wildfly.client.Client.execute')
	def test_read_operation_names_return_none(self, mock_execute):
		mock_execute.return_value = None

		client = Client('hostname')

		self.assertIsNone(client.read_operation_names())

	@mock.patch('wildfly.client.Client.read_operation_description')
	def test_read_operation_description(self, mock_read_operation_description):
		mock_read_operation_description.return_value = 'operation_description'
		client = Client("hostname")

		self.assertEqual(mock_read_operation_description.return_value, client.read_operation_description('operation_name'))
		mock_read_operation_description.assert_called_with('operation_name')

	@mock.patch('wildfly.client.Client.execute')
	def test_read_operation_description_return_none(self, mock_execute):
		mock_execute.return_value = None

		client = Client('hostname')

		self.assertIsNone(client.read_operation_description('operation_name'))

	@mock.patch('wildfly.client.Client.read_children_types')
	def test_read_children_types(self, mock_read_children_types):
		mock_read_children_types.return_value = 'description'
		client = Client("hostname")

		self.assertEqual(mock_read_children_types.return_value, client.read_children_types())
		mock_read_children_types.assert_called_with()

	@mock.patch('wildfly.client.Client.execute')
	def test_read_children_types_return_none(self, mock_execute):
		mock_execute.return_value = None

		client = Client('hostname')

		self.assertIsNone(client.read_children_types())

	@mock.patch('wildfly.client.Client.read_attribute')
	def test_version(self, mock_read_attribute):
		mock_read_attribute.return_value = 'version'
		client = Client('hostname')

		self.assertEqual('version', client.version())