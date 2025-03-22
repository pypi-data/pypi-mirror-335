# Copyright (c) 2019 Frost Ming
#
# SPDX-License-Identifier: LicenseRef-MIT-X-Marko

# Copyright (c) 2024-2025 Chris Pressey, Cat's Eye Technologies.
#
# SPDX-License-Identifier: LicenseRef-MIT-X-Feedmark

import logging

from marko.md_renderer import MarkdownRenderer


logger = logging.getLogger(__name__)


class CleanMarkdownRenderer(MarkdownRenderer):

    def __init__(self) -> None:
        super().__init__()
        logger.debug(f"Created new {self.__class__.__name__}")

    def render_heading(self, element) -> str:
        """Override to render h1 and h2 underlined."""
        if element.level in (1, 2):
            text = self.render_children(element)
            underline = "=" if element.level == 1 else "-"
            result = self._prefix + text + "\n" + underline * len(text) + "\n"
        else:
            result = (
                self._prefix
                + "#" * element.level
                + " "
                + self.render_children(element)
                + "\n"
            )
        self._prefix = self._second_prefix
        return result

    def render_list(self, element) -> str:
        """Overrise to render list items indented by 4 places, not 2."""
        result = []
        if element.ordered:
            for num, child in enumerate(element.children, element.start):
                with self.container(f"{num}. ", " " * (len(str(num)) + 2)):
                    result.append(self.render(child))
        else:
            for child in element.children:
                with self.container(f"{element.bullet}   ", "    "):
                    result.append(self.render(child))
        self._prefix = self._second_prefix
        return "".join(result)

    def render_line_break(self, element) -> str:
        """Override to render line break as double space at end of line."""
        result = (
            "\n" + self._second_prefix if element.soft else "  \n" + self._second_prefix
        )
        return result

    def render_link_ref(self, element) -> str:
        """Override to render "default" reference links with trailing `[]`."""
        link_text = self.render_children(element)
        if element.label:
            label = element.label
            if label[0] == "[" and label[-1] == "]":
                label = label[1:-1]
            return f"[{link_text}][{label}]"
        else:
            return f"[{link_text}][]"

    def render_thematic_break(self, element) -> str:
        """Override to render thematic breaks as `- - - -`."""
        result = self._prefix + "- - - -\n"
        self._prefix = self._second_prefix
        return result

    def render_html_block(self, element) -> str:
        """Override to not add extra line breaks after HTML comments."""
        is_html_comment = element.body.rstrip().endswith("-->")

        result = self._prefix + element.body + ("\n" if not is_html_comment else "")
        self._prefix = self._second_prefix
        return result
