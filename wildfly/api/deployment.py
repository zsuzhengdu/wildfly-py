import os
import errno
import logging
import requests
from .. import util


DEFAULT_CONTENT_HOST = 'http://repo.maven.apache.org'
DEFAULT_CONTENT_HOST_EP = 'maven2'
DEFAULT_CONTENT_HOST_PORT = '80'
DEFAULT_SERVER_GROUP = 'A'
DEFAULT_ARTIFACT_TYPE = 'war'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DeploymentApiMixin(object):

    def deployments(self, server_group=None, host=None):
        """ Returns information about deployments. """

        # status['RUNNING', 'STOPPED', 'FAILED']
        deployments = self.read_children_resources('deployment')
        for key in deployments:
            deployments[key]['server-groups'] = []
            deployments[key]['enabled'] = False
            deployments[key]['status'] = 'STOPPED'
            deployments[key]['hosts'] = []

        server_groups = self.server_groups()
        for _server_group in server_groups:
            deployments_in_group = self.read_children_resources(
                'deployment', [{'server-group': _server_group}], runtime=True)
            for key in deployments_in_group:
                deployments[key]['enabled'] = deployments_in_group[
                    key]['enabled']
                if 'server-groups' in deployments[key]:
                    deployments[key]['server-groups'].append(_server_group)
                else:
                    deployments[key]['server-groups'] = [_server_group]

        servers = self.servers()
        for server in servers:
            if servers[server]['status'] != 'STOPPED':
                deployments_on_server = self.read_children_resources(
                    'deployment',
                    [{'host': servers[server]['host']}, {'server': server}],
                    runtime=True)
                logger.debug(
                    'DEPLOYMENTS_ON_SERVER({}): {}'.format(
                        server, deployments_on_server))
                for key in deployments_on_server:
                    if deployments_on_server[key]['status'] == 'OK':
                        deployments[key]['status'] = 'RUNNING'
                    deployments[key]['hosts'].append(servers[server]['host'])

        if server_group:
            for key in deployments.keys():
                if server_group not in deployments[key]['server-groups']:
                    del deployments[key]

        if host:
            for key in deployments.keys():
                if host not in deployments[key]['hosts']:
                    del deployments[key]

        return deployments

    def is_deployment_in_repository(self, name):
        """ Check if deployment exists in content repository. """
        return name in self.deployments()

    def is_deployment_enabled(self, name):
        """ Check if deployment is enabled. """
        return self.deployments()[name]['enabled']

    def deployment_status(self, name):
        """ Get deployment status. """
        return self.deployments()[name]['status']

    def pull(
            self,
            groupId,
            artifactId,
            version,
            type='war',
            server_groups=DEFAULT_SERVER_GROUP,
            path=None,
            content_host=DEFAULT_CONTENT_HOST,
            content_host_ep=DEFAULT_CONTENT_HOST_EP,
            content_host_port=DEFAULT_CONTENT_HOST_PORT):
        """ Pull artifact from artifact repository into wildfly content
        repository. """

        self.deploy(groupId, artifactId, version, type, server_groups,
                    path, enabled=False,
                    content_host=content_host, content_host_ep=content_host_ep,
                    content_host_port=content_host_port)

    def deploy(
            self,
            groupId,
            artifactId,
            version,
            type=DEFAULT_ARTIFACT_TYPE,
            server_groups=DEFAULT_SERVER_GROUP,
            path=None,
            enabled=True,
            force=True,
            content_host=DEFAULT_CONTENT_HOST,
            content_host_ep=DEFAULT_CONTENT_HOST_EP,
            content_host_port=DEFAULT_CONTENT_HOST_PORT):
        """ Deploy artifact to WildFly. """

        # TODO need to handle SNAPSHOT versions

        if path is None:
            if content_host_ep == 'nexus':
                BASE_URL = '{}:{}/nexus/service/local/repo_groups' \
                           '/public/content'.format(content_host,
                                                    content_host_port)

                url = '{0}/{1}/{2}/{3}/{2}-{3}.{4}'.format(
                    BASE_URL,
                    groupId.replace('.', '/'),
                    artifactId,
                    version,
                    type)

            elif content_host_ep == 'maven2':
                BASE_URL = '{}:{}/maven2'.format(content_host,
                                                 content_host_port)
                url = '{0}/{1}/{2}/{3}/{2}-{3}.{4}'.format(
                    BASE_URL,
                    groupId.replace('.', '/'),
                    artifactId,
                    version,
                    type)

            else:
                # Not supported
                raise Exception("Content host type {} not supported"
                                .format(content_host_ep))

            # check if url exists
            response = requests.head(url)
            if response.status_code is not 200:
                response.raise_for_status()

            # upload artifact from url to content repository
            response = self.execute('upload-deployment-url', {'url': url})

        else:

            # check if file exists
            if not os.path.isfile(path):
                raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), path)

            # upload artifact from local file path to content repository
            files = {'file': open(path, 'rb')}
            response = requests.post(
                self.endpoint + '/add-content',
                files=files,
                auth=requests.auth.HTTPDigestAuth(
                    self.username,
                    self.password))
            logger.debug(
                'Response Status Code: {}: {}'.format(
                    response.status_code,
                    response.reason))
            logger.debug('Response: {}'.format(response.json()))

        # TODO support new deploy and redeploy
        # TODO if deploy fails then rollback to previous
        # if force:
        # if isDeploymentInRepository("{}.{}".format(artifactId, type)):
        # replaceDeployment(ctx, f, deploymentUrl, name, runtimeName, disabled)
        # return

        # https://github.com/cenx-cf/wildfly-py/issues/5
        if type == 'war':
            runtime_name = artifactId + '-' + version + '.' + type
        elif type == 'jar':
            runtime_name = artifactId.split(
                '-')[-2] + '-resources' + '.' + type

        # add artifact to content repository
        byte_value = response.json()['result']['BYTES_VALUE']
        request = {"content": [{"hash": {"BYTES_VALUE": byte_value}}],
                   "address": [{"deployment": "{}".format(runtime_name)}],
                   "operation": "add"}
        response = self._post(request)

        # add artifact to server-group(s)
        address = [{'server-group': server_groups},
                   {'deployment': '{}'.format(runtime_name)}]
        response = self.add(address, {'enabled': enabled})

    def disable(self, name, server_groups=DEFAULT_SERVER_GROUP):
        """ Disable artifact in given server_groups, but keep artifact in
        assigned server_groups. """
        address = [{'server-group': server_groups},
                   {'deployment': name}]

        response = self.execute('undeploy', address=address)
        if not util.is_success(response):
            logging.debug("Failed to disable artifact: {}".format(name))

    def enable(self, name, server_groups=DEFAULT_SERVER_GROUP):
        """ Enable artifact in given server_groups. """
        address = [{'server-group': server_groups},
                   {'deployment': name}]

        response = self.execute('deploy', address=address)
        if not util.is_success(response):
            logging.debug("Failed to enable artifact: {}".format(name))

    def undeploy(self, name, server_groups=DEFAULT_SERVER_GROUP):
        """ Undeploy artifact from WildFly. """

        # remove deployment from server-group(s)
        address = [{'server-group': server_groups},
                   {'deployment': name}]
        response = self.remove(address)
        if util.is_success(response) is True:
            # remove deployment from content repository
            address = [{"deployment": name}]
            response = self.remove(address)
        return response

    def _download_from_bamboo(self):

        print "NOT YET IMPLEMENTED"
        # ATLASSIAN_USER=ian.kent
        # wget -nv --http-user=$ATLASSIAN_USER --ask-password
        # http://cenx-cf.atlassian.net/builds/browse/UI-APOLLO-$APP_BUILD/artifact/shared/apollo-app/apollo.war?os_authType=basic
        # -O /opt/cenx/deploy/apollo.war
