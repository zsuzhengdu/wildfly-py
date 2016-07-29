import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class HostApiMixin(object):

    def hosts(self, server_group=None):
        """ Returns list of hosts. """

        # TODO need to implement filter for only hosts in specified server_group
        hosts = self.read_children_names('host')
        logger.debug('HOSTS: {}'.format(hosts))
        return hosts

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
