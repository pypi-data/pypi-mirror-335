# jflat

A humble library for flattening Python dictionaries according to their JSON-paths.

## Installation

```bash
pip install jflat
```

## Usage

```python
from jflat import flatten, unflatten

data = {
    "a": {
        "b": {
            "c": True
        }
    },
    "list": [ 1, 2, 3 ]
}

flattened = flatten(data)
print(flattened)
# {
#     "$.a.b.c": True,
#     "$.list[0]": 1,
#     "$.list[1]": 2,
#     "$.list[2]": 3
# }

unflattened = unflatten(flattened)
print(unflattened)
# {
#     "a": {
#         "b": {
#             "c": True
#         }
#     },
#     "list": [ 1, 2, 3 ]
# }
```
