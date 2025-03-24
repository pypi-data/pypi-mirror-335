# Nopaque Config

A configuration management utility for Nopaque services. Install this into any application and provide the correct environment table name to be able to fetch, write, update and delete config data.

## Installation

```bash
pip install tpconfig
```

# Builds

Carry out the following:

Update the version in `config-package/src/__init__.py` and `config-package/setup.py`

1. `cd config-package`
2. `pip install setuptools twine`
3. `python setup.py sdist bdist_wheel`
4. `twine check dist/*`
6. `twine upload dist/*`