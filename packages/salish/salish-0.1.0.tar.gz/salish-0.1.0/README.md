Salish is a workflow management library named after the [Salish Sea](https://en.wikipedia.org/wiki/Salish_Sea).

Example:

```
from channels import *
import itertools

def display1(item):
    print("Display1:", item)
    return item, item

def display2(item1, item2):
    print("Display2:", item1, item2)
    return {"item1": item1, "item2": item2}

def display3(item1, item2):
    print("Display3:", item1, item2)
    return item1 + item2

def combinations(items):
    yield from itertools.combinations(items, 2)


pipeline = Channel([1, 2, 3]) | display1 | Bind(display2, how="*") | Bind(display3, how="**") | Bind(combinations, how="collect") | display1
pipeline.join()
```

Output:
```
Display1: 1
Display1: 2
Display1: 3
Display2: 1 1
Display2: 2 2
Display2: 3 3
Display3: 1 1
Display3: 2 2
Display3: 3 3
Display1: (2, 4)
Display1: (2, 6)
Display1: (4, 6)
```

Objects:

Channel: 

Caller

Bind

ReactiveBinding

ChannelIterator