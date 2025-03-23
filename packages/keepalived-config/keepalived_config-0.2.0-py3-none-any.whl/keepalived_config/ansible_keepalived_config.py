#!/usr/bin/python

# this module can update the configuration file(s) of keepalived

import os
import json
import traceback

from ansible.module_utils.basic import AnsibleModule
from keepalived_config.keepalived_config_parser import (
    KeepAlivedConfigParser,
    KeepAlivedConfig,
)
from keepalived_config.keepalived_config_block import (
    KeepAlivedConfigBlock,
    KeepAlivedConfigParam,
    KeepAlivedConfigConstants,
)


class AnsibleKeepAlivedConfig:
    SUPPORTED_STATES = ["present", "absent"]

    def __init__(self):
        self._module = None
        self._result = None

    def get_config_item(self, config: KeepAlivedConfig, key: str) -> tuple:
        parent = None
        config_item = config

        if not isinstance(config, KeepAlivedConfig):
            raise TypeError(
                f"Invalid type '{type(config)}' for config! Expected '{KeepAlivedConfig.__class__.__name__}'"
            )

        if not isinstance(key, str):
            raise TypeError(f"Invalid type '{type(key)}' for key! Expected 'str'")

        if not key:
            return (config, None)

        for k in key.split("."):
            parent = config_item
            config_item = list(filter(lambda p: p.name == k, config_item.params))
            if not config_item:
                raise KeyError(f"Key '{key}' not found in config!")
            if len(config_item) > 1:
                raise KeyError(f"Multiple keys found for '{key}' in config!")
            config_item = config_item[0]

        if config_item == config:
            raise KeyError(f"Key '{key}' not found in config!")

        return (config_item, parent)

    def update_config_item(
        self,
        parent_item: KeepAlivedConfig | KeepAlivedConfigBlock | KeepAlivedConfigParam,
        item: KeepAlivedConfigBlock | KeepAlivedConfigParam,
        new_value: str,
        state: str,
        with_key_prefix: bool = True,
    ):
        if not isinstance(parent_item, (KeepAlivedConfig, KeepAlivedConfigBlock)):
            raise TypeError(
                f"Invalid type '{type(parent_item)}' for parent_item! Expected '{', '.join(t.__class__.__name__ for t in [KeepAlivedConfig, KeepAlivedConfigBlock])}'"
            )

        if not isinstance(item, (KeepAlivedConfigBlock, KeepAlivedConfigParam)):
            raise TypeError(
                f"Invalid type '{type(item)}' for item! Expected '{KeepAlivedConfigBlock.__class__.__name__}' or '{KeepAlivedConfigParam.__class__.__name__}'"
            )

        if not isinstance(new_value, str):
            raise TypeError(
                f"Invalid type '{type(new_value)}' for new_value! Expected 'str'"
            )

        if not isinstance(state, str):
            raise TypeError(f"Invalid type '{type(state)}' for state! Expected 'str'")
        if state not in self.SUPPORTED_STATES:
            raise ValueError(
                f"Invalid state '{state}'! Supported states: {', '.join(self.SUPPORTED_STATES)}"
            )

        if state == "absent":
            parent_item.params.remove(item)
            return

        new_config: KeepAlivedConfig = KeepAlivedConfigParser().parse_string(
            f"{item.name} {new_value}" if with_key_prefix else new_value
        )

        if isinstance(
            item, (KeepAlivedConfig, KeepAlivedConfigBlock)
        ) and not isinstance(new_config.params[0], KeepAlivedConfigBlock):
            raise ValueError(
                f"Invalid config string '{new_value}'! Expected valid block config string"
            )

        index = parent_item.params.index(item)
        parent_item.params[index] = new_config.params[0]

    def create_config_item(
        self,
        config: KeepAlivedConfig,
        key: str,
        value: str,
        with_key_prefix: bool = True,
    ):
        if not isinstance(config, KeepAlivedConfig):
            raise TypeError(
                f"Invalid type '{type(config)}' for config! Expected '{KeepAlivedConfig.__class__.__name__}'"
            )

        if not isinstance(key, str):
            raise TypeError(f"Invalid type '{type(key)}' for key! Expected 'str'")

        if not isinstance(value, str):
            raise TypeError(f"Invalid type '{type(value)}' for value! Expected 'str'")

        if not isinstance(with_key_prefix, bool):
            raise TypeError(
                f"Invalid type '{type(with_key_prefix)}' for with_key_prefix! Expected 'bool'"
            )

        # get the parent item by cutting off the last key
        parent_item, _ = self.get_config_item(config, ".".join(key.split(".")[:-1]))

        new_config: KeepAlivedConfig = KeepAlivedConfigParser().parse_string(
            f"{key.split(".")[-1]} {value}" if with_key_prefix else value
        )

        parent_item.params.append(new_config.params[0])

    def run_module(self):
        # Define the argument/parameters that the module should accept
        module_args = dict(
            key=dict(
                type="str",
                required=True,
                help="The key in the config to update. Can be a nested key, given as a dot-separated string.",
            ),
            file=dict(
                type="str",
                default=KeepAlivedConfigConstants.DEFAULT_PATH,
                help=f"The path to the keepalived configuration file. Default: {KeepAlivedConfigConstants.DEFAULT_PATH}",
            ),
            value=dict(
                type="str",
                default="",
                help="The new value to set for the key, must be a valid config string (can also be a block without the key). The value will be prefixed with the key name if 'with_key_prefix' is true (default).",
            ),
            with_key_prefix=dict(
                type="bool",
                default=True,
                help="If true, the key will be prefixed to the value. If false, the value will be used as is.",
            ),
            create=dict(
                type="bool",
                default=False,
                help="If true, the key will be created if it does not exist in the config.",
            ),
            state=dict(
                type="str",
                default=self.SUPPORTED_STATES[0],
                choices=self.SUPPORTED_STATES,
                help="The state of the key. If 'present', the key will be set to the given value. If 'absent', the key will be removed from the config.",
            ),
        )

        # Initialize the module
        self._module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=True,
            required_if=[("state", self.SUPPORTED_STATES[0], ("value",))],
        )

        # Get the parameters
        file = self._module.params["file"]
        key = self._module.params["key"]
        value = self._module.params["value"]
        state = self._module.params["state"]
        with_key_prefix = self._module.params["with_key_prefix"]
        create = self._module.params["create"]

        if not os.path.exists(file):
            self._module.fail_json(msg=f"File '{file}' not existing!")

        try:
            parser = KeepAlivedConfigParser()
            cur_config = parser.parse_file(file)
            try:
                cur_item, parent_item = self.get_config_item(cur_config, key)
            except KeyError as e:
                if not (
                    create
                    and any("not found in config!" in arg for arg in e.args)
                    and state == "present"
                ):
                    raise e

                self.create_config_item(cur_config, key, value, with_key_prefix)
                self._persist_config(cur_config)
                self._module.exit_json(
                    changed=True, msg=f"Key '{key}' added to configuration!"
                )

            cur_value = cur_item.value

            if value == cur_value:
                self._module.exit_json(changed=False)

            self.update_config_item(
                parent_item, cur_item, value, state, with_key_prefix
            )

            self._persist_config(cur_config)

            self._module.exit_json(
                changed=True, msg=f"Key '{key}' updated in configuration!"
            )

        except Exception as e:
            self._module.fail_json(
                msg=f"Exception occured: {', '.join(arg for arg in e.args)}",
                exception=traceback.format_exc(),
            )

        # Exit the module and return the result
        self._module.exit_json(**self._result)

    def _persist_config(self, config: KeepAlivedConfig):
        if not isinstance(config, KeepAlivedConfig):
            raise TypeError(
                f"Invalid type '{type(config)}' for config! Expected '{KeepAlivedConfig.__class__.__name__}'"
            )

        if not self._module.check_mode:
            config.save()


if __name__ == "__main__":
    AnsibleKeepAlivedConfig().run_module()
