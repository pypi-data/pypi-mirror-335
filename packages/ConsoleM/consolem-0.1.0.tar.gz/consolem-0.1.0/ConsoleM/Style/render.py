import re

from .const import Color, get_all_colors, Style, STYLE_ATTRIBUTES, AsciiEscapeCode, EMOJI
from typing import Optional


class Render:
    def __init__(self, content: Optional[str] = None):
        self.content = content
        self.pattern_color = re.compile(r"\[(.+?)]")
        self.pattern_emoji = re.compile(r":([^ ]+?):")

    def render(self, content: Optional[str] = None):
        if not content:
            if not self.content:
                return ""
            content = self.content

        for match in re.finditer(self.pattern_color, content):
            if match.group(1) in ["/", "\\"]:
                content = content.replace(match.group(0), AsciiEscapeCode.OCTAL.build(0))
            content = content.replace(match.group(0), self.ansi_builder(match.group(1)))

        content = self.emoji_render(content)

        return content

    def ansi_builder(self, content: str) -> str:
        if not content and not self.content:
            return ""
        content = content or self.content

        color: Color = Color.NONE
        style: Style = Style.NONE

        for part in content.split(" "):
            lower = part.lower()
            if lower in get_all_colors():
                color = Color.get_color_from_str(lower)
            elif lower := STYLE_ATTRIBUTES.get(lower):
                style = Style.get_style_from_str(lower)

        if color != Color.NONE and style == Style.NONE:
            if isinstance(color.value, str):
                return AsciiEscapeCode.OCTAL.build(38, color.value)
            return AsciiEscapeCode.OCTAL.build(color.value)

        if color != Color.NONE and style != Style.NONE:
            return AsciiEscapeCode.OCTAL.build(color.value, style.value)

        if style != Style.NONE:
            return AsciiEscapeCode.OCTAL.build(style.value)
        return ""

    def emoji_render(self, content: str) -> str:
        if not content and not self.content:
            return ""
        content = content or self.content

        for match in re.finditer(self.pattern_emoji, content):
            emoji = EMOJI.get(match.group(1))
            if emoji:
                content = content.replace(match.group(0), emoji)
        return content
