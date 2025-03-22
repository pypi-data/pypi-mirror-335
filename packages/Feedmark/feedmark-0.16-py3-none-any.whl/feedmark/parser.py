# Copyright (c) 2019-2024 Chris Pressey, Cat's Eye Technologies
# This file is distributed under an MIT license.  See LICENSES/ directory.
# SPDX-License-Identifier: LicenseRef-MIT-X-Feedmark

from datetime import datetime
from collections import OrderedDict
import re

from marko.block import (
    SetextHeading,
    Heading,
    HTMLBlock,
    BlankLine,
    List,
    Paragraph,
    LinkRefDef,
)
from marko.inline import Image, Link, RawText, Literal
from marko.parser import Parser as MarkoParser

from .models import Document, Section
from .renderer import CleanMarkdownRenderer
from .formats.markdown import markdown_to_html5, markdown_to_html5_deep
from .utils import quote


def strip_square_brackets(s):
    if s.startswith("[") and s.endswith("]"):
        return s[1:-1]
    return s


def parse_property(listitem_text):
    match = re.match(r"^(.*?)\s*\@\s*(.*?)\s*$", listitem_text)
    if match:
        (key, val) = (match.group(1), match.group(2))
        return ("@", key, val)
    match = re.match(r"^(.*?)\s*\:\s*(.*?)\s*$", listitem_text)
    if match:
        (key, val) = (match.group(1), match.group(2))
        return (":", key, val)
    raise ValueError('Expected property, found "{}"'.format(listitem_text))


def has_image_child(child):
    return isinstance(child, Image) or (
        isinstance(child, Link) and isinstance(child.children[0], Image)
    )


def is_image_paragraph(child):
    return isinstance(child, Paragraph) and has_image_child(child.children[0])


def parse_image_children(element, renderer):
    for child in element.children:
        if isinstance(child, Image):
            yield {
                "description": renderer.render(child.children[0]).strip(),
                "source": child.dest,
            }
        if isinstance(child, Link) and isinstance(child.children[0], Image):
            yield {
                "description": renderer.render(child.children[0].children[0]).strip(),
                "source": child.children[0].dest,
                "link": child.dest,
            }


def obtain_heading_text(element):
    chunks = []
    for child in element.children:
        if isinstance(child, RawText):
            chunks.append(child.children)
        elif isinstance(child, Literal):
            chunks.append("\\")
            chunks.append(child.children)
    return "".join(chunks)


class Parser:
    def __init__(self):
        pass

    def parse(self, markdown_text):
        marko_parser = MarkoParser()
        marko_document = marko_parser.parse(markdown_text)

        renderer = CleanMarkdownRenderer()

        document = Document()
        header_comment = ""
        preamble = ""
        section = None
        reading_images = True
        reading_properties = True

        for child in marko_document.children:
            if isinstance(child, (Heading, SetextHeading)):
                title_text = obtain_heading_text(child)
                if child.level == 1:
                    document.set_title(title_text)
                elif child.level == 3:
                    section = Section(title_text)
                    reading_images = True
                    reading_properties = True
                    document.sections.append(section)
                    section.document = document
                elif section:
                    section.add_to_body(renderer.render(child).strip())
                else:
                    preamble += renderer.render(child)
            elif isinstance(child, HTMLBlock) and not section:
                header_comment += renderer.render(child)
            elif reading_properties and isinstance(child, List):
                reading_images = False
                reading_properties = False
                for listitem in child.children:
                    listitem_text = renderer.render(listitem).strip()
                    kind, key, value = parse_property(listitem_text)
                    if not section:
                        document.add_property(kind, key, value)
                    else:
                        section.add_property(kind, key, value)
            elif isinstance(child, LinkRefDef):
                # LinkRefDef elements always go in the main document, not sections.
                document.link_ref_defs.add(
                    strip_square_brackets(child.label.text), child.dest, child.title
                )
            elif reading_images and is_image_paragraph(child):
                for image_record in parse_image_children(child, renderer):
                    section.add_image(image_record)
            else:
                if isinstance(child, Paragraph):
                    reading_images = False
                    reading_properties = False
                if section:
                    text = renderer.render(child)
                    text = re.sub(r"^\n+", "", text)
                    text = re.sub(r"\n+$", "", text)
                    section.add_to_body(text)
                else:
                    preamble += renderer.render(child)

        document.header_comment = header_comment.strip()
        document.preamble = preamble.strip()

        return document
