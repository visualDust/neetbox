from time import time
from typing import Union

from transformers import (
    TrainerCallback,
    TrainerControl,
    TrainerState,
    TrainingArguments,
)

from neetbox import action, add_hyperparams, add_scalar, logger, progress
from neetbox._protocol import get_timestamp


class NeetboxTrainerCallback(TrainerCallback):
    _SCALAR_NAME_IGNORED = [  # ignore scalars that are not useful metrics
        "epoch",
        "step",
        "total_flos",
        "total_mem",
        "total_mem_cpu",
        "total_mem_gpu",
        "eval_runtime",
        "eval_samples_per_second",
        "eval_steps_per_second",
        "train_runtime",
        "train_samples_per_second",
        "train_steps_per_second",
        "train_loss",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._status = {
            "last_update_epoch": None,
            "last_update_epoch_time": None,
            "last_update_step": None,
            "last_update_step_time": None,
        }
        self._scalars = {}
        self._launched_time_stamp = get_timestamp()

    def _extract_scalar(self, log, ignore_keys=[]):
        assert isinstance(log, dict), "log should be a dictionary."
        result = {}

        def recurse(curr, prefix=""):
            if isinstance(curr, dict):
                for key, value in curr.items():
                    if key in ignore_keys:
                        continue
                    new_prefix = f"{prefix}-{key}" if prefix else key
                    recurse(value, new_prefix)
            elif isinstance(curr, (int, float)):
                result[prefix] = curr
            elif isinstance(curr, tuple):
                for i, item in enumerate(curr):
                    if isinstance(item, (int, float)):
                        result[f"{prefix}-{i}"] = item
            # Ignore other types

        recurse(log)
        return result

    def on_train_begin(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ):
        """
        Event called at the beginning of training.
        """
        logger.info("Training started.")
        add_hyperparams(args.to_dict())

        @action(name="Trigger stop training")
        def trigger_should_training_stop():
            """Trigger TrainerControl.should_training_stop"""
            control.should_training_stop = not control.should_training_stop
            message = f"should_training_stop was set to: {control.should_training_stop}"
            logger.send_mention(message)
            return message

        @action(name="Trigger save model")
        def tirgger_should_save():
            """Trigger TrainerControl.should_save"""
            control.should_save = not control.should_save
            message = f"should_save was set to: {control.should_save}"
            logger.send_mention(message)
            return message

        @action(name="Trigger evaluate model")
        def trigger_should_evaluate():
            """Trigger TrainerControl.should_evaluate"""
            control.should_evaluate = not control.should_evaluate
            message = f"should_evaluate was set to: {control.should_evaluate}"
            logger.send_mention(message)
            return message

    def on_train_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ):
        """
        Event called at the end of training.
        """
        log_history = state.log_history[-1] if len(state.log_history) else None
        if log_history is None:
            return  # Skip logging
        log = dict(log_history)
        scalars = self._extract_scalar(log)
        logger.info(f"Training finished. Metrics: {scalars}")

    def on_save(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ):
        """
        Event called after a checkpoint save.
        """
        log_history = state.log_history[-1] if len(state.log_history) else None
        if log_history is None:
            return  # Skip logging
        log = dict(log_history)
        scalars = self._extract_scalar(log, ignore_keys=self._SCALAR_NAME_IGNORED)
        logger.info(f"Checkpoint saved on {scalars}")

    def on_step_end(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ):
        """
        Event called after each step.
        """
        # Update progress bar for epoch
        if not self._status["last_update_epoch"]:
            self._status["last_update_epoch"] = state.epoch
            self._status["last_update_epoch_time"] = time()
        else:
            if state.epoch != self._status["last_update_epoch"]:
                last_update_epoch = self._status["last_update_epoch"]
                last_update_epoch_time = self._status["last_update_epoch_time"]
                elapsed_time = time() - last_update_epoch_time
                rate = (state.epoch - last_update_epoch) / elapsed_time
                progress._update(
                    name="epoch",
                    what_is_current=f"of current step {int(state.global_step)}",
                    done=int(state.epoch),
                    total=int(args.num_train_epochs),
                    rate=rate,
                    timestamp=self._launched_time_stamp,
                )
                self._status["last_update_epoch"] = state.epoch
                self._status["last_update_epoch_time"] = time()

        # Update progress bar for step
        if not self._status["last_update_step"]:
            self._status["last_update_step"] = state.global_step
            self._status["last_update_step_time"] = time()
        else:
            if state.global_step != self._status["last_update_step"]:
                last_update_step = self._status["last_update_step"]
                last_update_step_time = self._status["last_update_step_time"]
                elapsed_time = time() - last_update_step_time
                rate = (state.global_step - last_update_step) / elapsed_time
                progress._update(
                    name="step",
                    what_is_current=f"of epoch {int(state.epoch)}",
                    done=int(state.global_step),
                    total=int(state.max_steps),
                    rate=rate,
                    timestamp=self._launched_time_stamp,
                )
                self._status["last_update_step"] = state.global_step
                self._status["last_update_step_time"] = time()

    def on_log(
        self,
        args: TrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        **kwargs,
    ):
        """
        Event called after logging.
        """
        log_history = state.log_history[-1] if len(state.log_history) else None
        if log_history is None:
            return  # Skip logging
        log = dict(log_history)
        scalars = self._extract_scalar(log, ignore_keys=self._SCALAR_NAME_IGNORED)

        for key, value in scalars.items():
            if key not in self._scalars or self._scalars[key] != value:
                add_scalar(
                    name=key,
                    x=state.global_step,
                    y=value,
                )
                self._scalars[key] = value
