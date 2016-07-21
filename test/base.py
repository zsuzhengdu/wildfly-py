import time
import socket
import unittest
import docker
import wildfly

DEFAULT_WILDFLY_VERSION = '8.2.0.Final'
WILDFLY_CONTAINER_NAME = 'wildfly-py-fixture'
UNEXPECTED_EXCEPTION_FORMAT = 'Unexpected Exception: {}.'


def wait_for_wildfly_service():
    retries = 180
    delay = 1
    while retries > 0:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((WILDFLY_CONTAINER_NAME, 9990))
            s.close()
            retries = 0
        except Exception:
            retries -= 1
        if retries > 0:
            time.sleep(delay)


def start_wildfly_service():
    docker_client = docker.Client(base_url='unix://var/run/docker.sock')
    docker_client.start(WILDFLY_CONTAINER_NAME)
    wait_for_wildfly_service()


def stop_wildfly_service():
    docker_client = docker.Client(base_url='unix://var/run/docker.sock')
    docker_client.stop(WILDFLY_CONTAINER_NAME)


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.client = wildfly.Client(WILDFLY_CONTAINER_NAME)

    def tearDown(self):
        self.client.close()
