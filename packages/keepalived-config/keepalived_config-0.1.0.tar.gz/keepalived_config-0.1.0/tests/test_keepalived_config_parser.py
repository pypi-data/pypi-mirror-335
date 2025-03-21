import os
import sys
import pytest
from unittest import mock

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
sys.path.append(SRC_DIR)

from keepalived_config.keepalived_config_parser import (
    KeepAlivedConfigParser,
    KeepAlivedConfig,
    KeepAlivedConfigBlock,
    KeepAlivedConfigParam,
)


def test_invalid_parse_string():
    invalid_items = [
        None,
        123,
        0.3,
        True,
        {"a": "b"},
        ["a", "b"],
    ]

    def verify_invalid_parse_string(item):
        with pytest.raises(TypeError):
            KeepAlivedConfigParser().parse_string(item)

    for item in invalid_items:
        verify_invalid_parse_string(item)

    with pytest.raises(ValueError):
        KeepAlivedConfigParser().parse_string("")

    # test with valid string but syntax error
    with pytest.raises(SyntaxError):
        KeepAlivedConfigParser().parse_string("global_defs {")
        KeepAlivedConfigParser().parse_string(
            """
    global_defs {
        notification_email {
            root@localhost
    }
    """
        )


def test_valid_parse_string():
    config_str = """
    global_defs {
        notification_email {
            root@localhost
        }
    }
    """

    cfg = KeepAlivedConfigParser().parse_string(config_str, keep_empty_lines=True)
    assert cfg
    assert len(cfg.params) == 3  # because of empyt lines at start and end
    assert all(
        (
            cfg.params[index].name == ""
            and cfg.params[index].value == ""
            and isinstance(cfg.params[index], KeepAlivedConfigParam)
        )
        for index in [0, 2]
    )
    assert (
        cfg.params[1].name == "global_defs"
        and cfg.params[1].value == ""
        and isinstance(cfg.params[1], KeepAlivedConfigBlock)
    )

    cfg = KeepAlivedConfigParser().parse_string(config_str, keep_empty_lines=False)
    assert cfg
    assert len(cfg.params) == 1
    assert (
        cfg.params[0].name == "global_defs"
        and cfg.params[0].value == ""
        and isinstance(cfg.params[0], KeepAlivedConfigBlock)
        and len(cfg.params[0].params) == 1
        and cfg.params[0].params[0].name == "notification_email"
        and cfg.params[0].params[0].value == ""
        and isinstance(cfg.params[0].params[0], KeepAlivedConfigBlock)
        and len(cfg.params[0].params[0].params) == 1
        and cfg.params[0].params[0].params[0].name == "root@localhost"
        and cfg.params[0].params[0].params[0].value == ""
        and isinstance(cfg.params[0].params[0].params[0], KeepAlivedConfigParam)
    )


def test_invalid_parse_file():
    invalid_files = [None, 123, 0.3, True, {"a": "b"}, ["a", "b"]]
    for file in invalid_files:
        with pytest.raises(TypeError):
            KeepAlivedConfigParser().parse_file(file)

    with pytest.raises(FileNotFoundError):
        KeepAlivedConfigParser().parse_file("my_file")


@mock.patch("os.path.exists", return_value=True)
@mock.patch("builtins.open", mock.mock_open(read_data=""))
def test_valid_parse_file(exists_mock: mock.MagicMock):

    def verify_valid_parse_file(keep_empty_lines):
        with (
            mock.patch(
                "keepalived_config.keepalived_config_parser.KeepAlivedConfigParser.parse_string",
                return_value=KeepAlivedConfig(config_file="my_file"),
            ) as mock_parse_string,
        ):
            exists_mock.reset_mock()
            cfg = KeepAlivedConfigParser().parse_file(
                "my_file", keep_empty_lines=with_empty_lines
            )
            exists_mock.assert_called_once_with("my_file")
            assert cfg
            assert isinstance(cfg, KeepAlivedConfig)
            assert cfg.config_file == "my_file"
            mock_parse_string.assert_called_once_with("", with_empty_lines)

    for with_empty_lines in [True, False]:
        verify_valid_parse_file(with_empty_lines)
