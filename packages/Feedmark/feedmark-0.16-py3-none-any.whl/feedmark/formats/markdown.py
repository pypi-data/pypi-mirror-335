# Copyright (c) 2019-2024 Chris Pressey, Cat's Eye Technologies
# This file is distributed under an MIT license.  See LICENSES/ directory.
# SPDX-License-Identifier: LicenseRef-MIT-X-Feedmark

from __future__ import absolute_import

from collections import OrderedDict
import re

from feedmark.utils import items_in_priority_order


def remove_outer_p(html):
    match = re.match(r"^\s*\<\s*p\s*\>\s*(.*?)\s*\<\s*/\s*p\s*\>\s*$", html)
    if match:
        html = match.group(1)
    return html


def markdown_to_html5(text, link_ref_defs=None):
    """Canonical function used within `feedmark` to convert Markdown text to a HTML5 snippet."""
    from markdown import markdown

    if link_ref_defs:
        text += markdownize_link_ref_defs(link_ref_defs)

    return markdown(text, extensions=["markdown.extensions.toc"])


def markdown_to_html5_deep(obj, **kwargs):
    if obj is None:
        return None
    elif isinstance(obj, OrderedDict):
        return OrderedDict(
            (k, markdown_to_html5_deep(v, **kwargs)) for k, v in obj.items()
        )
    elif isinstance(obj, dict):
        return dict((k, markdown_to_html5_deep(v, **kwargs)) for k, v in obj.items())
    elif isinstance(obj, list):
        return [markdown_to_html5_deep(subobj, **kwargs) for subobj in obj]
    else:
        return remove_outer_p(markdown_to_html5(str(obj), **kwargs))


def markdownize_properties(properties, property_priority_order):
    if not properties:
        return ""
    md = ""
    for key, value in items_in_priority_order(properties, property_priority_order):
        if isinstance(value, list):
            for subitem in value:
                md += "*   {} @ {}\n".format(key, subitem)
        else:
            md += "*   {}: {}\n".format(key, value)
    md += "\n"
    return md


def markdownize_link_ref_defs(link_ref_defs):
    if not link_ref_defs:
        return ""
    md = "\n"  # blank line before the link ref defs block
    # TODO: an option that writes out these link ref defs in sorted order
    for name, (url, title) in link_ref_defs.items():
        name = sorted(link_ref_defs.unnormalized_labels_for(name))[0]
        # FIXME handle title
        md += "[{}]: {}\n".format(name, url)
    return md


def feedmark_markdownize(document, schema=None):
    property_priority_order = []
    if schema is not None:
        property_priority_order = schema.get_property_priority_order()

    md = "{}\n{}\n\n".format(document.title, "=" * len(document.title))
    if document.header_comment:
        md += document.header_comment + "\n\n"
    md += markdownize_properties(document.properties, property_priority_order)
    if document.preamble:
        md += document.preamble + "\n"
    md = re.sub(r"\n+$", "\n", md)
    for section in document.sections:
        md += "\n"
        md += "### {}\n\n".format(section.title.strip())
        if section.images:
            for entry in section.images:
                if "link" in entry:
                    md += "[![{}]({})]({})\n".format(
                        entry["description"],
                        entry["source"],
                        entry["link"],
                    )
                else:
                    md += "![{}]({})\n".format(
                        entry["description"],
                        entry["source"],
                    )
            md += "\n"
        md += markdownize_properties(section.properties, property_priority_order)
        md += re.sub(r"^\n+", "", section.body)
        md = re.sub(r"\n+$", "\n", md)
    md += "\n"
    md = re.sub(r"\n+$", "\n", md)
    md += markdownize_link_ref_defs(document.link_ref_defs)
    md = re.sub(r"\n+$", "\n", md)
    return md


def feedmark_htmlize(document, *args, **kwargs):
    return markdown_to_html5(feedmark_markdownize(document, *args, **kwargs))
