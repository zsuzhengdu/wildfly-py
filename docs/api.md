# Client API

To instantiate a `Wildfly` class that will allow you to communicate with a WildFly domain controller, simply do:

```python
from wildfly import Wildfly
client = Wildfly(host='localhost')
```

**Params**:

Name | Type | Default | Description
--- | --- | --- | ---
host | string | localhost | WildFly domain controller host address.
port | string | 9990 | WildFly domain controller port.
username | string | admin | The username for authentication while connecting to the controller.
password | string | admin | The password for authentication while connecting to the controller.
timeout | int | 5000 | The HTTP request timeout, in milliseconds.

****

## version

Prints the version info of the WildFly Application Server release.

**Parameters**:

* None

**Returns**: (string): WildFly version.

## execute

Execute operation against management resource.

Operation requests allow for low level interaction with the management model. The management model is represented as a tree of addressable resources, where each node in the tree (aka resource) offers a set of operations to execute.

An operation request basically consists of three parts: the address, an operation name and an optional set of parameters.

```python
host = '172.32.1.32'
address = [{'host': host},
           {'server': '{}-0'.format(host)},
           {'subsystem': 'logging'}]
parameters = {'name': 'server.log', 'tail': 'true', 'lines': '100'}
response = client.execute('read-log-file', parameters, address)
```

**Parameters**:

Name | Type | Default | Description
--- | --- | --- | ---
address | list | [] | The address of wildfly management resource.
operation | string | | The operation to perfom on resource.
parameters | dict | None | Parameters to pass to operation.

**Returns** (requests.Response): response from operation execution 

## add

Creates a new management resource.

```python
address = [{'profile': 'full-ha'},
           {'subsystem': 'jmx'},
           {'remoting-connector': 'jmx'}
parameters = {'use-management-endpoint': 'false'}
response = client.add(parameters, address)
```

## remove

Remove existing management resource.

```python
address = [{'profile': 'full-ha'},
           {'subsystem': 'jmx'},
           {'remoting-connector': 'jmx'}
response = client.remove(address)
```

## start-servers

Starts all configured servers in the domain or specific server group that are not currently running.

**Parameters**:

* server_group (str): Starts all servers within server group that are not currently running. Default = None.
* blocking (bool): Wait until the servers are fully started before returning from the operation. Default = False.

**Returns** (requests.Response): 

## stop-servers

Stop all configured servers in the domain or specific server group that are currently running.

**Parameters**:

* server_group (str): Stops all servers within server group that are currently running. Default = None.
* blocking (bool): Wait until the servers are fully stopped before returning from the operation. Default = False.

**Returns** (requests.Response): 

## reload-servers

Reload all configured servers in the domain or specific server group that are currently running.

**Parameters**:

* server_group (string): Reload all servers within server group that are currently running. Default = None.
* blocking (bool): Wait until the servers are fully reloaded before returning from the operation. Default = False.

**Returns** (requests.Response): 

## restart-servers

Restart all configured servers in the domain or specific server group that are currently running.

**Parameters**:

* server_group (string): Restart all servers within server group that are currently running. Default = None.
* blocking (bool): Wait until the servers are fully restarted before returning from the operation. Default = False.

**Returns** (requests.Response): 

## deploy

Deploy artifact to WildFly.

**Parameters**:

* groupId (string): 
* artifactId (string):
* version (string):
* type (string): artifact packaging type. Default: war
* server_groups (sting): Default: 'A'
* path (string): Default: None
* enabled (bool): Default: True

## undeploy

Undeploy artifact from WildFly.

**Parameters**:

* artifactId (string):
* type (string): artifact packaging type. Default: war
* server_groups (sting): Default: all


## deployment_info


