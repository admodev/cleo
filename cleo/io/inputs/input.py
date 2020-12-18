import re

from io import BufferedReader
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from cleo._compat import shell_quote
from cleo.exceptions import RuntimeException
from cleo.exceptions import ValueException
from cleo.io.inputs.argument import Argument
from cleo.io.inputs.option import Option

from .definition import Definition


class Input:
    """
    This class is the base class for concrete Input implementations.
    """

    def __init__(self, definition: Optional[Definition] = None) -> None:
        self._definition = None
        self._stream = None
        self._options = {}
        self._arguments = {}
        self._interactive = True

        if definition is None:
            definition = Definition()
        else:
            self.bind(definition)
            self.validate()

    @property
    def arguments(self) -> Dict[str, Any]:
        return {**self._definition.argument_defaults, **self._arguments}

    @property
    def options(self) -> Dict[str, Any]:
        return {**self._definition.option_defaults, **self._options}

    @property
    def stream(self) -> BufferedReader:
        return self._stream

    @property
    def first_argument(self) -> Optional[str]:
        """
        Returns the first argument from the raw parameters (not parsed).
        """
        raise NotImplementedError()

    def parameter_option(
        self,
        values: Union[str, List[str]],
        default: Any = False,
        only_params: bool = False,
    ) -> Any:
        """
        Returns the value of a raw option (not parsed).
        """
        raise NotImplementedError()

    def is_interactive(self) -> bool:
        return self._interactive

    def interactive(self, interactive: bool = True) -> None:
        self._interactive = interactive

    def bind(self, definition: Definition) -> None:
        """
        Binds the current Input instance with
        the given definition's arguments and options.
        """
        self._arguments = []
        self._options = []
        self._definition = definition

        self._parse()

    def validate(self) -> None:
        missing_arguments = []

        for argument_name in self._definition.arguments.keys():
            if (
                argument_name not in self._arguments
                and self._definition.argument(argument_name).is_required()
            ):
                missing_arguments.append(argument_name)

        if missing_arguments:
            raise RuntimeException(
                'Not enough arguments (missing: "{}")'.format(
                    ", ".join(missing_arguments)
                )
            )

    def argument(self, name: str) -> Argument:
        if not self._definition.has_argument(name):
            raise ValueException(f'The argument "{name}" does not exist')

        if name in self._arguments:
            return self._arguments[name]

        return self._definition.argument(name).default

    def set_argument(self, name: str, value: Any) -> None:
        if not self._definition.has_argument(name):
            raise ValueException(f'The argument "{name}" does not exist')

        self._arguments[name] = value

    def has_argument(self, name: str) -> bool:
        return self._definition.has_argument(name)

    def option(self, name: str) -> Option:
        if not self._definition.has_option(name):
            raise ValueException(f'The option "--{name}" does not exist')

        if name in self._options:
            return self._options[name]

        return self._definition.option(name).default

    def set_option(self, name: str, value: Any) -> None:
        if not self._definition.has_option(name):
            raise ValueException(f'The option "--{name}" does not exist')

        self._options[name] = value

    def has_option(self, name: str) -> bool:
        return self._definition.has_option(name)

    def escape_token(self, token: str) -> str:
        if re.match("^[\w-]+$"):
            return token

        return shell_quote(token)

    def set_stream(self, stream: BufferedReader) -> None:
        self._stream = stream

    def has_parameter_option(
        self, values: Union[str, List[str]], only_params: bool = False
    ) -> bool:
        """
        Returns true if the raw parameters (not parsed) contain a value.
        """
        raise NotImplementedError()

    def _parse(self) -> None:
        raise NotImplementedError()
