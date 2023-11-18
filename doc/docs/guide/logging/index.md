---
sidebar_position: 2
---

# Simple Logging Utility

Simple log utility for lazy you.

## Get started

Get a logger:
```python
from neetbox.logging import logger
```

say hello:
```python
world = "world"
logger.log("hello", world)
```
output:
```bash
2023-03-18-13:56:03 > test.py > hello world 
```

## Using a decorator

`@logger.mention` will mention the decorated function on each call.

```python
@logger.mention
def function_a():
    print('message from a')

def function_b():
    function_a()
    print('message from b')

def function_c():
    function_a()
    function_b()
    print('message from c')

function_c()
```
output:
```html
2023-11-18-06:26:04 > main/function_c >  Currently running: function_a
message from a
2023-11-18-06:26:04 > main/function_b >  Currently running: function_a
message from a
message from b
message from c
```


## Auto tracing

The default `logger` automatically trace back the caller of logger instance.

```python
from neetbox.logging import logger

class AClass():
    def __init__(self) -> None:
        logger.log("Class A Ready.")
        self.post_processing()
    def post_processing(self):
        logger.log("Running PostProcessing...")

def get_instance_of_A():
    logger.log("Buidling AClass Instance...")
    return AClass()

a = get_instance_of_A()
```
output:
```bash
2023-03-18-13:57:47 > test.py/get_instance_of_A > Buidling AClass Instance... 
2023-03-18-13:57:47 > AClass/__init__ > Class A Ready. 
2023-03-18-13:57:47 > AClass/post_processing > Running PostProcessing...
```

if you want to specify the identity, try `logger(whom)`:
```python
from neetbox.logging import logger
logger = logger(whom="identity name")
logger.log("some message")
```
output:
```bash
2023-03-18-13:58:40 > identity name > some message 
```

## Log into files

```python
from neetbox.logging import logger
logger.set_log_dir("./logdir")
logger.log("this message will be written to both stdout and file")
logger.log("this message will be written to stdout only", into_file=False)
```
output:
```bash
[INFO]2023-03-18-14:29:59 > neetbox.logging.logger/Logger/info > Directory ./logdir not found, trying to create. 
2023-03-18-14:29:59 > test.py > this message will be written to both stdout and file 
2023-03-18-14:29:59 > test.py > this message will be written to stdout only 
```
in `./logdir/2023-03-18.log`:
```
2023-03-18-14:29:59 | test.py | this message will be written to both stdout and file 

```

:::caution
If you are creating a logger using the Logger constructor, notice that what you create is a new instance of the `Logger` class and it would not share file writers with the others. See [Who Is Logging?](/docs/guide/logging/logger-instances) for more information.
:::

## Options using `logger.log`

If you want to log without datetime, try:
```python
logger.log("some message", with_datetime=False)
```
output:
```
test.py > some message 
```

The same thing, if you want to log without identifier:
```python
logger.log("some message", with_identifier=False)
```
output:
```
2023-03-18-14:44:22 > some message 
```

Looking for advanced format control? See [advanced logging format](./config-logger.md)