from time import time

from cv2 import add
from transformers import (
    TrainerCallback,
    TrainerControl,
    TrainerState,
    TrainingArguments,
)

from neetbox import add_hyperparams, add_scalar, logger, progress
from neetbox._protocol import get_timestamp


class NeetboxTrainerCallback(TrainerCallback):
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
        logger.info("Training finished.")

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
        logger.info(f"Checkpoint saved.")

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
        # Check if anything in last log is scalar and update
        name_ignored = [
            "epoch",
            "step",
            "total_flos",
            "total_mem",
            "total_mem_cpu",
            "total_mem_gpu",
            "eval_runtime",
            "eval_samples_per_second",
            "eval_steps_per_second",
        ]
        for key, value in log.items():
            if key not in name_ignored and isinstance(value, (int, float)):
                if key not in self._scalars or self._scalars[key] != value:
                    add_scalar(
                        name=key,
                        x=state.global_step,
                        y=value,
                    )
                self._scalars[key] = value
