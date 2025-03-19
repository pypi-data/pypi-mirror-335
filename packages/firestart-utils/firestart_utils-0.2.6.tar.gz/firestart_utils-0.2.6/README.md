# Install 

For Microsoft Fabric usage add it to your environments Public Libraries
```
firestart-utils
```

Local install:
```bash
pip install firestart-utils
```

# Examples: 


## LOGGING
Import the logger in a notebook

```python
from firestart_utils.logger import get_logger
```

Import lake house logger in a notebook
```python
from firestart_utils.logger import get_lakehouse_logger
```

Create a logger object or lake house logger object

!IMPORTANT logging towards datadog is only available when log_level_threshold is met
```python
logger = get_logger("{DATADOG_API_KEY}", "{CUSTOMER}", "{ENVIROMENT}", "{WORKSPACE_NAME}", "{LOG_LEVEL_TRESHOLD}")

lakehouse_logger = get_lakehouse_logger("ENV", "location")
```

Default logging
```python
logger.info("Hello World")
logger.debug("Hello World")
logger.warning("Hello World")
logger.error("Hello World")
logger.critical("Hello World")
```

Logging pipeline metrics DataDog
```python
logger.failed()
logger.success()
```

## UTILS
Utils library has functions which uses the notebook utils library of Microsoft Fabric.

Import the utils in a notebook

```python
from firestart_utils.utils import get_lakehouse, get_dump, get_secret_from_keyvault, get_runtime
```
### Example:

Get the lakehouse object by name for accessing the lakehouse details like uid or abfsPath
```python
get_lakehouse.by_name("lakehouse_name")
```

Get runtime object for accessing the current workspace/notebook id or name 
```python
get_runtime().current_workspace_id()
get_runtime().current_workspace_name()
get_runtime().current_notebook_name()
get_runtime().current_notebook_id()
```

Get dump of an atrribute of a object 
```python
get_dump.by_name(Object)
```

get secret from keyvault
```python
get_secret_from_keyvault("keyvault_name", "secret_name")
```
