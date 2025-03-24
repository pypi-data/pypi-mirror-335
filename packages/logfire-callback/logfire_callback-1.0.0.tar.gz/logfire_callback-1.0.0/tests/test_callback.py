import json
import os
from unittest.mock import patch

import pytest
from transformers import TrainerControl, TrainerState, TrainingArguments

from logfire_callback import LogfireCallback, is_logfire_available


def test_is_logfire_available_true():
    """Test is_logfire_available when logfire is installed."""
    assert is_logfire_available() is True


@pytest.fixture
def mock_logfire():
    """Fixture to mock the logfire module."""
    with patch("logfire_callback.callback.logfire") as mock:
        yield mock


@pytest.fixture
def mock_env_token():
    """Fixture to mock the LOGFIRE_TOKEN environment variable."""
    with patch.dict(os.environ, {"LOGFIRE_TOKEN": "test-token"}):
        yield


@pytest.fixture
def callback(mock_logfire, mock_env_token):
    """Fixture to create a LogfireCallback instance with mocked dependencies."""
    return LogfireCallback()


@pytest.fixture
def training_args():
    """Fixture to create TrainingArguments."""
    return TrainingArguments(output_dir="./test-output")


@pytest.fixture
def trainer_state():
    """Fixture to create TrainerState with is_local_process_zero=True."""
    state = TrainerState()
    state.is_local_process_zero = True
    return state


@pytest.fixture
def trainer_control():
    """Fixture to create TrainerControl."""
    return TrainerControl()


def test_callback_initialization(mock_logfire, mock_env_token):
    """Test LogfireCallback initialization."""
    callback = LogfireCallback()
    assert callback._logfire == mock_logfire
    assert callback._logfire_token == "test-token"
    assert callback._initialized is False
    mock_logfire.configure.assert_called_once_with(
        token="test-token", console=False, inspect_arguments=False
    )


def test_on_train_begin(callback, training_args, trainer_state, trainer_control):
    """Test on_train_begin method."""
    # Create test objects for all serialization cases
    class CustomObject:
        def __init__(self):
            # Test list serialization
            self.list_value = [1, 2, "test"]
            # Test tuple serialization explicitly
            self.tuple_value = (3, 4, "tuple")
            # Test dict serialization
            self.dict_value = {"key": [5, 6]}
            # Test nested tuple containing a list
            self.nested_tuple = (["a", "b"], "c")
            # Test nested list containing a tuple
            self.nested_list = ["x", (1, 2)]
        def __str__(self):
            return "custom_object"

    training_args.nested_param = CustomObject()

    callback.on_train_begin(training_args, trainer_state, trainer_control)

    # Verify that logfire.info was called with training parameters
    callback._logfire.info.assert_called_once()
    call_args = callback._logfire.info.call_args
    assert "Training started with the following parameters" in call_args[0][0]

    # Verify each serialization case
    args_str = call_args[1]['args']
    args_dict = json.loads(args_str)
    assert 'nested_param' in args_dict
    nested = args_dict['nested_param']
    assert isinstance(nested, dict)

    # Verify list serialization
    assert nested['list_value'] == [1, 2, "test"]
    # Verify tuple serialization (converted to list)
    assert nested['tuple_value'] == [3, 4, "tuple"]
    # Verify dict serialization with nested list
    assert nested['dict_value'] == {"key": [5, 6]}
    # Verify nested tuple with list
    assert nested['nested_tuple'] == [["a", "b"], "c"]
    # Verify nested list with tuple
    assert nested['nested_list'] == ["x", [1, 2]]


def test_on_train_end(callback, training_args, trainer_state, trainer_control):
    """Test on_train_end method."""
    callback.on_train_end(training_args, trainer_state, trainer_control)

    # Verify that logfire.info was called with completion message
    callback._logfire.info.assert_called_once_with(
        "Training successfully completed.",
    )


def test_on_log(callback, training_args, trainer_state, trainer_control):
    """Test on_log method."""
    test_logs = {
        "loss": 0.5,
        "learning_rate": 0.001,
        "epoch": 1,
    }

    callback.on_log(training_args, trainer_state, trainer_control, logs=test_logs)

    # Verify that logfire.info was called with the logs
    callback._logfire.info.assert_called_once_with(
        "{logs}",
        logs=test_logs,
    )


def test_on_log_none_logs(callback, training_args, trainer_state, trainer_control):
    """Test on_log method with None logs."""
    callback.on_log(training_args, trainer_state, trainer_control, logs=None)

    # Verify that logfire.info was called with None logs
    callback._logfire.info.assert_called_once_with(
        "{logs}",
        logs=None,
    )


def test_not_main_process(callback, training_args, trainer_control):
    """Test callbacks when not on main process."""
    state = TrainerState()
    state.is_local_process_zero = False

    # Test all callback methods with explicit test for each method
    callback.on_train_begin(training_args, state, trainer_control)
    assert callback._logfire.info.call_count == 0, "on_train_begin should not log on non-main process"

    callback.on_train_end(training_args, state, trainer_control)
    assert callback._logfire.info.call_count == 0, "on_train_end should not log on non-main process"

    callback.on_log(training_args, state, trainer_control, logs={"loss": 0.5})
    assert callback._logfire.info.call_count == 0, "on_log should not log on non-main process"
