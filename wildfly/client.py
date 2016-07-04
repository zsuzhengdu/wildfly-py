# python binding for wildlfy management http/json api

import logging
import json
import requests
from . import util
from . import api

log_format = '%(asctime)s | %(levelname)7s | %(name)s | line:%(lineno)4s | %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)

logger = logging.getLogger(__name__)

# Define some
KEY_OUTCOME = "outcome"
KEY_RESULT = "result"


class Client(requests.Session,
             api.HostApiMixin,
             api.ServerApiMixin,
             api.DeploymentApiMixin):

    DEFAULT_MANAGEMENT_PORT = '9990'
    DEFAULT_MANAGEMENT_USER = 'admin'
    DEFAULT_MANAGEMENT_PWD = 'admin'
    DEFAULT_TIMEOUT = 5000

    def __init__(self, host, port=DEFAULT_MANAGEMENT_PORT,
                 username=DEFAULT_MANAGEMENT_USER, password=DEFAULT_MANAGEMENT_PWD,
                 timeout=DEFAULT_TIMEOUT):
        """
        Creates an object that interacts with WildFly via HTTP request
        :param  hostname  The hostname of the WildFly domain controller
        :param  port      The port used to access the WildFly UI
        :param  username  The WildFly username
        :param  password  The WildFly username's password
        :param  timeout   The timeout
        """
        super(Client, self).__init__()
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.endpoint = 'http://{}:{}/management'.format(self.host, self.port)
        self._hostname_map = self._get_hostname_map()

    def _post(self, request):

        logger.debug('Request: {}'.format(request))
        headers = {'content-type': 'application/json'}
        response = requests.post(self.endpoint, headers=headers,
                                 auth=requests.auth.HTTPDigestAuth(self.username, self.password),
                                 data=json.dumps(request))
        if response.status_code in [200, 204]:
            logger.debug('Response Status Code: {}: {}'.format(response.status_code, response.reason))
        elif response.status_code == 500:
            logger.debug('Response Status Code: {}: {}'.format(response.status_code, response.json()))
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

    def read_resource(self, address=[], recursive=False, recursive_depth=10,
                      runtime=False, include_defaults=True, attributes_only=False):
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
                                {'name': name, 'include-defaults': include_defaults},
                                address)
        return response.json()['result'] if util.is_success(response) else None

    def write_attribute(self, name, value, address=[]):
        """ Write value of attribute of resource. """

        response = self.execute('write-attribute',
                                {'name': name, 'value': value},
                                address)
        return response

    def unset_attribute(self, name, address=[]):
        """ Sets the value of an individual attribute to the undefined value. """

        response = self.execute('unset-attribute',
                                {'name': name},
                                address)
        response = response.json()
        return response.json()['result'] if util.is_success(response) else None

    def read_children_names(self, child_type, address=[]):
        """ Returns a list of the names of all child resources of a given type. """

        response = self.execute('read-children-names',
                                {'child-type': child_type},
                                address)
        return response.json()['result'] if util.is_success(response) else None

    def read_children_resources(self, child_type, address=[], runtime=False):
        """ Returns a list of the resources of all child resources of a given type. """

        response = self.execute('read-children-resources',
                                {'child-type': child_type, 'include-runtime': runtime},
                                address)
        logger.debug(response.json())
        return response.json()['result'] if util.is_success(response) else None

    def read_operation_names(self, address=[]):
        """ Returns a list of the names of all the operations the resource supports. """

        response = self.execute('read-operation-names',
                                address)
        return response.json()['result'] if util.is_success(response) else None

    def read_operation_description(self, name, address=[]):
        """ Returns the description of an operation, along with details of
        its parameter types and its return value. """

        response = self.execute('read-operation-description',
                                {'name': name},
                                address)
        return response.json()['result'] if util.is_success(response) else None

    def read_children_types(self, address=[]):
        """ Returns a list of the types of child resources the resource supports. """

        response = self.execute('read-children-types',
                                address)
        return response.json()['result'] if util.is_success(response) else None

    def version(self):
        """ Prints version of WildFly. """

        result = self.read_attribute('release-version')
        return result

    def get_raw_server_groups_info(self):
        """
        Run the equivalent WildFly CLI command   /server-group=*:read-resource
        :return a dictionary representing the response
        """

        address = [{'server-group': '*'}]
        resp = self.read_resource(address)
        return resp.json()

    def get_deployed_apps(self, server_group=None):
        """
        Returns a list of applications deployed on a server group,
        :param server_group The desired server group
        :return a dictionary where the keys are the server group, and the value is a list of all applications running \
                in the said server group
        """
        deployed_apps = self.deployments(server_group)
        # Let's parse the output of the deployed output so it's in a format we expect
        ret_value = {}
        for war, value in deployed_apps.items():
            sgs = value.get('server-groups', [])
            for sg in sgs:
                if sg not in ret_value:
                    ret_value[sg] = []
                ret_value[sg].append(war)

        if server_group:
            item = ret_value.get(server_group, [])
            ret_value = {server_group: item }
        logger.debug("Results = {result}".format(result=ret_value))
        return ret_value

    def get_server_name(self, host):
        """
        Return a single
        Runs the equivalent WF CLI command: ls /host=<host>

        :param host  A Wildfly host as specified by the `ls /hosts` CLI command
        :return A string representing a WF Server name for the given WF host.
        """
        logger.info("Retrieving server name for host '{host}'.".format(host=host))
        address = [{'host': host}, {'server': '*'}]
        result = self.read_resource(address).json()

        logger.info("Retrieved server name for wf host {host}.  Response is {resp}".format(host=host, resp=result))
        status = result.get(KEY_OUTCOME, None)
        if status != 'success':
            raise Exception("Something bad happened when trying th get servers of WF host {host}".format(host=host))

        logger.debug("Command is successful, processing response now...")
        server = None
        if KEY_RESULT in result and result[KEY_RESULT]:
            for list_item in result[KEY_RESULT]:
                address = list_item.get('address', [])
                for item in address:
                    if 'server' in item:
                        server = item['server']
        return server

    def get_server_group(self, host, server_name):
        """
        Gets the server group associated with a WF host and WF server.  Runs the equivalent WF CLI command:
             /host=<host>/server=<server>:read_attribute(name=server-group,include-defaults=true)
        :param host  The WildFly host
        :param server_name  The WildFly server
        :return The value of the server-group
        """
        logger.debug("Retrieving server-group for host '{host}' and server '{server}'...".format(host=host,
                                                                                                 server=server_name))
        address = [{'host': host}, {'server': server_name}]
        val = self.read_attribute('server-group', address, include_defaults=True)
        logger.info("WildFly host {host} and server {server} has a server-group of {sg}".format(host=host,
                                                                                                server=server_name,
                                                                                                sg=val))
        return val

    def get_hostname(self, host, server_name):
        """
        Returns the fully qualified host nanme associated with a given WF host and WF server.  Runs the equivalent WF
        CLI command:   /host=<host>/server=<server>/core-service=server-environment:read_attribute(name=qualified-host-name,include-defaults=true)
        :param host  The WildFly host
        :param server_name  The WildFly server
        :return The associated qualified host name
        """
        logger.debug("Retrieving qualified hostname for host '{host}' and server '{server}'...".format(host=host,
                                                                                                    server=server_name))
        address = [{'host': host}, {'server': server_name}, {'core-service': 'server-environment'}]
        val = self.read_attribute('qualified-host-name', address, include_defaults=True)
        logger.info("WildFly host {wfhost} and server {server} has a hostname of {host}".format(wfhost=host,
                                                                                             server=server_name,
                                                                                             host=val))
        return val

    def _get_hostname_map(self):
        """
        Returns a dictionary that has a mapping of the physical machine qualified_hostname to a WF host and WF server.

        The dictionary has the following sample structure
            { 'wf-hos-2t': 'wf-server-1': { 'server-group-1': "qualified-host-name',
                                            'server-group-2': "qualified-host-name'},
                           'wf-server-2': { 'server-group-3': "qualified-host-name'},
              'wf-host-2': 'wf-server-3': { 'server-group-4': "qualified-host-name'},
                           'wf-server-4': { 'server-group-5': "qualified-host-name',
                                            'server-group-6': "qualified-host-name',
                                            'server-group-7': "qualified-host-name'}
            }
        :return a dictionary that has a mapping of the WF host, server and server group to a physically qualified domain
                name
        """
        logger.debug("Generating Hostname map")
        host_map = {}
        for host in self.hosts():
            logger.debug("host is {host}".format(host=host))
            if host not in host_map:
                # Ensure we have the host key is in the host_map
                host_map[host] = {}
            # Get the server name
            server_name = self.get_server_name(host)

            logger.debug("server name is {server}".format(server=server_name))
            if server_name not in host_map[host]:
                # Ensure the server name is a key under the host
                host_map[host][server_name] = {}

            if server_name:
                try:
                    # Not all WildFly server names will have a server group, so we need to wrap it with a try catch.
                    sg = self.get_server_group(host, server_name)
                    qualified_hostname = self.get_hostname(host, server_name)

                    # Set the Server group and qualified_hostname
                    host_map[host][server_name][sg] = qualified_hostname
                    logger.info("WildFly host {wfhost} and server {server} has a ".format(wfhost=host,
                                                                                       server=server_name,) +
                             "server group {sg} and qualified_hostname of {host}".format(sg=sg,
                                                                                         host=qualified_hostname,))
                except (SystemError, KeyError) as e:
                    # if an error occurs, the WF server may not have a server-group as it may be the data container
                    # Just log the error and "pass"
                    logger.error("(NOT A BUG) A failure occurred: {err}".format(err=e))

        logger.debug("done generating hostname map.")
        logger.info("The Hostname map is {map}".format(map=host_map))
        return host_map

    def get_server_group_host(self, server_group):
        """
        Returns the hostname of a server group
        :param server_group  The server group
        :return hostname associated with a server group
        """
        if "_hostname_map" not in self.__dict__ or self._hostname_map is None or len(self._hostname_map) == 0:
            # Initialize the hostname map if self._hostname_map is not defined in the class object, or is None, or is
            # an empty dictionary
            self._hostname_map = self._get_hostname_map()

        logger.info("Getting server group {sg} hostname.".format(sg=server_group))
        hostnames = [hostname
                     for wf_host in self._hostname_map
                     for wf_server in self._hostname_map[wf_host]
                     for sg, hostname in self._hostname_map[wf_host][wf_server].items()
                     if server_group == sg]
        logger.info("Server Group {sg} is running on hostnames {hostnames}".format(sg=server_group,
                                                                                hostnames=", ".join(hostnames)))
        return hostnames

    def get_application_hostnames(self, application, ext=None):
        """
        Get the hostname where an application is deployed
        :param application The application
        :param ext The application extension  e.g. war, jar
        :return A list of hostnames where the application is running
        """

        # Let's find the server groups that the apps is deployed against, because an app can be deployed to more than
        # one server group
        if ext:
            application = ".".join([application, ext])

        logger.info("Getting hostnames where application {app} is running.".format(app=application))
        # Get a list of deployed all
        sg_info = self.get_deployed_apps()
        server_groups = [sg for sg in sg_info for app in sg_info[sg] if application in app]
        logger.info("Application {app} is deployed in server-groups: {sg}".format(app=application,
                                                                               sg=", ".join(server_groups)))
        hosts_list = set([host for sg in server_groups for host in self.get_server_group_host(sg)])
        logger.info("Application {app} is deployed on host names: {hosts}".format(app=application,
                                                                               hosts=", ".join(hosts_list)))

        return hosts_list
