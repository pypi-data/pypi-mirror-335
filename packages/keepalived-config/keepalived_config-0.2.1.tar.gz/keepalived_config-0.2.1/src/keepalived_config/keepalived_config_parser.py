import re
import os

from keepalived_config.keepalived_config import (
    KeepAlivedConfig,
    KeepAlivedConfigParam,
    KeepAlivedConfigBlock,
    KeepAlivedConfigComment,
)


class KeepAlivedConfigParser:
    KEY_VALUE_REGEX = re.compile(
        r"^ *(?![!#])(?P<key>[\w\-]+)(?: +(?P<value>[^{}\n\r]+))?(?: +(?P<block_type>[{}]))?$"
    )

    def __init__(self):
        self._config: KeepAlivedConfig = None
        self._items: list[KeepAlivedConfigParam | KeepAlivedConfigBlock] = []
        self._block_nesting_level = 0
        self._comments: list[KeepAlivedConfigComment] = []
        self._parse_source = None

    def parse_file(
        self, config_file, keep_empty_lines: bool = True
    ) -> KeepAlivedConfig:
        self._config = KeepAlivedConfig(config_file=config_file)

        self._parse_source = self._config.config_file

        with open(self._config.config_file, "r") as f:
            contents = f.read()

        return self.parse_string(contents, keep_empty_lines)

    def parse_string(
        self, config_string: str, keep_empty_lines: bool = True
    ) -> KeepAlivedConfig:

        if not isinstance(config_string, str):
            raise TypeError(
                f"Invalid config_string type '{type(config_string)}'! Expected 'str'"
            )

        if not config_string:
            raise ValueError("Empty config_string provided!")

        self._keep_empty_lines = keep_empty_lines
        if not self._config:
            self._config = KeepAlivedConfig()

        if not self._parse_source:
            self._parse_source = "string"

        self._parse_config_file_contents(config_string.split("\n"))

        if self._block_nesting_level > 0:
            raise SyntaxError(
                f"Unexpected end of file! Missing '}}' at nesting level {self._block_nesting_level}"
            )

        self._config.params.extend(self._items)

        return self._config

    def _parse_config_file_contents(self, file_contents: list) -> list:
        self._items = []

        for line_nr, line in enumerate(file_contents, 1):
            self._parse_config_file_line(line.strip(), line_nr)

    def _parse_config_file_line(self, line: str, line_nr: int):
        active_block = self._get_active_block(self._items, self._block_nesting_level)

        if not line and self._keep_empty_lines:
            if active_block:
                active_block.params.append(KeepAlivedConfigParam("", ""))
            else:
                self._items.append(KeepAlivedConfigParam("", ""))
            return

        if line and KeepAlivedConfigComment.has_comment(line):
            self._comments.append(KeepAlivedConfigComment.from_str(line))
            line = re.sub(KeepAlivedConfigComment.COMMENT_REGEX, "", line)

        if not line:
            return

        if line.startswith("}") and self._block_nesting_level == 0:
            raise ValueError(
                f"Unexpected '}}' found at nesting level 0! Reference: {self._parse_source}@{line_nr}: '{line}'"
            )

        if line.startswith("}") and self._block_nesting_level > 0:
            self._block_nesting_level -= 1
            active_block = self._get_active_block(
                self._items, self._block_nesting_level
            )
            return

        match = re.match(self.KEY_VALUE_REGEX, line)
        if not match:
            # there are special cases where we have a single value without a key, which is not catched by the regex
            items = line.split(" ")
            if len(items) == 1:
                items = [items[0], None, None]
            else:
                raise ValueError(
                    f"Unexpected line format in {self._config.config_file}@{line_nr}: '{line}'"
                )
        else:
            items = match.groups()
        valid_items = len(list(filter(None, items)))
        if valid_items < 1 or valid_items > 3:
            raise ValueError(
                f"Unexpected line format in {self._parse_source}@{line_nr}: '{line}'"
            )

        key, value, block_type = items

        if block_type and block_type == "{":
            self._block_nesting_level += 1
            new_block = KeepAlivedConfigBlock(
                key, name=value, comments=self._comments.copy()
            )
            self._comments.clear()
            if active_block:
                active_block.add_param(new_block)
            else:
                self._items.append(new_block)
            return

        if valid_items == 1:
            value = ""

        # normal case where we have a key and a value
        config_param = KeepAlivedConfigParam(key, value, comments=self._comments.copy())
        self._comments.clear()
        if active_block:
            active_block.add_param(config_param)
        else:
            self._items.append(config_param)

    def _get_active_block(self, config: list, nesting_level: int):
        if not isinstance(config, list):
            raise TypeError(f"Invalid config type '{type(config)}'! Expected 'list'")
        if not isinstance(nesting_level, int):
            raise TypeError(
                f"Invalid nesting_level type '{type(nesting_level)}'! Expected 'int'"
            )
        if nesting_level < 0:
            raise ValueError(
                f"Invalid nesting_level value '{nesting_level}'! Expected '>= 0'"
            )

        if nesting_level == 0:
            return None

        active_block = (
            config[-1] if isinstance(config[-1], KeepAlivedConfigBlock) else None
        )
        for _ in range(1, nesting_level, 1):
            if not active_block:
                return None
            if not active_block.params or not isinstance(
                active_block.params[-1], KeepAlivedConfigBlock
            ):
                return None
            active_block = active_block.params[-1]
        return active_block
