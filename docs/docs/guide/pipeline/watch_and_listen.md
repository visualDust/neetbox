# Watch and Listen

`@watch` provides

Example:

1. Initialize a empty project
```bash
mkdir test_pipeline
cd test_pipeline
neet init
```
create and edit `test.py`. In `test.py`:
```python
from neetbox.pipeline import watch,listen
from neetbox.extension.environment import hardware
from neetbox.logging import logger
import time

@watch(initiative=True)
def train(epoch):
    return f"result loss and acc of epoch {epoch}"

@listen(train)
def print_result(the_value):
    logger.log(the_value)

for epoch in range(1000):
    train(epoch)
    time.sleep(1) # fake example
```
