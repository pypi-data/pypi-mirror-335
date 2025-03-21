import os
import sys
import json
import pytest
from unittest import mock
from io import TextIOWrapper, BufferedReader, BytesIO

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
sys.path.append(SRC_DIR)

from keepalived_config.ansible_keepalived_config import (
    AnsibleKeepAlivedConfig,
    KeepAlivedConfig,
    KeepAlivedConfigConstants,
    AnsibleModule,
)
from keepalived_config.keepalived_config_param import KeepAlivedConfigParam
from keepalived_config.keepalived_config_block import KeepAlivedConfigBlock
import ansible.module_utils.basic as ansible_basic


class AnsibleInputMock:
    def __init__(self, input_json: dict = {}, file_path: str = None, path_exists=True):
        if not isinstance(input_json, dict):
            raise TypeError("Invalid input_json type! Expected 'dict'")

        if len(input_json) == 0:
            self.input_json = ""
        else:
            self.input_json = json.dumps({
                "ANSIBLE_MODULE_ARGS": input_json,
            }, indent=None) + "\n"

        self.file_path = file_path
        self.path_exists = path_exists

        self.orig_stdin = sys.stdin
        self.stdin_mock = None

        self.orig_sys_argv = sys.argv
        self.sys_argv_mock = None

        self.orig_os_path_exists = os.path.exists
        self.os_path_exists_mock = None

    def __enter__(self):
        self.stdin_mock = TextIOWrapper(
            BufferedReader(
                BytesIO(self.input_json.encode())
            ),
        )
        self.sys_argv_mock = (
            [self.file_path] if self.file_path else [os.path.basename(__file__)]
        )
        self.os_path_exists_mock = mock.patch(
            "os.path.exists", new_callable=lambda path: self.path_exists
        )
        os.path.exists = self.os_path_exists_mock
        sys.argv = self.sys_argv_mock
        sys.stdin = self.stdin_mock

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdin = self.orig_stdin
        sys.argv = self.orig_sys_argv
        os.path.exists = self.orig_os_path_exists


class AnsibleModuleCheckMock(AnsibleModule):
    def __init__(self, *args, **kwargs):
        ansible_basic._ANSIBLE_ARGS = None
        super().__init__(*args, **kwargs)
        self.check_mode = True


def test_noparams_run_module():
    with AnsibleInputMock(), pytest.raises(SystemExit) as exit_mock:
        AnsibleKeepAlivedConfig().run_module()
    exit_mock.value.code == 1


def test_invalidparams_run_module():
    params = {
        "file": "file",
        "key": "key",
        "value": "value",
        "state": "state",
    }

    with AnsibleInputMock(params), pytest.raises(SystemExit) as exit_mock:
        AnsibleKeepAlivedConfig().run_module()
    exit_mock.value.code == 1


def test_requiredparams_run_module():
    invalid_param_combinations = [
        {
            # Missing always required 'key' parameter
            "file": "file",
            "value": "value",
            "state": "present",
        },
        {
            # Missing always required 'value' parameter when state is 'present'
            "key": "key",
            "state": "present",
        },
    ]
    for params in invalid_param_combinations:
        with AnsibleInputMock(params), pytest.raises(SystemExit) as exit_mock:
            AnsibleKeepAlivedConfig().run_module()
        exit_mock.value.code == 1


@mock.patch("builtins.open", new_callable=mock.mock_open, read_data="key value\n")
def test_valid_unchanged_run_module(open_mock, capsys):
    params = {
        "file": "my_file",
        "key": "key",
        "value": "value",
        "state": "present",
    }
    ansible_basic._ANSIBLE_ARGS = None
    with AnsibleInputMock(params), pytest.raises(SystemExit) as exit_mock:
        AnsibleKeepAlivedConfig().run_module()

    captured = capsys.readouterr()

    open_mock.assert_called_once_with("my_file", "r")
    assert exit_mock.value.code == 0

    ansible_result = json.loads(captured.out)
    assert ansible_result["changed"] == False


@mock.patch("builtins.open", new_callable=mock.mock_open, read_data="key value\n")
def test_valid_changed_check_run_module(open_mock, capsys):
    params = {
        "key": "key",
        "value": "new_value",
        "state": "present",
    }

    def verify_changed(params):
        with mock.patch(
            "keepalived_config.ansible_keepalived_config.AnsibleModule",
            new=AnsibleModuleCheckMock,
        ), AnsibleInputMock(params), pytest.raises(SystemExit) as exit_mock:
            AnsibleKeepAlivedConfig().run_module()
        captured = capsys.readouterr()
        ansible_result = json.loads(captured.out)
        assert exit_mock.value.code == 0
        assert ansible_result["changed"] == True

    # check for the default file path
    verify_changed(params)
    open_mock.assert_called_once_with(KeepAlivedConfigConstants.DEFAULT_PATH, "r")

    # check for the given file path
    open_mock.reset_mock()
    params["file"] = "my_file"
    verify_changed(params)
    open_mock.assert_called_with("my_file", "r")

    # check for the absent state
    open_mock.reset_mock()
    params["state"] = "absent"
    verify_changed(params)
    open_mock.assert_called_with("my_file", "r")


