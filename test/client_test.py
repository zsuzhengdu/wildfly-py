import time
import unittest
import requests
import wildfly
import wildfly.util
from wildfly.api.deployment import DEFAULT_SERVER_GROUP
import base


class ConnectionTimeoutTest(unittest.TestCase):

    def setUp(self):
        self.timeout = 0.5
        self.client = wildfly.Client(base.WILDFLY_CONTAINER_NAME, timeout=self.timeout)

    def tearDown(self):
        self.client.close()

    def test_timeout(self):
        start = time.time()
        response = None
        # This call isn't supposed to complete, and it should fail fast.
        try:
            operation = 'read-resource-fake'
            response = self.client.execute(operation=operation)
        except:
            pass
        end = time.time()
        self.assertTrue(response is None)
        self.assertTrue(end - start < 2 * self.timeout)


class VersionTest(base.BaseTestCase):

    def test_version(self):
        try:
            result = self.client.version()
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))
        self.assertEqual(result, base.DEFAULT_WILDFLY_VERSION)


class ExecuteTest(base.BaseTestCase):

    def test_execute_defaults(self):
        operation = 'read-resource'
        response = self.client.execute(operation=operation)
        self.assertTrue(wildfly.util.is_success(response))

    def test_execute_address(self):
        operation = 'read-resource'
        address = [{'server-group': DEFAULT_SERVER_GROUP}]
        response = self.client.execute(operation=operation, address=address)
        self.assertTrue(wildfly.util.is_success(response))

    def test_execute_parms(self):
        operation = 'read-children-resources'
        parameters = {'child-type': 'host', 'include-runtime': 'true'}
        response = self.client.execute(operation=operation, parameters=parameters)
        self.assertTrue(wildfly.util.is_success(response))

    def test_execute_controller_bad_port(self):
        client = wildfly.Client(base.WILDFLY_CONTAINER_NAME, 99990)
        operation = 'read-resource'
        with self.assertRaisesRegexp(requests.ConnectionError, 'Connection refused'):
            client.execute(operation=operation)
        client.close()

    def test_execute_controller_bad_address(self):
        client = wildfly.Client('invalidaddress')
        operation = 'read-resource'
        with self.assertRaisesRegexp(requests.ConnectionError, 'Name or service not known'):
            client.execute(operation=operation)
        client.close()

    @unittest.skip("TOO SLOW")
    def test_execute_controller_down(self):
        base.stop_wildfly_service()
        operation = 'read-resource'
        with self.assertRaisesRegexp(requests.ConnectionError, 'No route to host'):
            self.client.execute(operation=operation)
        base.start_wildfly_service()


class AddTest(base.BaseTestCase):

    def test_add(self):

        address = [{'system-property': 'dummy'}]
        parameters = {'value': 'test'}
        try:
            response = self.client.add(address=address, parameters=parameters)
            self.assertTrue(wildfly.util.is_success(response))
            result = self.client.read_attribute(address=address, name='value')
            self.assertEqual(result, 'test')
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))
        finally:
            self.client.remove(address=address)

    def test_add_exists(self):
        address = [{'system-property': 'dummy'}]
        parameters = {'value': 'test'}
        try:
            response = self.client.add(address, parameters)
            self.assertTrue(wildfly.util.is_success(response))
            result = self.client.read_attribute(address=address, name='value')
            self.assertEqual(result, 'test')
            response = self.client.add(address, parameters)
            self.assertFalse(wildfly.util.is_success(response))
            failure_description = response.json()['failure-description']['domain-failure-description']
            self.assertIn('Duplicate resource', failure_description)
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))
        finally:
            self.client.remove(address)


@unittest.skip("TODO test remove operation")
class RemoveTest(base.BaseTestCase):

    def test_remove(self):
        pass


class ReadResourceTest(base.BaseTestCase):

    def test_read_resource_default(self):
        result = self.client.read_resource()
        self.assertTrue(wildfly.util.is_success(result))

    def test_read_resource(self):
        address = [{'server-group': DEFAULT_SERVER_GROUP}]
        result = self.client.read_resource(address)
        self.assertTrue(wildfly.util.is_success(result))


class ReadAttributeTest(base.BaseTestCase):

    def test_read_attribute(self):
        result = self.client.read_attribute(address=[], name='process-type')
        self.assertEqual(result, 'Domain Controller')


class WriteAttributeTest(base.BaseTestCase):

    def test_write_attribute(self):
        current_value = self.client.read_attribute(address=[], name='name')
        result = self.client.write_attribute(address=[], name='name', value='test')
        result = self.client.read_attribute(address=[], name='name')
        self.assertEqual(result, 'test')
        self.client.write_attribute(address=[], name='name', value=current_value)


class ReadChildrenNamesTest(base.BaseTestCase):

    def test_read_children_names(self):
        result = self.client.read_children_names(address=[], child_type='server-group')
        self.assertIsNotNone(result)
        self.assertIn(DEFAULT_SERVER_GROUP, result)


class ReadChildrenResourcesTest(base.BaseTestCase):

    def test_read_children_resources(self):
        result = self.client.read_children_resources(address=[], child_type='server-group')
        self.assertIsNotNone(result)
        self.assertIn(DEFAULT_SERVER_GROUP, result)
        self.assertEqual(result[DEFAULT_SERVER_GROUP]['deployment'], None)
