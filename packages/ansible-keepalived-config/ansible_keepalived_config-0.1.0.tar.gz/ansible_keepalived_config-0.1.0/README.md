# ansible-keepalived-config

ansible module API for working with configuration files for linux [keepalived package](https://www.keepalived.org/).

## Features

- Modify the config object and any parameter inside
- Save back the (modified) config to another (or the same) file
- Comments in the config file are supported and can also be added
- ansible module that supports modification of parameters and also blocks in the configuration with full idempotency

## Usage

Recommended way is to install the module in your virtual environment you are using on yopur ansible controller. Then just create a symlink in your `ANSIBLE_LIBRARY` with the same name pointing to the installed `ansible_keepalived.py` (or just clone this repo or only the module file).

### Parameters

- ***key*** [required]</br>
    This is the name of the key in the configuration you want to modify. If you need to modify a nested key, give the key as a dot seperated path.  
    ```
    Example:
    vrrp_instance VI_1 {
        router_id 1
        authentication {
            user myuser
            pass mypass
        }
    }
    ```
    If you want to modify the authentication password, the correct key would be:  
    `vrrp_instance VI_1.authentication.pass`

- ***file*** [optional, default=`/etc/keepalived/keepalived.conf`]</br>
    This is the source file of the keepalived configuration you want to modify

- ***value*** [optional, required if state == present, default=`none`]</br>
    The new/desired value you want your given key to have. In general, this should be just the value of your key, for example `my very strong password`.</br>
    But you can also manipulate a complete configuration block:</br>
    ```
    {
        token my-very strong t0ken even with spaces
    }
    ```
    Setting this value and the key to `vrrp_instance VI_1.authentication`, then the authentication block will be updated with all the nested contents.
    > ***NOTE***: If you have a block with an id (like vrrp_instance) and you want to modify its id, you have to fully redefine the block in the value field like so:
    >```
    >vrrp_instance VI_NEW {
    >  router_id 3    
    >}
    >```
    > and you need to set the module parameter `with_key_prefix` to false (the related key would be `vrrp_instance VI_1`)! Keep in mind, that this is not idemptotent, as on the next execution VI_1 will not be present anymore!

- ***with_key_prefix*** [optional, default=`false`]</br>
    This automatically adds the last element of your (eventually) nested key value to the given value to build the new/updated configuration. There are special cases (like renaming a named config block), where this is requried to be set to false

- ***create*** [optional, default=`false`]</br>
    If this is true, the module will not fail when the given key is not found in the config but instead add it to the configuration. Also works for nested keys.

- ***state*** [optional, default=`present`]
    If this is set to present, the key will be updated or not modified at all if the value already matches. If the key is not existing, it will fail if `create == false`. If state is `absent` the key will be removed from the configuration if present.


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
