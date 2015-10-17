# Client API

To instantiate a `Wildfly` class that will allow you to communicate with a WildFly domain controller  daemon, simply do:

```python
>>> from wildfly import Wildfly
>>> client = Wildfly(host='localhost')
```

**Params**:

* host (str): Refers to WildFly domain controller host address.
* port (str): Port used by WildFly domain controller.
* username (str): The username for authentication while connecting to the controller. Default: admin
* password (str): The password for authentication while connecting to the controller. Default: admin
* timeout (int): The HTTP request timeout, in milliseconds. Defaults to 5000 milliseconds.

****

## version

Prints the version info of the WildFly Application Server release.

**Params**:

* None

**Returns** (str): WildFly version.

## operation

Run operation ...

**Params**:

* address (str): The container to attach to
* operation (bool): Get STDOUT

**Returns** (str): The logs or output for the image

## start-servers

Starts all configured servers in the domain or specific server group that are not currently running.

**Params**:

* server_group (str): Starts all servers within server group that are not currently running. Default = None.
* blocking (bool): Wait until the servers are fully started before returning from the operation. Default = False.

**Returns** (requests.Response): response

## stop-servers

Stop all configured servers in the domain or specific server group that are currently running.

**Params**:

* server_group (str): Stops all servers within server group that are currently running. Default = None.
* blocking (bool): Wait until the servers are fully stopped before returning from the operation. Default = False.

**Returns** (requests.Response): response

## restart-servers

Restart all configured servers in the domain or specific server group that are currently running.

**Params**:

* server_group (str): Restart all servers within server group that are currently running. Default = None.
* blocking (bool): Wait until the servers are fully restarted before returning from the operation. Default = False.

**Returns** (requests.Response): response

## deploy

## undeploy
