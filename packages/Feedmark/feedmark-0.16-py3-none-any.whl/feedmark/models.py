# Copyright (c) 2019-2024 Chris Pressey, Cat's Eye Technologies
# This file is distributed under an MIT license.  See LICENSES/ directory.
# SPDX-License-Identifier: LicenseRef-MIT-X-Feedmark

from datetime import datetime
from collections import OrderedDict
import re

from marko.block import LinkRefDefs

from .formats.markdown import markdown_to_html5, markdown_to_html5_deep
from .utils import quote


def rewrite_link_ref_defs(refdex, link_ref_defs):
    from marko.block import LinkRefDefs

    new_link_ref_defs = LinkRefDefs()
    seen_names = set()
    for name, (url, title) in link_ref_defs.items():
        name = sorted(link_ref_defs.unnormalized_labels_for(name))[0]
        if name in seen_names:
            continue
        seen_names.add(name)
        if name in refdex:
            entry = refdex[name]
            if "filename" in entry and "anchor" in entry:
                filename = quote(entry["filename"].encode("utf-8"))
                anchor = quote(entry["anchor"].encode("utf-8"))
                url = "{}#{}".format(filename, anchor)
            elif "filenames" in entry and "anchor" in entry:
                # pick the last one, for compatibility with single-refdex style
                filename = quote(entry["filenames"][-1].encode("utf-8"))
                anchor = quote(entry["anchor"].encode("utf-8"))
                url = "{}#{}".format(filename, anchor)
            elif "url" in entry:
                url = entry["url"]
            else:
                raise ValueError("Badly formed refdex entry: {}".format(entry))
        new_link_ref_defs.add(name, url, title)
    return new_link_ref_defs


class Document(object):
    def __init__(self):
        self.title = "Untitled"
        self.properties = OrderedDict()

        self.header_comment = None
        self.preamble = None
        self.sections: list(Section) = []
        self.link_ref_defs = LinkRefDefs()

    def __str__(self):
        return "document '{}'".format(self.title.encode("utf-8"))

    def set_title(self, title):
        self.title = title

    def add_property(self, kind, key, value):
        if kind == ":":
            if key in self.properties:
                raise KeyError("{} already given".format(key))
            self.properties[key] = value
        elif kind == "@":
            self.properties.setdefault(key, []).append(value)
        else:
            raise NotImplementedError(kind)

    def rewrite_link_ref_defs(self, refdex):
        self.link_ref_defs = rewrite_link_ref_defs(refdex, self.link_ref_defs)

    def global_link_ref_defs(self):
        return self.link_ref_defs

    def to_json_data(self, **kwargs):

        if kwargs.get("htmlize", False):
            if "link_ref_defs" not in kwargs:
                kwargs["link_ref_defs"] = self.global_link_ref_defs()
            preamble = markdown_to_html5(
                self.preamble, link_ref_defs=kwargs["link_ref_defs"]
            )
            properties = markdown_to_html5_deep(
                self.properties, link_ref_defs=kwargs["link_ref_defs"]
            )
        else:
            preamble = self.preamble
            properties = self.properties

        if kwargs.get("ordered", False):
            properties_list = []
            for key, value in properties.items():
                properties_list.append([key, value])
            properties = properties_list
        else:
            properties = dict(properties)

        return {
            "filename": self.filename,
            "title": self.title,
            "properties": properties,
            "preamble": preamble,
            "sections": [s.to_json_data(**kwargs) for s in self.sections],
        }


class Section(object):
    def __init__(self, title):
        self.document = None
        self.title = title
        self.properties = OrderedDict()
        self._body_lines = []
        self.images = []

    def __str__(self):
        s = "section '{}'".format(self.title.encode("utf-8"))
        if self.document:
            s += " of " + str(self.document)
        return s

    def add_property(self, kind, key, value):
        if kind == ":":
            if key in self.properties:
                raise KeyError("{} already given".format(key))
            self.properties[key] = value
        elif kind == "@":
            self.properties.setdefault(key, []).append(value)
        else:
            raise NotImplementedError(kind)

    def add_to_body(self, line):
        self._body_lines.append(line)

    def add_image(self, image_record):
        self.images.append(image_record)

    @property
    def body(self):
        return "\n".join(self._body_lines)

    @property
    def publication_date(self):
        formats = (
            "%b %d %Y %H:%M:%S",
            "%a, %d %b %Y %H:%M:%S GMT",
        )
        for format in formats:
            try:
                return datetime.strptime(self.properties["date"], format)
            except KeyError:
                raise KeyError("could not find 'date' on {}".format(self))
            except ValueError:
                pass
        raise NotImplementedError

    @property
    def anchor(self):
        title = self.title.strip().lower()
        title = re.sub(r"[^\w]+$", "", title)
        title = re.sub(r"[^\w\s\/\.\'-]", "", title)
        return re.sub(r"[\s\/\.\'-]+", "-", title)

    def to_json_data(self, **kwargs):

        if kwargs.get("htmlize", False):
            body = markdown_to_html5(self.body, link_ref_defs=kwargs["link_ref_defs"])
            properties = markdown_to_html5_deep(
                self.properties, link_ref_defs=kwargs["link_ref_defs"]
            )
        else:
            body = self.body
            properties = self.properties

        if kwargs.get("ordered", False):
            properties_list = []
            for key, value in properties.items():
                properties_list.append([key, value])
            properties = properties_list
        else:
            properties = dict(properties)

        return {
            "title": self.title,
            "anchor": self.anchor,
            "images": self.images,
            "properties": properties,
            "body": body,
        }
