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

**Parameters**:

Name | Type | Default | Description
--- | --- | --- | ---
address | list | [] | The address of wildfly managment resource.
operation | dict | | The operation to perfom on resource.
parameters | dict | None | Parameters to pass to operation.

**Returns** (requests.Response): response from operation execution 

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

* server_group (str): Reload all servers within server group that are currently running. Default = None.
* blocking (bool): Wait until the servers are fully reloaded before returning from the operation. Default = False.

**Returns** (requests.Response): 

## restart-servers

Restart all configured servers in the domain or specific server group that are currently running.

**Parameters**:

* server_group (str): Restart all servers within server group that are currently running. Default = None.
* blocking (bool): Wait until the servers are fully restarted before returning from the operation. Default = False.

**Returns** (requests.Response): 

## deploy

## undeploy
