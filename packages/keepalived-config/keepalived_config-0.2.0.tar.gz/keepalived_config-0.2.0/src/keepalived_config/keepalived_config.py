import os

from keepalived_config.keepalived_config_constants import KeepAlivedConfigConstants
from keepalived_config.keepalived_config_param import KeepAlivedConfigParam
from keepalived_config.keepalived_config_block import KeepAlivedConfigBlock
from keepalived_config.keepalived_config_comment import (
    KeepAlivedConfigComment,
    KeepAlivedConfigCommentTypes,
)


class KeepAlivedConfig:

    def __init__(self, params: list = None, config_file=None):
        self._config_file = None
        self._params: list[KeepAlivedConfigBlock | KeepAlivedConfigParam] = []

        if config_file:
            self.config_file = config_file

        if params:
            self.set_params(params)

    @property
    def params(self):
        return self._params

    def set_params(self, params: list):
        if not isinstance(params, list):
            raise TypeError(f"Invalid params type '{type(params)}'! Expected 'list'")

        if list(
            filter(
                lambda c: not isinstance(c, KeepAlivedConfigParam)
                and not isinstance(c, KeepAlivedConfigBlock),
                params,
            )
        ):
            raise ValueError(
                f"Invalid params list! Expected list of {KeepAlivedConfigParam.__class__.__name__}' or {KeepAlivedConfigBlock.__class__.__name__}"
            )

        self._params = params

    @property
    def config_file(self):
        return self._config_file

    @config_file.setter
    def config_file(self, config_file: str):
        if not isinstance(config_file, str):
            raise TypeError(
                f"Invalid config_file type '{type(config_file)}'! Expected 'str'"
            )

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file '{config_file}' not found!")

        self._config_file = config_file

    def save(self, file=None):
        if not file:
            file = self.config_file

        with open(file, "w") as f:
            for item in self._params:
                f.write(item.to_str() + "\n")
