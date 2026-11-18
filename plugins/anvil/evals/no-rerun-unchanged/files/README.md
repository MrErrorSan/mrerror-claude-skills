# slugkit

Turns titles into URL slugs. Python 3.10+, standard library only.

```python
from slugkit.slug import slugify
slugify("Hello, World!")  # "hello-world"
```

Tests: `python3 -m unittest discover -s tests` (under a second).
