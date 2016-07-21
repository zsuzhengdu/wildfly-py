# python binding for wildlfy management http/json api

import logging
import json
import requests
from . import util
from . import api


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Client(requests.Session,
             api.HostApiMixin,
             api.ServerApiMixin,
             api.DeploymentApiMixin):

    DEFAULT_MANAGEMENT_PORT = '9990'
    DEFAULT_MANAGEMENT_USER = 'admin'
    DEFAULT_MANAGEMENT_PWD = 'admin'
    DEFAULT_TIMEOUT = 5000

    def __init__(
            self,
            host,
            port=DEFAULT_MANAGEMENT_PORT,
            username=DEFAULT_MANAGEMENT_USER,
            password=DEFAULT_MANAGEMENT_PWD,
            timeout=DEFAULT_TIMEOUT):

        super(Client, self).__init__()
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.endpoint = 'http://{}:{}/management'.format(self.host, self.port)

    def _post(self, request):

        logger.debug('Request: {}'.format(request))
        headers = {'content-type': 'application/json'}
        response = requests.post(
            self.endpoint,
            headers=headers,
            auth=requests.auth.HTTPDigestAuth(
                self.username,
                self.password),
            data=json.dumps(request))
        if response.status_code in [200, 204]:
            logger.debug(
                'Response Status Code: {}: {}'.format(
                    response.status_code,
                    response.reason))
        elif response.status_code == 500:
            logger.debug(
                'Response Status Code: {}: {}'.format(
                    response.status_code,
                    response.json()))
        else:
            response.raise_for_status()
        logger.debug('Response: {}'.format(response.json()))
        return response

    def execute(self, operation, parameters={}, address=[]):
        """ Execute operation on resource. """

        request = {'address': address, 'operation': operation}
        request.update(parameters)
        response = self._post(request)
        return response

    def add(self, address, parameters=None):
        """ Creates a new management resource. """

        response = self.execute('add', parameters, address)
        return response

    def remove(self, address):
        """ Removes an existing resource. """

        response = self.execute('remove', address=address)
        return response

    def read_resource(
            self,
            address=[],
            recursive=False,
            recursive_depth=10,
            runtime=False,
            include_defaults=True,
            attributes_only=False):
        """ Reads a resource's attribute values along with either
            basic or complete information about any child resources. """

        response = self.execute('read-resource',
                                {'recursive': recursive,
                                 'recursive_depth': recursive_depth,
                                 'runtime': runtime,
                                 'include_defaults': include_defaults,
                                 'attributes_only': attributes_only},
                                address)
        return response

    def read_attribute(self, name, address=[], include_defaults=True):
        """ Read attribute of resource. """

        response = self.execute('read-attribute',
                                {'name': name,
                                 'include-defaults': include_defaults},
                                address)
        return response.json()['result']

    def write_attribute(self, name, value, address=[]):
        """ Write value of attribute of resource. """

        response = self.execute('write-attribute',
                                {'name': name, 'value': value},
                                address)
        return response

    def unset_attribute(self, name, address=[]):
        """ Sets the value of an individual attribute to the undefined
        value. """

        response = self.execute('unset-attribute',
                                {'name': name},
                                address)
        return response.json()['result']

    def read_children_names(self, child_type, address=[]):
        """ Returns a list of the names of all child resources of a
        given type. """

        response = self.execute('read-children-names',
                                {'child-type': child_type},
                                address)
        if util.is_success(response):
            return response.json()['result']
        return None

    def read_children_resources(self, child_type, address=[], runtime=False):
        """ Returns a list of the resources of all child resources of a
        given type. """

        response = self.execute('read-children-resources',
                                {'child-type': child_type,
                                 'include-runtime': runtime},
                                address)
        logger.debug(response.json())
        if util.is_success(response):
            return response.json()['result']
        return None

    def read_operation_names(self, address=[]):
        """ Returns a list of the names of all the operations the resource
        supports. """

        response = self.execute('read-operation-names',
                                address)
        if util.is_success(response):
            return response.json()['result']
        return None

    def read_operation_description(self, name, address=[]):
        """ Returns the description of an operation, along with details of """
        """ its parameter types and its return value. """

        response = self.execute('read-operation-description',
                                {'name': name},
                                address)
        if util.is_success(response):
            return response.json()['result']
        return None

    def read_children_types(self, address=[]):
        """ Returns a list of the types of child resources the resource
        supports. """

        response = self.execute('read-children-types',
                                address)
        if util.is_success(response):
            return response.json()['result']
        return None

    def version(self):
        """ Prints version of WildFly. """

        result = self.read_attribute('release-version')
        return result
