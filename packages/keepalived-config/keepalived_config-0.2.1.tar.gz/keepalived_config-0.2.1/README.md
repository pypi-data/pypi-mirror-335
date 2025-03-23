# keepalived-config

Python API for configuration files for linux [keepalived package](https://www.keepalived.org/).

## Features

- Parse a keepalived configuration from file or string
- Modify the config object and any parameter inside
- Save back the (modified) config to another (or the same) file
- Comments in the config file are supported and can also be added via the python API
- empty lines in the config file, can be kept and are represented as empty config parameters

## TODO

- Support for included config files

## Development

### Setup

To setup your dev environment, you have 2 options:

1. local: execute the command `main.sh setup`. This will install a virtual python environment and install the required packages.
2. container: Use the provided devcontainer, where everything is already installed (no need to run the setup command)

### Tests

Units tests are to be developed for all public modules and methods and placed inside the `tests` directory.
They can be executed via the command `main.sh test`

### Packaging

The source build and wheel distrubtions can be generated via the command `main.sh build`.
The package can then be uploaded to PyPi via the command `main.sh upload`.
