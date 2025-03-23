import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)


class ProgressTracker:
    def start(self, total=None, **kwargs): ...

    def update_progress(self, value): ...

    def done(self): ...


class TqdmTracker(ProgressTracker):
    def __init__(self, tqdm_type: str = "std") -> None:
        self.tqdm_type = tqdm_type
        self._last_value = 0

    def should_skip(self):
        return self.total <= 4 * 1024

    def start(self, total=None, **kwargs):
        self.total = total
        self._last_value = 0
        if self.should_skip():
            return
        if self.tqdm_type == "notebook":
            from tqdm.notebook import tqdm

            self.progress_bar = tqdm(total=total, **kwargs)
        elif self.tqdm_type == "std":
            from tqdm.std import tqdm

            self.progress_bar = tqdm(total=total, **kwargs)
        elif self.tqdm_type == "rich":
            from tqdm.rich import tqdm_rich

            self.progress_bar = tqdm_rich(total=total, **kwargs)
        else:
            raise ValueError(f"Unknown tqdm_type: {self.tqdm_type}")

    def update_progress(self, value):
        if self.should_skip():
            return
        incr = value - self._last_value
        self._last_value = value
        self.progress_bar.update(incr)

    def done(self):
        if self.should_skip():
            return
        self.progress_bar.close()
