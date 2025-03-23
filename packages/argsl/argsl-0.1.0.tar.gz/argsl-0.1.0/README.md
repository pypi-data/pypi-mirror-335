# argsl

A readable DSL on top of argparse. Define your CLI like:

```python
from argsl import argsl

args = argsl("""
--name|-n <str!>            # Required
--age|-a <int=42>           # Optional with default
--debug|-d <flag>           # Boolean flag
filename <path!>            # Required positional
""")
```

No more boilerplate, just clear CLI definitions.

### CLI Entry Point

You can also run:

```bash
argsl --name Alice --debug
```

To test the built-in DSL runner (self-test).
