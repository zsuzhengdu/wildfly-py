import os
import errno
import unittest
import logging
import requests
import wildfly.util
from wildfly.api.deployment import DEFAULT_SERVER_GROUP
from . import base


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEFAULT_NEXUS_HOST = 'nexus'
DEFAULT_NEXUS_PORT = '8081'
DEFAULT_GROUP_ID = 'com'
DEFAULT_ARTIFACT_ID = 'project'
DEFAULT_ARTIFACT_VERSION = '1.0'
DEFAULT_ARTIFACT_TYPE = 'jar'
DEFAULT_DEPLOYMENT_NAME = '{}-{}.{}'.format(
    DEFAULT_ARTIFACT_ID,
    DEFAULT_ARTIFACT_VERSION,
    DEFAULT_ARTIFACT_TYPE)


class DeploymentTest(base.BaseTestCase):

    def test_deployments_with_opitions(self):
        try:
            self.client.deploy(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION,
                type='jar'
            )
            deployments = self.client.deployments(
                server_group=DEFAULT_SERVER_GROUP)
            for key in deployments.keys():
                self.assertIn(
                    DEFAULT_SERVER_GROUP,
                    deployments[key]['server-groups'])
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))
        finally:
            self.client.undeploy(DEFAULT_DEPLOYMENT_NAME)

    # TODO: ADD Test to cover option: host. Currently, host name is docker
    # instance ip in fixture setup.

    def test_list_deployments(self):
        try:
            self.client.deploy(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION,
                type='jar'
            )
            deployments = self.client.deployments()
            self.assertIn(DEFAULT_DEPLOYMENT_NAME, deployments)
            self.assertTrue(
                self.client.is_deployment_enabled(DEFAULT_DEPLOYMENT_NAME))
            self.assertEqual(self.client.deployment_status(
                DEFAULT_DEPLOYMENT_NAME), 'RUNNING')
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))
        finally:
            self.client.undeploy(DEFAULT_DEPLOYMENT_NAME)

    def test_list_deployments_disabled(self):
        try:
            self.client.deploy(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION,
                type='jar',
                enabled=False
            )
            deployments = self.client.deployments()
            self.assertIn(DEFAULT_DEPLOYMENT_NAME, deployments)
            self.assertFalse(
                self.client.is_deployment_enabled(DEFAULT_DEPLOYMENT_NAME))
            self.assertEqual(self.client.deployment_status(
                DEFAULT_DEPLOYMENT_NAME), 'STOPPED')
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))
        finally:
            self.client.undeploy(DEFAULT_DEPLOYMENT_NAME)

    def test_list_deployments_server_down(self):
        try:
            self.client.stop_servers(blocking=True)
            self.client.deploy(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION,
                type='jar'
            )
            deployments = self.client.deployments()
            self.assertIn(DEFAULT_DEPLOYMENT_NAME, deployments)
            self.assertTrue(deployments[DEFAULT_DEPLOYMENT_NAME]['enabled'])
            self.assertEqual(
                deployments[DEFAULT_DEPLOYMENT_NAME]['status'],
                'STOPPED')
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))
        finally:
            self.client.undeploy(DEFAULT_DEPLOYMENT_NAME)
            self.client.start_servers(blocking=True)

    def test_list_deployments_in_group(self):
        try:
            self.client.deploy(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION,
                type='jar'
            )
            deployments = self.client.deployments(
                server_group=DEFAULT_SERVER_GROUP)
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))
        finally:
            self.client.undeploy(DEFAULT_DEPLOYMENT_NAME)
        self.assertIn(DEFAULT_DEPLOYMENT_NAME, deployments)

    def test_is_deployment_in_repository(self):
        try:
            self.client.deploy(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION)
            result = self.client.is_deployment_in_repository(
                DEFAULT_DEPLOYMENT_NAME)
            self.assertTrue(result)
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))
        finally:
            self.client.undeploy(DEFAULT_DEPLOYMENT_NAME)

    def test_is_deployment_not_in_repository(self):
        try:
            result = self.client.is_deployment_in_repository(
                DEFAULT_DEPLOYMENT_NAME)
            self.assertFalse(result)
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))

    def test_is_deployment_enabled(self):
        try:
            self.client.deploy(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION)
            result = self.client.is_deployment_enabled(DEFAULT_DEPLOYMENT_NAME)
            self.assertTrue(result)
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))
        finally:
            self.client.undeploy(DEFAULT_DEPLOYMENT_NAME)


class PullTest(base.BaseTestCase):

    def test_pull(self):
        try:
            self.client.pull(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION,
                type='jar')
            deployments = self.client.deployments()
            self.assertIn(DEFAULT_DEPLOYMENT_NAME, deployments)
            self.assertFalse(deployments[DEFAULT_DEPLOYMENT_NAME]['enabled'])
            self.assertEqual(
                deployments[DEFAULT_DEPLOYMENT_NAME]['status'],
                'STOPPED')
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))
        finally:
            self.client.undeploy(DEFAULT_DEPLOYMENT_NAME)


