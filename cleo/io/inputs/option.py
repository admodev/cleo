from typing import Any
from typing import Optional

from cleo.exceptions import LogicException


class Option:
    """
    A command line option.
    """

    def __init__(
        self,
        name: str,
        shortcut: Optional[str] = None,
        flag: bool = True,
        requires_value: bool = True,
        is_list: bool = False,
        description: Optional[str] = None,
        default: Optional[Any] = None,
    ) -> None:
        if name.startswith("--"):
            name = name[2:]

        if not name:
            raise ValueError("An option name cannot be empty")

        if not shortcut:
            shortcut = None

        if shortcut:
            # TODO: Multiple shortcuts
            shortcut = shortcut.lstrip("-")

        self._shortcut = shortcut
        self._flag = flag
        self._requires_value = requires_value
        self._is_list = is_list
        self._description = description
        self._default = None

        if self._is_list and self._flag:
            raise LogicException("A flag option cannot be a list as well")

        self.set_default(default)

    @property
    def name(self) -> str:
        return self._name

    @property
    def shortcut(self) -> str:
        return self._shortcut

    @property
    def description(self) -> str:
        return self._description

    @property
    def default(self) -> Optional[Any]:
        return self._default

    def is_flag(self) -> bool:
        return self._flag

    def accepts_value(self) -> bool:
        return not self._flag

    def requires_value(self) -> bool:
        return self._requires_value

    def is_list(self) -> bool:
        return self._is_list

    def set_default(self, default: Optional[Any] = None) -> None:
        if self._flag and default is not None:
            raise LogicException("A flag option cannot have a default value")

        if self._is_list:
            if default is None:
                default = []
            elif not isinstance(default, list):
                raise LogicException("A default value for a list option must be a list")

        if self._flag:
            default = False

        self._default = default
