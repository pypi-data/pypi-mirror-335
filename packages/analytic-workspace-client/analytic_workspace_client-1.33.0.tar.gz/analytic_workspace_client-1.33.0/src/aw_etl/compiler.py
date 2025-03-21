from typing import Protocol


class CompiledModule(Protocol):
    """ """
    def __contains__(self, item):
        """ """

    def __getattr__(self, item):
        """ """

    def __getitem__(self, item):
        """ """

    @property
    def is_empty(self) -> bool:
        """ """