class DeployTest(base.BaseTestCase):

    def test_deploy_url(self):

        try:
            self.client.deploy(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION)
            deployments = self.client.deployments()
            self.assertIn(DEFAULT_DEPLOYMENT_NAME, deployments)
            self.assertTrue(deployments[DEFAULT_DEPLOYMENT_NAME]['enabled'])
            self.assertEqual(
                deployments[DEFAULT_DEPLOYMENT_NAME]['status'],
                'RUNNING')
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))
        finally:
            self.client.undeploy(DEFAULT_DEPLOYMENT_NAME)

    def test_deploy_file(self):

        NEXUS_BASE_URL = 'http://{}:{}/nexus' \
                         '/service/local/repo_groups/public/content'\
            .format(DEFAULT_NEXUS_HOST, DEFAULT_NEXUS_PORT)

        url = '{0}/{1}/{2}/{3}/{2}-{3}.{4}'.format(
            NEXUS_BASE_URL,
            DEFAULT_GROUP_ID.replace(
                '.',
                '/'),
            DEFAULT_ARTIFACT_ID,
            DEFAULT_ARTIFACT_VERSION,
            DEFAULT_ARTIFACT_TYPE)
        response = requests.get(url)

        if response.status_code not in [200, 204]:
            print(
                'Response Status Code: {}: {}'.format(
                    response.status_code,
                    response.reason))
            response.raise_for_status()

        filename = '{}-{}.{}'.format(DEFAULT_ARTIFACT_ID,
                                     DEFAULT_ARTIFACT_VERSION,
                                     DEFAULT_ARTIFACT_TYPE)

        with open(filename, "wb") as artifact:
            artifact.write(response.content)

        try:
            self.client.deploy(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION,
                path=filename)
            deployments = self.client.deployments()
            logger.debug('DEPLOYMENTS: {}'.format(deployments))
            self.assertIn(DEFAULT_DEPLOYMENT_NAME, deployments)
            self.assertTrue(deployments[DEFAULT_DEPLOYMENT_NAME]['enabled'])
            self.assertEqual(
                deployments[DEFAULT_DEPLOYMENT_NAME]['status'],
                'RUNNING')
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))
        finally:
            self.client.undeploy(DEFAULT_DEPLOYMENT_NAME)

        os.remove(filename)

    def test_deploy_file_not_exist(self):

        with self.assertRaises(IOError) as cm:
            self.client.deploy(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION,
                path='no-file-at-path')
        exception = cm.exception
        self.assertEqual(exception.errno, errno.ENOENT)
        self.assertEqual(exception.strerror, os.strerror(exception.errno))

    def test_deploy_url_not_exist(self):

        with self.assertRaisesRegexp(requests.exceptions.HTTPError,
                                     "Not Found for url"):
            self.client.deploy('fake', 'fake', 'fake')

    @unittest.skip("still working on this one")
    def test_redeploy_url(self):

        pass
        try:
            self.client.deploy(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION)
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))

        result = self.client.read_attribute(
            'enabled',
            [{'server-group': DEFAULT_SERVER_GROUP},
             {'deployment': DEFAULT_DEPLOYMENT_NAME}])

        self.assertTrue(result)

        try:
            self.client.deploy(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION)
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))

        result = self.client.read_attribute(
            'enabled',
            [{'server-group': DEFAULT_SERVER_GROUP},
             {'deployment': DEFAULT_DEPLOYMENT_NAME}])

        self.assertTrue(result)
        self.client.undeploy(DEFAULT_DEPLOYMENT_NAME)


class UndeployTest(base.BaseTestCase):

    def test_undeploy(self):

        try:
            self.client.deploy(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION)
            self.client.undeploy(DEFAULT_DEPLOYMENT_NAME)
            deployments = self.client.deployments()
            self.assertNotIn(DEFAULT_DEPLOYMENT_NAME, deployments)
        except Exception as e:
            self.fail(base.UNEXPECTED_EXCEPTION_FORMAT.format(e))

    def test_undeploy_not_deployed(self):

        response = self.client.undeploy(DEFAULT_DEPLOYMENT_NAME)
        self.assertFalse(wildfly.util.is_success(response))
        failure_description = response.json(
        )['failure-description']['domain-failure-description']
        self.assertIn('not found', failure_description)


class EnableDisableTest(base.BaseTestCase):

    def test_enable(self):
        try:
            self.client.pull(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION,
                type='jar')
            self.client.enable(DEFAULT_DEPLOYMENT_NAME, DEFAULT_SERVER_GROUP)
            self.assertTrue(
                self.client.is_deployment_enabled(DEFAULT_DEPLOYMENT_NAME))
        finally:
            self.client.undeploy(DEFAULT_DEPLOYMENT_NAME)

    def test_disable(self):
        try:
            self.client.deploy(
                DEFAULT_GROUP_ID,
                DEFAULT_ARTIFACT_ID,
                DEFAULT_ARTIFACT_VERSION)
            self.client.disable(DEFAULT_DEPLOYMENT_NAME, DEFAULT_SERVER_GROUP)
            self.assertFalse(
                self.client.is_deployment_enabled(DEFAULT_DEPLOYMENT_NAME))
        finally:
            self.client.undeploy(DEFAULT_DEPLOYMENT_NAME)