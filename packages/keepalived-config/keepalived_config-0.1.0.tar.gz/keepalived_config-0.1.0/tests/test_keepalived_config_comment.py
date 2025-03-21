import os
import sys
import pytest

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
sys.path.append(SRC_DIR)

from keepalived_config.keepalived_config_comment import (
    KeepAlivedConfigCommentTypes,
    KeepAlivedConfigComment,
    KeepAlivedConfigConstants,
)


class InvalidStr:
    def __str__(self):
        raise Exception("Invalid __str__")


def test_comment():
    comment = KeepAlivedConfigComment("This is a comment")
    assert comment.comment_str == "This is a comment"
    assert comment.type == KeepAlivedConfigCommentTypes.GENERIC


def test_inline_comment():
    comment = KeepAlivedConfigComment(
        "This is an inline comment", type=KeepAlivedConfigCommentTypes.INLINE
    )
    assert comment.comment_str == "This is an inline comment"
    assert (
        str(comment)
        == f"{KeepAlivedConfigConstants.get_indent(1)}{KeepAlivedConfigComment.COMMENT_INDICATOR} This is an inline comment"
    )
    assert comment.type == KeepAlivedConfigCommentTypes.INLINE


def test_invalid_comment_type():
    with pytest.raises(TypeError):
        KeepAlivedConfigComment("This is a comment", type="invalid")


def test_invalid_comment_str():
    with pytest.raises(TypeError):
        KeepAlivedConfigComment(InvalidStr())


def test_invalid_from_str():
    invalid_test_items = [None, 123, 3.2, True]

    for item in invalid_test_items:
        with pytest.raises(TypeError):
            KeepAlivedConfigComment.from_str(item)

    with pytest.raises(ValueError):
        KeepAlivedConfigComment.from_str(
            "This is an invalid comment missing the comment indicator"
        )


def test_from_str():

    with pytest.raises(ValueError):
        KeepAlivedConfigComment.from_str(
            "This is a comment missing the comment indicator"
        )

    comment = KeepAlivedConfigComment.from_str(
        KeepAlivedConfigComment.COMMENT_INDICATOR + " This is a normal comment"
    )
    assert comment.comment_str == "This is a normal comment"
    assert (
        str(comment)
        == KeepAlivedConfigComment.COMMENT_INDICATOR + " This is a normal comment"
    )
    assert comment.type == KeepAlivedConfigCommentTypes.GENERIC

    inline_comment = KeepAlivedConfigComment.from_str(
        "    shutdown_script_timeout SECONDS   "
        + KeepAlivedConfigComment.COMMENT_INDICATOR
        + " This is an inline comment"
    )
    assert inline_comment.comment_str == "This is an inline comment"
    assert (
        str(inline_comment)
        == f"{KeepAlivedConfigConstants.get_indent(1)}{KeepAlivedConfigComment.COMMENT_INDICATOR} This is an inline comment"
    )
    assert inline_comment.type == KeepAlivedConfigCommentTypes.INLINE

    with pytest.raises(ValueError):
        KeepAlivedConfigComment.from_str("    shutdown_script_timeout SECONDS   #")
        KeepAlivedConfigComment.from_str("    shutdown_script_timeout SECONDS   # ")
        KeepAlivedConfigComment.from_str("#")


def test_has_comment():
    assert KeepAlivedConfigComment.has_comment("    # This is a comment")
    assert KeepAlivedConfigComment.has_comment("    #")
    assert KeepAlivedConfigComment.has_comment("#")
    assert KeepAlivedConfigComment.has_comment("# ")
    assert KeepAlivedConfigComment.has_comment("# This is a comment")
    assert KeepAlivedConfigComment.has_comment("mykey    # This is a inline comment")
    assert not KeepAlivedConfigComment.has_comment("This is not a comment")
    assert not KeepAlivedConfigComment.has_comment("    This is not a comment")
