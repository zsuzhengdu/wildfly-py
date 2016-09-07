import responses
import requests
import urllib
from wildfly.client import Client
from .. import base

try:
    from unittest import mock
except ImportError:
    import mock


class DeploymentApiMixinTest(base.BaseTestCase):

	@mock.patch('wildfly.client.Client.read_children_resources')
	@mock.patch('wildfly.api.server.ServerApiMixin.server_groups')
	@mock.patch('wildfly.api.server.ServerApiMixin.servers')
	def test_deployments(self, mock_servers, mock_server_groups, mock_read_children_resources):
		def my_side_effect(*args, **kwargs):
			if args[0] == 'deployment' and len(args) == 1:
				return {'application': {'content': [{'hash': {'BYTES_VALUE': 'hash'}}],
										'runtime-name': 'runtime_name',
										'name': 'name'}}
			else:
				return {u'application': {u'status': u'OK',
										 u'subsystem': {u'undertow': None},
										 u'name': u'name',
										 u'enabled': True,
										 u'persistent': True,
										 u'content': [{u'hash': {u'BYTES_VALUE': u'hash'}}],
										 u'runtime-name': u'runtime_name',
										 u'subdeployment': None}}

		mock_servers.return_value = {'server': {'status': 'running', 'host': 'hostname', 'group': 'group', 'uptime': 123}}
		mock_server_groups.return_value  = {'server_group': {u'profile': u'full-ha',
		                                                     u'socket-binding-group': u'full-ha-sockets',
		                                                     u'deployment-overlay': None,
		                                                     u'socket-binding-port-offset': 0,
		                                                     u'jvm': None,
		                                                     u'deployment': {u'application': None},
		                                                     u'system-property': None,
		                                                     u'management-subsystem-endpoint': False}}

		mock_read_children_resources.side_effect = my_side_effect

		client = Client('hostname')

		self.assertEqual('RUNNING', client.deployments('server_group', 'hostname')['application']['status'])

		self.assertDictEqual({}, client.deployments(server_group='server_group_not_exist', host=None))


	@mock.patch('wildfly.api.deployment.DeploymentApiMixin.deployments')
	def test_is_deployment_in_repository(self, mock_deployments):
		mock_deployments.return_value = {'name': 'artifact'}
		client = Client('hostname')

		self.assertTrue(client.is_deployment_in_repository('name'))

	@mock.patch('wildfly.api.deployment.DeploymentApiMixin.deployments')
	def test_is_deployment_enabled(self, mock_deployments):
		mock_deployments.return_value = {'name': {'enabled': True}}
		client = Client('hostname')

		self.assertTrue(client.is_deployment_enabled('name'))

	@mock.patch('wildfly.api.deployment.DeploymentApiMixin.deployments')
	def test_deployment_status(self, mock_deployments):
		mock_deployments.return_value = {'name': {'status': 'running'}}
		client = Client('hostname')

		self.assertEqual('running', client.deployment_status('name'))

	@mock.patch('wildfly.api.deployment.DeploymentApiMixin.deploy')
	def test_pull(self, mock_deploy):
		mock_deploy.return_value = True
		client = Client('hostname')
		client.pull('groupId', 'artifactId', 'version', 'war', 'A', None, 'content_host', 'endpoint', 'port')

		mock_deploy.assert_called_with('groupId', 'artifactId', 'version', 'war', 'A', None, content_host='content_host', content_host_ep='endpoint', content_host_port='port', enabled=False)


	@mock.patch('__builtin__.open', spec=open)
	@mock.patch('wildfly.api.deployment.os.path.isfile')
	@responses.activate
	def test_deploy(self, mock_isfile, mock_open):
		mock_isfile.return_value = True
		mock_open.return_value = 'file_content'


		# path is None, end_point is nexus and snapshot
		groupId = 'group_id'
		artifactId = 'artifact_id'
		type = 'war'
		server_groups = 'server_groups'
		path = None
		enabled = True
		force = True
		content_host = 'content_host'
		content_host_ep = 'nexus'
		content_host_port = 8081
		scheme='http'


		client = Client('hostname')


		# path is None, end_point is nexus and non-snapshot
		version = 'version'
		BASE_URL = '{}://{}:{}/{}/service/local/repo_groups' \
		           '/public/content'.format(scheme,
		                                    content_host,
		                                    content_host_port,
		                                    content_host_ep)

		url = '{0}/{1}/{2}/{3}/{2}-{3}.{4}'.format(
			BASE_URL,
			groupId.replace('.', '/'),
			artifactId,
			version,
			type
		)

		responses.add(responses.POST, 'http://hostname:9990/management', json={"result": {'BYTES_VALUE': 'asdf'}}, status=200)
		responses.add(responses.HEAD, url, json={"uploaed": True}, status=200)
		client.deploy(groupId, artifactId, version, type, server_groups, path, enabled, force, content_host,
		              content_host_ep, content_host_port)


		version = 'version-SNAPSHOT'

		BASE_URL = '{}://{}:{}/{}/service/local/artifact' \
		           '/maven/content?r=public'.format(scheme,
		                                            content_host,
		                                            content_host_port,
		                                            content_host_ep)

		url = '{0}&g={1}&a={2}&v={3}&p={4}'.format(
			BASE_URL,
			groupId.replace('.', '/'),
			artifactId,
			version,
			type
		)

		responses.add(responses.HEAD, url, json={"uploaed": True}, status=200)

		# client.deploy(groupId, artifactId, version, type, server_groups, path, enabled, force, content_host,
		#               content_host_ep, content_host_port)


		# path is None, end_point is maven2
		content_host_ep = 'maven2'
		BASE_URL = '{}://{}:{}/{}'.format(scheme,
		                                  content_host,
		                                  content_host_port,
		                                  content_host_ep)
		url = '{0}/{1}/{2}/{3}/{2}-{3}.{4}'.format(
			BASE_URL,
			groupId.replace('.', '/'),
			artifactId,
			version,
			type)

		responses.add(responses.HEAD, url, json={"uploaed": True}, status=200)
		client.deploy(groupId, artifactId, version, type, server_groups, path, enabled, force, content_host,
		              content_host_ep, content_host_port)

		# path is None, end_pint is None
		content_host_ep = None
		BASE_URL = '{}://{}:{}/service/local/repositories/releases/content'.format(scheme,
		                                                                           content_host,
		                                                                           content_host_port)
		url = '{0}/{1}/{2}/{3}/{2}-{3}.{4}'.format(
			BASE_URL,
			groupId.replace('.', '/'),
			artifactId,
			version,
			type
		)

		responses.add(responses.HEAD, url, json={"uploaed": True}, status=200)
		client.deploy(groupId, artifactId, version, type, server_groups, path, enabled, force, content_host,
		              content_host_ep, content_host_port)

		type = 'jar'
		url = '{0}/{1}/{2}/{3}/{2}-{3}.{4}'.format(
			BASE_URL,
			groupId.replace('.', '/'),
			artifactId,
			version,
			type
		)
		responses.add(responses.HEAD, url, json={"uploaed": True}, status=200)
		client.deploy(groupId, artifactId, version, type, server_groups, path, enabled, force, content_host,
		              content_host_ep, content_host_port)

		# path is not None
		path = 'path'

		# path not exist exception catching
		url = client.endpoint + '/add-content'
		responses.add(responses.POST, url, json={"result": {'BYTES_VALUE': 'asdf'}}, status=200)
		client.deploy(groupId, artifactId, version, type, server_groups, path, enabled, force, content_host,
		              content_host_ep, content_host_port)



	@responses.activate
	def test_disalbe_success(self):
		client = Client('hostname')
		responses.add(responses.POST, client.endpoint, json={"outcome": "success"}, status=200)
		client.disable('name', 'server_group')

	@responses.activate
	def test_disalbe_fail(self):
		client = Client('hostname')
		responses.add(responses.POST, client.endpoint, json={"outcome": "fail"}, status=300)
		client.disable('name', 'server_group')

	@responses.activate
	def test_enable_success(self):
		client = Client('hostname')
		responses.add(responses.POST, client.endpoint, json={"outcome": "success"}, status=200)
		client.enable('name', 'server_group')

	@responses.activate
	def test_enable_fail(self):
		client = Client('hostname')
		responses.add(responses.POST, client.endpoint, json={"outcome": "fail"}, status=300)
		client.enable('name', 'server_group')

	@responses.activate
	def test_undeploy_success(self):
		client = Client('hostname')
		responses.add(responses.POST, client.endpoint, json={"outcome": "success"}, status=200)
		reps = client.undeploy("name", "A")

		assert reps.json() == {"outcome": "success"}