# ckanext-selfinfo

This extension is built to represent a basic information about the running CKAN Application accessible only to admins.

CKAN should be configured to be able to connect to Redis as it heavily relies on it for storage.

On CKAN admin page `/ckan-admin/selfinfo`, admin can see such information as:
* System Information
    - System name
    - Python version
* RAM
    - RAM Usage in %
    - RAM Usage in GB
* Disk Space
    - Path
    - Disk Usage in %
    - Disk Total
    - Disk Free
* CKAN Information
    - Site Title
    - CKAN Version
    - Default Language
    - Extensions that enabled on the portal
* GIT Information (Optional, see Config Settings section)
    - Project
    - Head
    - Based on
    - Commit
    - Remotes
* PIP Freeze
    - List of modules that are installed.
* Python Information
    - Provides information about CKAN Core, CKAN Extensions, Python installed packages. It shows their current version and latest version.
* Errors (Optional, see Enable Error Saving section)
    - Shows latest exceptions.

## Requirements

Having CKAN Core version 2.10+

Installing the packages mentioned in `requirements.txt` file.


## Installation

To install ckanext-selfinfo:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com//ckanext-selfinfo.git
    cd ckanext-selfinfo
    pip install -e .

3. Add `selfinfo` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload


## Developer installation

To install ckanext-selfinfo for development, activate your CKAN virtualenv and
do:

    git clone https://github.com//ckanext-selfinfo.git
    cd ckanext-selfinfo
    python setup.py develop


## Config Settings

`ckan.selfinfo.redis_prefix_key` - This configuration is needed, when you use Redis with multiple CKAN apps. In order to have a unique key per portal, this configuration can be used. Example `ckan_test` will be used as `ckan_test_errors_selinfo`.

`ckan.selfinfo.ckan_repos_path` - Path to the src folder where CKAN and CKAN Extensions stored at the environment. While provided, additional GIT Infromation will be granted. Make sure that there no other folders and files that are not related to CKAN are stored there. Example: `/usr/lib/ckan/default/src`

`ckan.selfinfo.ckan_repos` - List of CKAN Extension folders separated by space (ckanext-scheming ckanext-spatial ckanext-xloader). By default, if `ckan.selfinfo.ckan_repos_path` is provided, it will look into the directory and gather the extensions from there. Make sure to read the Note under this options before adding it, as it may cause 500 error, if not configured right.

#### NOTE!
For Linux, keep in mind that the added folder in `ckan.selfinfo.ckan_repos_path` should have the same owner as the one that runs the application (e.g. if the application runs from `ckan` User in the system, then ckanext-scheming folder owner should be `ckan`), otherwise there will be an error related to ownership of the repository.

`ckan.selfinfo.partitions` - Used for representing disk space. The value is comma separated paths. By default the value is `/`, which is usually the root.

Example: `/path/to/partition /path/to/partition2 /path/to/partition3`

`ckan.selfinfo.errors_limit` - Limit used to specify how much errors will be stored in Redis. By default this value is `20`.


## Enable Errors Saving
In CKAN INI file, need to add and modify few lines.

After `handler_console` section add:

    [handler_selfinfoErrorHanlder]
    class = ckanext.selfinfo.handlers.SelfinfoErrorHandler
    level = ERROR
    formatter = generic

In `handlers` modify the `keys`, example:

    [handlers]
    keys = console, selfinfoErrorHanlder

In `logger_ckan` modify `handlers`, example:

    [logger_ckan]
    level = INFO
    handlers = console, selfinfoErrorHanlder
    qualname = ckan
    propagate = 0


## Tests

To run the tests, do:

    pytest --ckan-ini=test.ini


## Releasing a new version of ckanext-selfinfo

If ckanext-selfinfo should be available on PyPI you can follow these steps to publish a new version:

1. Update the version number in the `setup.py` file. See [PEP 440](http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers) for how to choose version numbers.

2. Make sure you have the latest version of necessary packages:

    pip install --upgrade setuptools wheel twine

3. Create a source and binary distributions of the new version:

       python setup.py sdist bdist_wheel && twine check dist/*

   Fix any errors you get.

4. Upload the source distribution to PyPI:

       twine upload dist/*

5. Commit any outstanding changes:

       git commit -a
       git push

6. Tag the new release of the project on GitHub with the version number from
   the `setup.py` file. For example if the version number in `setup.py` is
   0.0.1 then do:

       git tag 0.0.1
       git push --tags

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
