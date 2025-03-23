import abc
from collections.abc import Iterable

import awesome_list_generator as alg


class Formatter(abc.ABC):
    @abc.abstractmethod
    def format(
        self, categories: Iterable[alg.Category], projects: Iterable[alg.ProjectInfo]
    ) -> str: ...
