import os
import sys
import pytest

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
sys.path.append(SRC_DIR)

from keepalived_config.keepalived_config_param import (
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
        ("param", "value", []),
        ("param", 123, []),
        ("param", True, [KeepAlivedConfigComment("comment")]),
        (
            "param",
            "value",
            [KeepAlivedConfigComment("comment"), KeepAlivedConfigComment("comment")],
        ),
    ]

    for name, value, comments in valid_items:
        param = KeepAlivedConfigParam(name=name, value=value, comments=comments)
        assert param.name == name
        assert param.value == str(value)
        assert param.comments == comments


def test_invalid_init():
    invalid_items = [
        (123, "value", []),
        (True, "value", []),
        ("param", 123, {"a": "b"}),
        ("param", True, ["comment"]),
        ("param", "value", ["comment", "comment"]),
    ]

    def test_invalid_init(name, value, comments):
        with pytest.raises(TypeError):
            KeepAlivedConfigParam(name=name, value=value, comments=comments)

    for name, value, comments in invalid_items:
        test_invalid_init(name, value, comments)


def test_name():
    param = KeepAlivedConfigParam("param")
    assert param.name == "param"

    with pytest.raises(TypeError):
        param.name = 123


def test_value():
    param = KeepAlivedConfigParam("param")
    assert param.value == ""

    with pytest.raises(TypeError):
        param.value = InvalidValue()


def test_comments():
    param = KeepAlivedConfigParam("param")
    assert param.comments == []

    param.add_comment(KeepAlivedConfigComment("comment"))
    assert len(param.comments) == 1

    with pytest.raises(TypeError):
        param.add_comment("comment")

    param.add_comment(
        KeepAlivedConfigComment(
            "inline comment", type=KeepAlivedConfigCommentTypes.INLINE
        )
    )
    with pytest.raises(ValueError):
        param.add_comment(
            KeepAlivedConfigComment(
                "second inline comment", type=KeepAlivedConfigCommentTypes.INLINE
            )
        )

    with pytest.raises(TypeError):
        param.add_comments("comment")

    param.add_comments(
        [KeepAlivedConfigComment("comment"), KeepAlivedConfigComment("comment")]
    )
    assert len(param.comments) == 4


def test_to_str():
    param = KeepAlivedConfigParam("param", value="value")
    assert param.to_str() == "param value"
    assert param.to_str(1) == f"{KeepAlivedConfigConstants.get_indent(1)}param value"

    param.add_comment(
        KeepAlivedConfigComment(
            "inline comment", type=KeepAlivedConfigCommentTypes.INLINE
        )
    )
    assert (
        param.to_str()
        == f"param value{KeepAlivedConfigConstants.get_indent(1)}{KeepAlivedConfigComment.COMMENT_INDICATOR} inline comment"
    )

    param.add_comment(KeepAlivedConfigComment("comment"))
    assert (
        param.to_str()
        == f"{KeepAlivedConfigComment.COMMENT_INDICATOR} comment"
        + "\n"
        + f"param value{KeepAlivedConfigConstants.get_indent(1)}{KeepAlivedConfigComment.COMMENT_INDICATOR} inline comment"
    )
