from contextlib import contextmanager

from pydantic import BaseModel, ConfigDict


class ImmutableModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    @contextmanager
    def _unfreeze(self):
        """
        If you must mutate (such as in a model validator that updates a field)
        then you must explicitly allow it using this protected context manager.
        """
        old_frozen_value = self.model_config.get("frozen")
        try:
            self.model_config["frozen"] = False
            yield
        finally:
            if old_frozen_value is None:
                del self.model_config["frozen"]
            else:
                self.model_config["frozen"] = old_frozen_value

    def model_update(self, **kwargs):
        return self.model_copy(update=kwargs)
