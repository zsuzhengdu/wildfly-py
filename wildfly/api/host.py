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
