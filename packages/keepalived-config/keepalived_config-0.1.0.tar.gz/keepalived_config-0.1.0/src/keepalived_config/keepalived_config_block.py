from keepalived_config.keepalived_config_param import (
    KeepAlivedConfigParam,
    KeepAlivedConfigConstants,
)


class KeepAlivedConfigBlock(KeepAlivedConfigParam):
    def __init__(self, type_name: str, name: str = "", comments=None):
        if not isinstance(type_name, str):
            raise TypeError(
                f"Invalid type type_name '{type(type_name)}'! Expected 'str'"
            )

        super().__init__(
            name=f"{type_name}{' ' + name if name else ''}", value="", comments=comments
        )

        self._params: list[KeepAlivedConfigParam | KeepAlivedConfigBlock] = []

    @property
    def params(self):
        return self._params

    def add_param(self, param):
        if not isinstance(param, KeepAlivedConfigParam):
            raise TypeError(
                f"Invalid param type '{type(param)}'! Expected '{KeepAlivedConfigParam.__class__.__name__}'"
            )
        self._params.append(param)

    def to_str(self, indent_level=0):
        Str = f"{super().to_str(indent_level)} {{" + "\n"
        if self._params:
            Str += (
                "\n".join([param.to_str((indent_level + 1)) for param in self._params])
                + "\n"
            )
        Str += f"{KeepAlivedConfigConstants.get_indent(indent_level)}}}"

        return Str
