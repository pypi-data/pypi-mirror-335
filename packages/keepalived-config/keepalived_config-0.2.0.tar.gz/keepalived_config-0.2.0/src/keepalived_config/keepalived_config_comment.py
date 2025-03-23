import enum
import re

from keepalived_config.keepalived_config_constants import KeepAlivedConfigConstants


class KeepAlivedConfigCommentTypes(enum.Enum):
    GENERIC = 0
    INLINE = 1


class KeepAlivedConfigComment:
    COMMENT_INDICATOR = "#"
    COMMENT_REGEX = re.compile(
        r"(^ *[#!](?P<comment>((.+)|())$))|( +[#!] (?P<inline_comment>.*$))"
    )

    @classmethod
    def from_str(cls, comment_str: str) -> "KeepAlivedConfigComment":
        if not isinstance(comment_str, str):
            raise TypeError(
                f"Invalid comment_str type '{type(comment_str)}'! Expected 'str'"
            )

        match = cls.COMMENT_REGEX.search(comment_str)
        if not match:
            raise ValueError(f"Invalid comment string '{comment_str}'")

        if match.group("inline_comment"):
            return cls(
                match.group("inline_comment"), type=KeepAlivedConfigCommentTypes.INLINE
            )

        if match.group("comment"):
            return cls(match.group("comment").strip())

        raise ValueError(f"Invalid comment string '{comment_str}'")

    @classmethod
    def has_comment(cls, line: str) -> bool:
        return cls.COMMENT_REGEX.search(line.strip()) is not None

    def __init__(
        self,
        comment_str: str,
        type: KeepAlivedConfigCommentTypes = KeepAlivedConfigCommentTypes.GENERIC,
    ):
        self._comment_str = None
        self._type = None

        self.comment_str = comment_str
        self.type = type

    @property
    def comment_str(self):
        return self._comment_str

    @comment_str.setter
    def comment_str(self, comment_str: str):
        if isinstance(comment_str, str):
            self._comment_str = comment_str.rstrip()
            return

        try:
            self._comment_str = str(comment_str).rstrip()
        except:
            raise TypeError(
                f"Invalid comment_str type '{type(comment_str)}'! Expected 'str'"
            )

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type: KeepAlivedConfigCommentTypes):
        if not isinstance(type, KeepAlivedConfigCommentTypes):
            raise TypeError(
                f"Invalid type type '{type(type)}'! Expected '{KeepAlivedConfigCommentTypes.__class__.__name__}'"
            )
        self._type = type

    def __str__(self):
        Str = f"{self.COMMENT_INDICATOR} {self._comment_str}"
        if self._type == KeepAlivedConfigCommentTypes.INLINE:
            Str = KeepAlivedConfigConstants.get_indent(1) + Str
        return Str
