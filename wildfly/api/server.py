import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ServerApiMixin(object):

    def servers(self, server_group=None, host=None):
        hosts = self.hosts()
        servers_merged = {}
        for host in hosts:
            address = [{'host': host}]
            servers_config = self.read_children_resources(
                'server-config', address, True)
            logger.debug('SERVERS_CONFIG: {}'.format(servers_config))
            servers = self.read_children_resources('server', address, True)
            logger.debug('SERVERS: {}'.format(servers))
            for key, value in servers.items():
                if value['server-state'] != 'STOPPED':
                    address = [{'host': host}, {'server': key}, {
                        'core-service': 'platform-mbean'}, {'type': 'runtime'}]
                    uptime = self.read_attribute(
                        address=address, name='uptime')
                else:
                    uptime = None
                if server_group is None or servers_config[
                        key]['group'] == server_group:
                    # STARTING, RUNNING, STOPPED or RESTART_REQUIRED
                    servers_merged[key] = {
                        'group': servers_config[key]['group'],
                        'host': host,
                        'status': value['server-state'],
                        'uptime': uptime}
        logger.debug('SERVERS_MERGED: {}'.format(servers_merged))
        return servers_merged

    def server_groups(self):
        server_groups = self.read_children_resources('server-group')
        return server_groups

    def _server_operation(self, operation, server_group=None, blocking=False):
        if server_group:
            address = [{'server-group': server_group}]
        else:
            address = []
        return self.execute(operation, {'blocking': blocking}, address)

    def start_servers(self, server_group=None, blocking=False):
        """ Starts all configured servers in domain or
        server_group that are not currently running. """
        return self._server_operation('start-servers', server_group, blocking)

    def stop_servers(self, server_group=None, blocking=False):
        """ Stops all servers currently running in the domain or
        server_group. """
        return self._server_operation('stop-servers', server_group, blocking)

    def reload_servers(self, server_group=None, blocking=False):
        """ Reloads all servers currently running in the domain. """
        return self._server_operation('reload-servers', server_group, blocking)

    def restart_servers(self, server_group=None, blocking=False):
        """ Restart all servers currently running in the domain or
        server_group. """
        return self._server_operation(
            'restart-servers', server_group, blocking)

    def read_log_file(self, host=None):
        """ Reads the contents of a log file. The file must be in the
        jboss.server.log.dir and must be defined as a file-handler,
        periodic-rotating-file-handler or size-rotating-file-handler. """

        if host is None:
            hosts = self.hosts()
            host = hosts[0]

        address = [{'host': host},
                   {'server': '{}-0'.format(host)},
                   {'subsystem': 'logging'}]
        parameters = {'name': 'server.log', 'tail': 'true', 'lines': '100'}
        response = self.execute('read-log-file', parameters, address)
        return response.json()['result']
