import re

from keepalived_config.keepalived_config_constants import KeepAlivedConfigConstants
from keepalived_config.keepalived_config_comment import (
    KeepAlivedConfigCommentTypes,
    KeepAlivedConfigComment,
)


class KeepAlivedConfigParam:
    def __init__(self, name, value: str = "", comments=None):
        self._name = None
        self._value = None

        self.name = name
        self.value = value
        self._comments: list[KeepAlivedConfigComment] = []

        if comments:
            self.add_comments(comments)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        if not isinstance(name, str):
            raise TypeError(f"Invalid name type '{type(name)}'! Expected 'str'")
        self._name = name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: str):
        if isinstance(value, str):
            self._value = value
            return

        try:
            self._value = str(value)
        except:
            raise TypeError(f"Invalid value type '{type(value)}'! Expected 'str'")

    @property
    def comments(self):
        return self._comments

    def add_comment(self, comment: KeepAlivedConfigComment):
        if not isinstance(comment, KeepAlivedConfigComment):
            raise TypeError(
                f"Invalid comment type '{type(comment)}'! Expected '{KeepAlivedConfigComment.__class__.__name__}'"
            )

        # we can only have 1 inline comment
        if list(
            filter(
                lambda c: comment.type == KeepAlivedConfigCommentTypes.INLINE
                and c.type == comment.type,
                self._comments,
            )
        ):
            raise ValueError(
                f"Inline comment already exists for param '{self._name}': '{comment.comment_str}'"
            )

        self._comments.append(comment)

    def add_comments(self, comments: list):
        if not isinstance(comments, list):
            raise TypeError(
                f"Invalid comments type '{type(comments)}'! Expected 'list'"
            )
        for comment in comments:
            self.add_comment(comment)

    def to_str(self, indent_level=0):
        Str = ""
        if self.__get_generic_comments__():
            Str = (
                "\n".join(
                    [
                        f"{KeepAlivedConfigConstants.get_indent(indent_level)}{str(comment)}"
                        for comment in self.__get_generic_comments__()
                    ]
                )
                + "\n"
            )
        Str += f"{KeepAlivedConfigConstants.get_indent(indent_level)}{self._name}{' ' + self._value if self._value else ''}{self.__get_inline_comment__() if self.__get_inline_comment__() else ''}"

        if re.match(r"^ *$", Str):
            return ""
        return Str

    def __get_inline_comment__(self) -> str:
        inline_comment: list[KeepAlivedConfigComment] = list(
            filter(
                lambda c: c.type == KeepAlivedConfigCommentTypes.INLINE, self._comments
            )
        )

        return str(inline_comment[0]) if inline_comment else ""

    def __get_generic_comments__(self) -> list[KeepAlivedConfigComment]:
        return list(
            filter(
                lambda c: c.type == KeepAlivedConfigCommentTypes.GENERIC, self._comments
            )
        )
