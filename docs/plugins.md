# ml-git Data Specialization Plugins

Data specialization plugins are resources that can be added to ml-git providing specific processing and metadata collection for specific data formats. This document aims to provide instructions on how data specialization plugins can be developed for ml-git, defining interface methods that must be implemented to provide the necessary functionalities for processing these data.

## Plugin contracts

<details>
<summary><code> add_metadata </code></summary>
</br>

This method is responsible for processing or gathering information about the versioned data and inserting it into the specification file. If the plugin is installed and properly configured, this signature will be triggered before the metadata is committed. 

*Definition:*

```python
def add_metadata(work_space_path, metadata):
    """
    Args:
        work_space_path (str): Absolute path where the files managed by 
        ml-git will be used to generate extra information that can be
        inserted in metadata.
        metadata (dict): Content of spec file that can be changed to add extra data.
    """
```
</details>

<details>
<summary><code> compare_metadata </code></summary>
</br>

This method is responsible for displaying a formatted output containing the comparison of the information that was added by the plugin in the specification file for each version of the entity.
If the plugin is installed and configured correctly, this signature will be triggered during the execution of the ml-git log command.

*Definition:*

```python
def compare_metadata(specs_to_compare):
    """
    Args:
        specs_to_compare (Iterator[dict]): List containing current spec file and predecessors to be compared for each version.
    """
```
</details>

**Note:**
The plugin doesn't need to implement all methods defined in the plugin contract.

## How to create a plugin

When developing the plugin we recommend that the user follow the structure proposed below:
```
ml-git-plugin-project-name/
    tests/
        core_tests.py
    package_name/ <-- name of your main package.
        __init__.py
        core.py <-- main module where the entry function is located.
    setup.py
```

In `package_name/core.py` it is expected to contain only the contract methods essential to the operation of the plugin.

```python
# package_name/core.py

def add_metadata(work_space_path, metadata):
    ...
    ...
```

In `package_name/__init__.py` it's necessary to import the implemented contract's methods. As in the following example:

```python
# package_name/__init__.py

from package_name.core import add_metadata
```

The main purpose of the setup script is to describe your module distribution.

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

For an entity of your preference, change the spec file like below: 

*(ex: dataset/dataset-ex/dataset-ex.spec)*
```yaml
datasets:
  categories:
  - computer-vision
  - images
  manifest:
    data-plugin: package_name <-- type here the package name in your plugin project.
    files: MANIFEST.yaml
    storage: s3h://mlgit
  mutability: strict
  name: dataset-ex
  version: 1
```