@mock.patch("builtins.open", new_callable=mock.mock_open, read_data="key value\n")
def test_valid_changed_run_module(open_mock, capsys):
    params = {
        "key": "key",
        "value": "new_value",
        "file": "my_file",
    }

    for state in AnsibleKeepAlivedConfig().SUPPORTED_STATES:
        open_mock.reset_mock()
        params["state"] = state

        with AnsibleInputMock(params), pytest.raises(SystemExit) as exit_mock:
            AnsibleKeepAlivedConfig().run_module()

        captured = capsys.readouterr()
        ansible_result = json.loads(captured.out)
        assert open_mock.call_args_list == [
            mock.call("my_file", "r"),
            mock.call("my_file", "w"),
        ]
        assert exit_mock.value.code == 0
        assert ansible_result["changed"] == True


@mock.patch("os.path.exists", return_value=True)
def test_invalid_get_config_item(os_path_exists_mock):
    invalid_items = [
        (KeepAlivedConfig(), 123),
        (KeepAlivedConfig(), None),
        (None, "key"),
        (123, "key"),
        (True, "key"),
        ("string", "key"),
    ]

    def verify_invalid(config, key):
        with pytest.raises(TypeError):
            AnsibleKeepAlivedConfig().get_config_item(config, key)

    for config, key in invalid_items:
        verify_invalid(config, key)


def test_invalidkey_get_config_item():
    with pytest.raises(KeyError), mock.patch("os.path.exists", return_value=True):
        AnsibleKeepAlivedConfig().get_config_item(KeepAlivedConfig(), "key")


@mock.patch("os.path.exists", return_value=True)
def test_valid_get_config_item(os_path_exists_mock):
    config = KeepAlivedConfig()

    config.set_params(
        [
            KeepAlivedConfigBlock("my_type", "myname"),
            KeepAlivedConfigParam("param", "value"),
        ]
    )
    assert AnsibleKeepAlivedConfig().get_config_item(config, "param") == (
        config.params[1],
        config,
    )
    assert AnsibleKeepAlivedConfig().get_config_item(config, "my_type myname") == (
        config.params[0],
        config,
    )

    config.params[0].add_param(KeepAlivedConfigParam("param2", "value2"))
    assert AnsibleKeepAlivedConfig().get_config_item(
        config, "my_type myname.param2"
    ) == (
        config.params[0].params[0],
        config.params[0],
    )

    config.params[0].add_param(KeepAlivedConfigBlock("mynewtype"))
    config.params[0].params[1].add_param(
        KeepAlivedConfigParam("mynewparam", "mynewvalue")
    )
    assert AnsibleKeepAlivedConfig().get_config_item(
        config, "my_type myname.mynewtype.mynewparam"
    ) == (
        config.params[0].params[1].params[0],
        config.params[0].params[1],
    )


def test_invalid_update_config_item():
    type_errors = [
        (None, KeepAlivedConfigParam("param", "value"), "new_value", "present"),
        (KeepAlivedConfig(), None, "new_value", "present"),
        (KeepAlivedConfig(), KeepAlivedConfigParam("param", "value"), None, "present"),
        (
            KeepAlivedConfig(),
            KeepAlivedConfigParam("param", "value"),
            "new_value",
            None,
        ),
    ]

    def verify_error(error, *items):
        with pytest.raises(error):
            AnsibleKeepAlivedConfig().update_config_item(*items)

    for items in type_errors:
        verify_error(TypeError, *items)

    verify_error(
        ValueError,
        KeepAlivedConfig(),
        KeepAlivedConfigParam("param", "value"),
        "new_value",
        "invalid",
    )

    verify_error(
        ValueError,
        KeepAlivedConfig(),
        KeepAlivedConfigParam("param", "value"),
        "new_value",
        "absent",
    )


def test_valid_present_update_config_item():
    config = KeepAlivedConfig()
    config.set_params(
        [
            KeepAlivedConfigBlock("my_type", "myname"),
            KeepAlivedConfigParam("param", "value"),
        ]
    )

    AnsibleKeepAlivedConfig().update_config_item(
        config, config.params[1], "new_value", "present"
    )
    assert config.params[1].value == "new_value"

    config.params[0].add_param(KeepAlivedConfigBlock("mynewtype"))
    config.params[0].params[0].add_param(
        KeepAlivedConfigParam("mynewparam", "mynewvalue")
    )
    AnsibleKeepAlivedConfig().update_config_item(
        config.params[0],
        config.params[0].params[0],
        """mychangedtype mychangedname {
    mychangedparam mychangedvalue
}""",
        "present",
    )
    assert (
        isinstance(config.params[0].params[0], KeepAlivedConfigBlock)
        and config.params[0].params[0].name == "mychangedtype mychangedname"
        and isinstance(config.params[0].params[0].params[0], KeepAlivedConfigParam)
        and config.params[0].params[0].params[0].name == "mychangedparam"
        and config.params[0].params[0].params[0].value == "mychangedvalue"
    )


def test_valid_absent_update_config_item():
    config = KeepAlivedConfig()
    config.set_params(
        [
            KeepAlivedConfigBlock("my_type", "myname"),
            KeepAlivedConfigParam("param", "value"),
        ]
    )

    AnsibleKeepAlivedConfig().update_config_item(
        config, config.params[1], "new_value", "absent"
    )
    assert len(config.params) == 1
    assert config.params[0].name == "my_type myname"

    config.params[0].add_param(KeepAlivedConfigBlock("mynewtype"))
    config.params[0].params[0].add_param(
        KeepAlivedConfigParam("mynewparam", "mynewvalue")
    )
    AnsibleKeepAlivedConfig().update_config_item(
        config.params[0],
        config.params[0].params[0],
        """mychangedtype mychangedname {
    mychangedparam mychangedvalue
}""",
        "absent",
    )
    assert len(config.params[0].params) == 0
