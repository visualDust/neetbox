# Logging Utility

Simple log utility for lazy you.

## Get started

Get a logger:
```python
from neetbox.logging import get_logger
logger = get_logger()
```

say hello:
```python
logger.log_os_info()
```
output:
```bash
whom		|	visualdust using OffensiveQwQ
machine		|	AMD64 on Intel64 Family 6 Model 151 Stepping 2, GenuineIntel
system		|	Windows10.0.22624
python		|	('default', 'Mar 25 2022 05:59:00'), ver 3.8.13
```

## Who is logging?

`get_logger()` automatically trace back the creator of logger instance in any scope.

```python
class AClass():
    def __init__(self) -> None:
        self.logger = get_logger()
        self.logger.log("Class A Ready.")
        self.post_processing()
    def post_processing(self):
        self.logger.log("Running PostProcessing...")

logger = get_logger()
def get_instance_of_A():
    logger.log("Buidling AClass Instance...")
    return AClass()

a = get_instance_of_A()
```
output:
```bash
2023-03-09-15:10:41 > somefile.py > get_instance_of_A > Buidling AClass Instance...
2023-03-09-15:10:41 > AClass > Class A Ready.
2023-03-09-15:10:41 > AClass > Running PostProcessing...
```

if you want to specify the identity, try:
```python
logger = get_logger(whom="identity name")
logger.log("some message")
```
output:
```bash
2023-03-09-15:44:22 > identity name > some message
```

## Log into files

```python
logger = get_logger()
logger.set_log_dir("./logdir")
logger.log("this message will be written to both stdout and file")
logger.log("this message will be written to stdout only", into_file=False)
logger.log("this message will be written to file only", into_stdout=False)

logger_another = get_logger("another logger")
logger_another().bind_file("specific_file.txt")
logger_another.log("this message will be written to both stdout and file")
```
output:
```bash
2023-03-09-15:26:25 > LOGGER > Directory ./logdir not found, trying to create.
2023-03-09-15:26:25 > somefile.py > this message will be written to both stdout and file
2023-03-09-15:26:25 > somefile.py > this message will be written to stdout only
2023-03-09-15:26:25 > another logger > this message will be written to stdout only
```
in `./log_dir/xxxx-xx-xx.log`:
```
2023-03-09-15:26:25 > somefile.py > this message will be written to both stdout and file
2023-03-09-15:26:25 > somefile.py > this message will be written to file only
```
in `./specific_file.txt`:
```
2023-03-09-15:26:25 > another logger > this message will be written to file only
```

## Log format

### Log with a icon

```python
logger = get_logger(icon='❤️')
logger.log("some message")
```
output:
```bash
2023-03-09-15:40:13 > ❤️2117723647.py > some message
```

### Log with color

Logger automatically applys a random color. If you want to specify the color, try:
```python
logger = get_logger(color='red')
logger.log("some message")
```

### datetime format

```
logger = get_logger(whom="NEETBOX", color='black')
logger.log("some message")
logger.log("some message", date_time_fmt="%Y-%m-%d")
logger.log("some message", date_time_fmt="%H:%M:%S")
```
output:
```bash
2023-03-09-15:53:29 > NEETBOX > some message
2023-03-09 > NEETBOX > some message
15:53:29 > NEETBOX > some message
```

### Log raw message

```python
logger.log(
    "raw message without icon and datetime",
    date_time_fmt=None,
    with_ic=False,
    with_identifier=False,
)
```
output:
```
raw message without icon and datetime
```
