import re

from typing import Dict
from typing import Optional
from typing import Tuple

from cleo.exceptions import ValueException

from .style import Style
from .style_stack import StyleStack


class Formatter:

    TAG_REGEX = re.compile(r"(?ix)<(([a-z](?:[^<>]*)) | /([a-z](?:[^<>]*))?)>")

    def __init__(
        self, decorated: bool = False, styles: Optional[Dict[str, Style]] = None
    ) -> None:
        self._decorated = decorated
        self._styles = {}

        self.set_style("error", Style("red", options=["bold"]))
        self.set_style("info", Style("blue"))
        self.set_style("comment", Style("green"))
        self.set_style("question", Style("cyan"))

        if styles is None:
            styles = {}

        for name, style in styles.items():
            self.set_style(name, style)

        self._style_stack = StyleStack()

    def decorated(self, decorated: bool = True) -> None:
        self._decorated = decorated

    def is_decorated(self) -> bool:
        return self._decorated

    def set_style(self, name: str, style: Style) -> None:
        self._styles[name] = style

    def has_style(self, name: str) -> bool:
        return name in self._styles

    def style(self, name: str) -> Style:
        if not self.has_style(name):
            raise ValueException(f'Undefined style: "{name}"')

        return self._styles[name]

    def format(self, message: str) -> str:
        return self.format_and_wrap(message, 0)

    def format_and_wrap(self, message: str, width: int) -> str:
        offset = 0
        output = ""
        current_line_length = 0
        for match in self.TAG_REGEX.finditer(message):
            pos = match.start()
            text = match.group(0)

            if pos != 0 and message[pos - 1] == "\\":
                continue

            # add the text up to the next tag
            formatted, current_line_length = self._apply_current_style(
                message[offset:pos], output, width, current_line_length
            )
            output += formatted
            offset = pos + len(text)

            # Opening tag
            open = text[1] != "/"
            if open:
                tag = match.group(1)
            else:
                tag = match.group(2)

            style = None
            if tag:
                style = self._create_style_from_string(tag)

            if not open and not tag:
                # </>
                self._style_stack.pop()
            elif style is None:
                formatted, current_line_length = self._apply_current_style(
                    text, output, width, current_line_length
                )
                output += formatted
            elif open:
                self._style_stack.push(style)
            else:
                self._style_stack.pop(style)

        formatted, current_line_length = self._apply_current_style(
            message[offset:], output, width, current_line_length
        )
        output += formatted

        if output.find("\0") != -1:
            return output.replace("\0", "\\").replace("\\<", "<")

        return output.replace("\\<", "<")

    def _create_style_from_string(self, string: str) -> Optional[Style]:
        if string in self._styles:
            return self._styles[string]

        matches = re.findall("([^=]+)=([^;]+)(;|$)", string.lower())
        if not matches:
            return None

        style = Style()

        for match in matches:
            if match[0] == "fg":
                style.foreground(match[1])
            elif match[0] == "bg":
                style.background(match[1])
            else:
                try:
                    for option in match[1].split(","):
                        style.set_option(option.strip())
                except ValueError:
                    return None

        return style

    def _apply_current_style(
        self, text: str, current: str, width: int, current_line_length: int
    ) -> Tuple[str, int]:
        print(text, current, width, current_line_length)
        if not text:
            return "", current_line_length

        if not width:
            if self.is_decorated():
                return self._style_stack.current.apply(text), current_line_length

            return text, current_line_length

        if not current_line_length and current:
            text = text.lstrip()

        if current_line_length:
            i = width - current_line_length
            prefix = text[:i] + "\n"
            text = text[i:]
        else:
            prefix = ""

        m = re.match(r"(\n)$", text)
        text = prefix + re.sub(r"([^\n]{{}})\\ *".format(width), "\1\n", text)
        text = text.rstrip("\n") + (m.group(1) if m else "")

        if not current_line_length and current and current[-1] != "\n":
            text = "\n" + text

        lines = text.split("\n")
        for line in lines:
            print(line, len(line))
            current_line_length += len(line)
            if current_line_length >= width:
                current_line_length = 0

        if self.is_decorated():
            for i, line in enumerate(lines):
                lines[i] = self._style_stack.current.apply(line)

        print(current_line_length)
        return "\n".join(lines), current_line_length
