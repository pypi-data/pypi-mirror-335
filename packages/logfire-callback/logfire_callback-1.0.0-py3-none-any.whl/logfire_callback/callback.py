import importlib.util
import json
import os

import logfire
from transformers import (
    AutoModelForMaskedLM,
    TrainerCallback,
    TrainerControl,
    TrainerState,
    TrainingArguments,
)


def is_logfire_available() -> bool:
    """Check if the logfire package is available.

    Returns:
        bool: True if logfire is available, False otherwise.
    """
    return importlib.util.find_spec("logfire") is not None


class LogfireCallback(TrainerCallback):
    """A callback for logging training events to Logfire.

    This callback integrates with the Logfire logging service to track training progress, metrics, and events during model training. It inherits from HuggingFace's TrainerCallback and logs important events like training start, end, and periodic metric updates.

    Note:
        Requires the `logfire` package to be installed. Install with `pip install logfire`. A Logfire API token must be set in the LOGFIRE_TOKEN environment variable.

    Attributes:
        _logfire: The logfire module instance for making logging calls.
        _logfire_token: The API token for Logfire authentication.
        _initialized: Boolean flag indicating if the callback has been initialized.
    """

    def __init__(self) -> None:
        """Initialize the LogfireCallback.

        Raises:
            RuntimeError: If the logfire package is not installed.
        """
        if not is_logfire_available():
            raise RuntimeError(
                "LogfireCallback requires `logfire` to be installed. Run `pip install logfire`."
            )

        self._logfire = logfire
        self._logfire_token = os.getenv("LOGFIRE_TOKEN", None)
        self._initialized = False

        self._logfire.configure(
            token=self._logfire_token, console=False, inspect_arguments=False
        )

    from typing import Any, Optional

    def on_train_begin(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        model: AutoModelForMaskedLM | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Called when training begins.

        Logs the initial training parameters and configuration to Logfire.

        Args:
            args (TrainingArguments): Training arguments and hyperparameters.
            state (TrainerState): Current state of the trainer.
            control (TrainerControl): Training control object.
            model (AutoModelForMaskedLM | None, optional): The model being trained. Defaults to None.
            **kwargs (dict[str, Any]): Additional keyword arguments.

        Note:
            Only logs when running on the main process (is_local_process_zero) to avoid duplicate logs in distributed training.
        """
        if self._logfire and state.is_local_process_zero:

            def make_serializable(obj: TrainingArguments) -> object:
                """Convert training arguments to a JSON-serializable format.

                Args:
                    obj (TrainingArguments): The object to make serializable.

                Returns:
                    object: A JSON-serializable version of the input object.
                """
                if hasattr(obj, "__dict__"):
                    return {
                        k: make_serializable(v)
                        for k, v in obj.__dict__.items()
                        if not k.startswith("_") and not callable(v)
                    }
                elif isinstance(obj, list | tuple):
                    return [make_serializable(x) for x in obj]
                elif isinstance(obj, dict):
                    return {k: make_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, int | float | str | bool | type(None)):
                    return obj
                else:
                    return str(obj)

            args_dict = make_serializable(args)

            self._logfire.info(
                "Training started with the following parameters: {args}",
                args=json.dumps(args_dict),
            )

    def on_train_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs: dict[str, Any],
    ) -> None:
        """Called when training ends.

        Logs the completion of training to Logfire.

        Args:
            args (TrainingArguments): Training arguments and hyperparameters.
            state (TrainerState): Final state of the trainer.
            control (TrainerControl): Training control object.
            **kwargs (dict[str, Any]): Additional keyword arguments.

        Note:
            Only logs when running on the main process (is_local_process_zero) to avoid
            duplicate logs in distributed training.
        """
        if self._logfire and state.is_local_process_zero:
            self._logfire.info(
                "Training successfully completed.",
            )

    def on_log(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        logs: dict[str, Any] | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Called when training metrics are logged.

        Sends training metrics and logs to Logfire for monitoring and visualization.

        Args:
            args (TrainingArguments): Training arguments and hyperparameters.
            state (TrainerState): Current state of the trainer.
            control (TrainerControl): Training control object.
            logs (dict[str, Any] | None, optional): Dictionary of logs to record. Defaults to None.
            **kwargs (dict[str, Any]): Additional keyword arguments.

        Note:
            Only logs when running on the main process (is_local_process_zero) to avoid duplicate logs in distributed training.

            The logs dictionary typically contains metrics such as:
            - loss: Training loss
            - learning_rate: Current learning rate
            - epoch: Current epoch number
            - step: Current training step
            - eval_loss: Evaluation loss (during evaluation)
            - eval_runtime: Evaluation runtime
            - eval_samples_per_second: Evaluation throughput
            - eval_steps_per_second: Evaluation steps per second
        """
        if self._logfire and state.is_local_process_zero:
            self._logfire.info(
                "{logs}",
                logs=logs,
            )
