The ezpath module allows managing paths relative to the file calling the module's functions, as opposed to being relative to the current working directory. This can be helpful to manage dependencies in a large local codebase.

Example:

```python
from ezpath import *

# adding ../src (relative to the current file) to PYTHONPATH
add_rel_path('../src', follow_links=False)

# adding an absolute path to PYTHONPATH
add_abs_path('/path/to/my/folder')

# getting the absolute path of a file/folder relative to the current file
get_abs_path('../src/my_file.py', follow_links=False)
```
