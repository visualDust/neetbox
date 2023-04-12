---
sidebar_position: 3
---

# Who is logging?

Basically the default `logger` object located in `neetbox.logging` is enough. There is also another way to get a logger using `neetbox.logging.logger(whom)`. This page is about the difference.

## Caller identity

the `logger` uses caller identity to identify who is calling it, the identity also helps the logger to decide which file to log in to or which color to paint on you console. You can specify the logger identity using `logger(whom)`:

```python
from neetbox.logging import logger

logger = logger("MyIdentity")
logger.log("something")
```
output:
```
2023-03-18-19:56:40 > MyIdentity > something
```

Obviously everything except `None` could be an identity:
```python
from neetbox.logging import logger

class SomeClass:
    def __init__(self) -> None:
        self.logger = logger(self)
        self.logger.log("something")
        
SomeClass()
```
output:
```
2023-03-18-20:15:52 > <__main__.SomeClass object at 0x0000025AFB2C1790>/__init__ > something
```
:::note
Notice that since the logger identity you specified when getting the logger using `logger(whom)` method will be printed into log message. So dont make it too long ; )
:::

## The default style

If you are not passing a style for the logger, it automatically creates the style based on a "default" one and using different colors in console to let you easily distinguish between different caller identity. However, since someone may use an identity-specified logger in different functions, things about default created styles may be different from what you thought about colors. Consider the following example:
```python
from neetbox.logging.logger import logger
logger = logger("someone")
def a():
    logger.log("a")
def b():
    a()
    logger.log("b")
b()
```
output:
```
2023-03-18-22:48:15 > someone/a > a 
2023-03-18-22:48:15 > someone/b > b 
```
Check the code and run it by yourself. You will find the two lines in the output with different colors. This may be confusing, but it is not a bug. The feature was designed because you still want to distinguish between the two lines since they have different function names, right?

:::tip conclusion
The auto-tracing features are kept to "method-level" in loggers with specific identity. If you do not specify the logger style, the style will be automatically created by auto-tracing. So there might be different colors if you are calling the logger in different scopes.
:::

## Caller Identity "None"

If you do not specific the identity while creating the logger or you just use `neetbox.logging.logger` as default, the logger never knows the identifier, so when you invoke `logger.log()` somewhere, it automatically traces back to the caller of `logger.log()`. To be specific, the default logger object (`neetbox.logging.logger`) was initially created by something like `Logger(None)`.  So technically they are the same.
```python
from neetbox.logging import logger
logger_another = logger(None)
logger.log("message from", logger)
logger_another.log("message from", logger_another)
```
output:
```
2023-03-18-22:12:20 > None/ > message from <neetbox.logging.logger.Logger object at 0x00000217D7F60670> 
2023-03-18-22:12:20 > None/ > message from <neetbox.logging.logger.Logger object at 0x00000217D7F60670> 
```
As you can see, they are the same object.


## Create logger manually

We recommend you use `neetbox.logging.logger` or `neetbox.logging.logger(whom)` to get the logger. However, if you want to create a logger instance manually anyway, you can create it from the constructor:
```
from neetbox.logging.logger import Logger

logger1 = Logger(whom="the_same_identity")
logger2 = Logger(whom="the_same_identity")
logger1.log("from", logger1)
logger2.log("from", logger2)
```
output:
```
2023-03-18-22:31:33 > the_same_identity/ > from <neetbox.logging.logger.Logger object at 0x00000217D8130820> 
2023-03-18-22:31:33 > the_same_identity/ > from <neetbox.logging.logger.Logger object at 0x00000217D81303D0> 
```
As you can see, they are different objects even though they have the same identifier. One was called `Logger object at 0x00000217D8130820` and the other was `Logger object at 0x00000217D81303D0`. But if you are using a console, you will see that they are painted the same color. This is because you did not pass a specific `LogStyle` when constructing the logger, it will use automatically generated style specified by their caller identity.

:::caution
However, file writers are not shared among different loggers objects even though they have same identifier. You have to assign file writers to each of them respectively. To be specific:
```python
from neetbox.logging.logger import Logger
logger1 = Logger(whom="the_same_identity").set_log_dir('./logdir1')
logger2 = Logger(whom="the_same_identity").set_log_dir('./logdir2')
logger1.log("from", logger1)
logger2.log("from", logger2)
```
output:
```
[INFO]2023-03-18-22:40:21 > neetbox.logging.logger/Logger/info > Directory ./logdir1 not found, trying to create. 
[INFO]2023-03-18-22:40:21 > neetbox.logging.logger/Logger/info > Directory ./logdir2 not found, trying to create. 
2023-03-18-22:40:21 > the_same_identity/ > from <neetbox.logging.logger.Logger object at 0x00000201B7D116A0> 
2023-03-18-22:40:21 > the_same_identity/ > from <neetbox.logging.logger.Logger object at 0x00000201B7D11070> 
```
output in `./logdir1/2023-03-18.log`:
```
2023-03-18-22:40:21 | the_same_identity/ | from <neetbox.logging.logger.Logger object at 0x00000201B7D116A0> 
```
output in `./logdir2/2023-03-18.log`:
```
2023-03-18-22:40:21 | the_same_identity/ | from <neetbox.logging.logger.Logger object at 0x00000201B7D11070> 
```
:::

This is not a bug. The feature was designed because someone needs to log different things into different files using the same caller identity.