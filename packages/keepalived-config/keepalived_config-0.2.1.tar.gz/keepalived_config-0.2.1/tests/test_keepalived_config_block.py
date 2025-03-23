import os
import sys
import pytest

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
sys.path.append(SRC_DIR)

from keepalived_config.keepalived_config_block import (
    KeepAlivedConfigBlock,
    KeepAlivedConfigParam,
    KeepAlivedConfigConstants,
)
from keepalived_config.keepalived_config_comment import (
    KeepAlivedConfigCommentTypes,
    KeepAlivedConfigComment,
)


class InvalidValue:
    def __str__(self):
        raise Exception("Invalid __str__")


def test_valid_init():
    valid_items = [
        ("my_type", "myname", []),
        ("my_type", "", []),
        (
            "mytype",
            "myname",
            [KeepAlivedConfigComment("comment"), KeepAlivedConfigComment("comment")],
        ),
    ]

    for type_name, name, comments in valid_items:
        block = KeepAlivedConfigBlock(type_name=type_name, name=name, comments=comments)
        assert block.name == f"{type_name}{' ' + name if name else ''}"
        assert block.value == ""
        assert block.comments == comments


def test_invalid_init():
    invalid_items = [
        (InvalidValue(), "value", []),
        (True, "value", []),
        ("param", 123, {"a": "b"}),
        ("param", 0.3, ["comment"]),
        ("param", "value", ["comment", "comment"]),
    ]

    def test_invalid_init(type_name, name, comments):
        with pytest.raises(TypeError):
            KeepAlivedConfigBlock(type_name=type_name, name=name, comments=comments)

    for type_name, name, comments in invalid_items:
        test_invalid_init(type_name, name, comments)


def test_params():
    block = KeepAlivedConfigBlock("my_type")
    assert block.name == "my_type"
    assert block.params == []

    block.add_param(KeepAlivedConfigBlock("my_type_2"))
    assert len(block.params) == 1
    assert isinstance(block.params[0], KeepAlivedConfigBlock)

    block.add_param(KeepAlivedConfigParam("mykey", "myvalue"))
    assert len(block.params) == 2
    assert isinstance(block.params[1], KeepAlivedConfigParam)


def test_invalid_add_param():
    invalid_params = [None, 123, 3.2, True, "param", KeepAlivedConfigComment("comment")]

    block = KeepAlivedConfigBlock("my_type")
    assert block.params == []

    def test_invalid_add_param(param):
        with pytest.raises(TypeError):
            block.add_param(param)

    for param in invalid_params:
        test_invalid_add_param(param)


def test_to_str():
    block = KeepAlivedConfigBlock("my_type", "myname")

    assert block.to_str() == "my_type myname {\n}"
    assert (
        block.to_str(1)
        == f"{KeepAlivedConfigConstants.get_indent(1)}my_type myname {{\n"
        + f"{KeepAlivedConfigConstants.get_indent(1)}}}"
    )

    block.add_param(KeepAlivedConfigBlock("my_type_2", "myname_2"))
    block.params[0].add_param(KeepAlivedConfigParam("mysubkey", "mysubvalue"))
    block.add_param(
        KeepAlivedConfigParam(
            "mykey", "myvalue", comments=[KeepAlivedConfigComment("comment")]
        )
    )

    assert (
        block.to_str()
        == "my_type myname {\n"
        + f"{KeepAlivedConfigConstants.get_indent(1)}my_type_2 myname_2 {{\n"
        + f"{KeepAlivedConfigConstants.get_indent(2)}mysubkey mysubvalue\n"
        + f"{KeepAlivedConfigConstants.get_indent(1)}}}\n"
        + f"{KeepAlivedConfigConstants.get_indent(1)}{KeepAlivedConfigComment.COMMENT_INDICATOR} comment\n"
        + f"{KeepAlivedConfigConstants.get_indent(1)}mykey myvalue\n"
        + "}"
    )
