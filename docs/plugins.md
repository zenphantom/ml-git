# Ml-git Plugins

The ml-git plugin is an interface to bind external functions to changes some commands behavior.

## Commands with plugin

- `ml-git <ml-entity> commit`

  In commit we have a point with plugin statement to help us to increment spec file with additional informations.

## How to create a plugin

#### Plugin structure

```
ml-git-plugin-project-name/
    tests/
        core_tests.py
    package_name/ <-- name of your main package.
        __init__.py
        core.py <-- main module where the entry function is located.
    setup.py
```
#### Implementation

Your need to implement the method *add_metadata*, it will be used by plugin caller in commit command to add extra informations in metadata file (.spec).

```python
# package_name/core.py
def add_metadata(work_space_path, metadata):
    """
    Args:
        works_space_path (str): Absolute path where the files managed by ml-git going to           be used to generate extra information that can be inserted in metadata.
        
        metadata (dict): Content of spec file that can be changed to add extra data.
    """
    ...
```

*Import entry function required to facilitate the use of the ml-git plugin.*

```python
# package_name/__init__.py

from package_name.core import add_metadata
```

```python
# setup.py

from setuptools import setup, find_packages

setup(
    name='ml-git-plugin-project-name',
    version='0.1',
    license='GNU General Public License v2.0',
    author='',
    description='',
    packages=find_packages(),
    platforms='Any',
    zip_safe=True,
)
```
## How to install a plugin

```
cd plugin-project-name
pip3 install --user .
```

In your project managed by ml-git, change your spec file like below:

```yaml
dataset:
  categories:
  - computer-vision
  - images
  manifest:
    data-plugin: package_name <-- type here the package name in your plugin project.
    files: MANIFEST.yaml
    store: s3h://mlgit
  mutability: strict
  name: dataset-ex
  version: 1
```