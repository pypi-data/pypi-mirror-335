# Copyright (c) 2019-2024 Chris Pressey, Cat's Eye Technologies
# This file is distributed under an MIT license.  See LICENSES/ directory.
# SPDX-License-Identifier: LicenseRef-MIT-X-Feedmark

import unittest

import json
import os
import sys
from subprocess import check_call
from tempfile import mkdtemp

from feedmark.checkers import Schema
from feedmark.main import main
from feedmark.loader import read_document_from
from feedmark.utils import StringIO


class TestFeedmarkFileCreation(unittest.TestCase):

    def setUp(self):
        super(TestFeedmarkFileCreation, self).setUp()
        self.saved_stdout = sys.stdout
        sys.stdout = StringIO()
        self.maxDiff = None
        self.dirname = mkdtemp()
        self.prevdir = os.getcwd()
        os.chdir(self.dirname)

    def tearDown(self):
        os.chdir(self.prevdir)
        check_call("rm -rf {}".format(self.dirname), shell=True)
        sys.stdout = self.saved_stdout
        super(TestFeedmarkFileCreation, self).tearDown()

    def assert_file_contains(self, filename, text):
        with open(filename, "r") as f:
            contents = f.read()
        self.assertIn(text, contents, contents)

    def test_atom_feed(self):
        main(
            [
                "{}/eg/Recent Llama Sightings.md".format(self.prevdir),
                "--output-atom=feed.xml",
            ]
        )
        self.assert_file_contains(
            "feed.xml",
            "<id>http://example.com/llama.xml/2 Llamas Spotted Near Mall</id>",
        )
        self.assert_file_contains(
            "feed.xml",
            "https://codeberg.org/catseye/Feedmark/src/branch/master/eg/Recent%20Llama%20Sightings.md#2-llamas-spotted-near-mall",
        )
        os.unlink("feed.xml")

    def test_rewrite_markdown_input_refdex(self):
        """When asked to `--rewrite-markdown`, the tool rewrites the input file,
        replacing reference links with links from the given `--input-refdex`.
        """
        with open("foo.md", "w") as f:
            f.write(
                """# Document

### Entry

Have you heard, [2 Llamas Spotted Near Mall]()?

[2 Llamas Spotted Near Mall]: TK
"""
            )
        main(
            [
                "foo.md",
                "--input-refdex={}/eg/refdex.json".format(self.prevdir),
                "--rewrite-markdown",
            ]
        )
        self.assert_file_contains(
            "foo.md",
            "[2 Llamas Spotted Near Mall]: eg/Recent%20Llama%20Sightings.md#2-llamas-spotted-near-mall",
        )
        os.unlink("foo.md")

    def test_rewrite_markdown_internal(self):
        """When asked to `--rewrite-markdown`, the tool rewrites the input file,
        replacing reference links with internal links to the matching sections
        in the document.
        """
        with open("foo.md", "w") as f:
            f.write(
                """# Document

### Bubble & Squeak

Have you heard, [Bubble & Squeak]()?

[Bubble & Squeak]: TK
"""
            )
        main(["foo.md", "--output-refdex", "--rewrite-markdown"])
        self.assert_file_contains("foo.md", "[Bubble & Squeak]: foo.md#bubble-squeak")
        os.unlink("foo.md")


class TestFeedmarkCommandLine(unittest.TestCase):

    def setUp(self):
        super(TestFeedmarkCommandLine, self).setUp()
        self.saved_stdout = sys.stdout
        sys.stdout = StringIO()
        self.maxDiff = None

    def tearDown(self):
        sys.stdout = self.saved_stdout
        super(TestFeedmarkCommandLine, self).tearDown()

    def test_schema(self):
        main(
            [
                "eg/Recent Llama Sightings.md",
                "eg/Ancient Llama Sightings.md",
                "--check-against-schema=eg/schema/Llama sighting.md",
            ]
        )
        output = sys.stdout.getvalue()
        self.assertEqual(output, "")

    def test_schema_failure(self):
        with self.assertRaises(SystemExit):
            main(
                [
                    "eg/Ill-formed Llama Sightings.md",
                    "eg/Recent Llama Sightings.md",
                    "--check-against-schema=eg/schema/Llama sighting.md",
                ]
            )
        data = json.loads(sys.stdout.getvalue())
        self.assertEqual(
            data,
            [
                {
                    "document": "Ill-formed Llama Sightings",
                    "result": [["extra", "excuse"], ["missing", "date"]],
                    "section": "Definite llama sighting with no date",
                }
            ],
        )

    def test_output_html(self):
        main(["eg/Recent Llama Sightings.md", "--output-html"])
        output = sys.stdout.getvalue()
        self.assertIn(
            '<h3 id="a-possible-llama-under-the-bridge">A Possible Llama Under the Bridge</h3>',
            output,
        )

    def test_output_json(self):
        main(["eg/Ancient Llama Sightings.md", "--output-json"])
        data = json.loads(sys.stdout.getvalue())
        self.assertDictEqual(
            data,
            {
                "documents": [
                    {
                        "filename": "eg/Ancient Llama Sightings.md",
                        "title": "Ancient Llama Sightings",
                        "preamble": "",
                        "properties": data["documents"][0]["properties"],
                        "sections": data["documents"][0]["sections"],
                    }
                ]
            },
        )
        self.assertDictEqual(
            data["documents"][0]["properties"],
            {
                "author": "Alfred J. Prufrock",
                "link-target-url": "https://codeberg.org/catseye/Feedmark/src/branch/master/eg/Ancient%20Llama%20Sightings.md",
                "url": "http://example.com/old_llama.xml",
            },
        )
        self.assertEqual(
            data["documents"][0]["sections"],
            [
                {
                    "body": data["documents"][0]["sections"][0]["body"],
                    "images": [
                        {
                            "description": "photo of possible llama",
                            "source": "https://static.catseye.tc/images/screenshots/Kolakoski_Kurve.jpg",
                        }
                    ],
                    "properties": {"date": "Jan 1 1984 12:00:00"},
                    "title": "Maybe sighting the llama",
                    "anchor": "maybe-sighting-the-llama",
                }
            ],
        )
        self.assertIn(
            "It was a possible llama sighting.\n\n",
            data["documents"][0]["sections"][0]["body"],
        )

    def test_output_json_with_multiple_images_and_linked_images(self):
        main(["eg/Recent Llama Sightings.md", "--output-json"])
        data = json.loads(sys.stdout.getvalue())
        self.assertEqual(
            data["documents"][0]["sections"][1]["images"],
            [
                {
                    "description": "photo of possible llama",
                    "source": "https://static.catseye.tc/images/screenshots/Heronsis_hermnonicii.jpg",
                    "link": "https://catseye.tc/article/Gewgaws.md",
                },
                {
                    "description": "another possible photo",
                    "source": "https://static.catseye.tc/images/screenshots/A_Non-Random_Walk.jpg",
                },
            ],
        )

    def test_output_htmlized_json(self):
        """When given the `--htmlized-json` flag, the tool will convert Markdown fields in the output to HTML."""
        main(["eg/Referenced Llama Sightings.md", "--output-json", "--htmlized-json"])
        data = json.loads(sys.stdout.getvalue())
        self.assertDictEqual(
            data,
            {
                "documents": [
                    {
                        "filename": "eg/Referenced Llama Sightings.md",
                        "title": "Referenced Llama Sightings",
                        "preamble": '<p>Some <strong>llamas</strong> have been <a href="spotted.html">spotted</a> recently.</p>',
                        "properties": data["documents"][0]["properties"],
                        "sections": data["documents"][0]["sections"],
                    }
                ]
            },
        )
        self.assertEqual(
            data["documents"][0]["sections"][0]["body"],
            "<p>I have strong opinions about this.  It's a <em>shame</em> more llamas aren't\nbeing spotted.  "
            "Sometimes they are <strong>striped</strong>, it's true, but<br />\nwhen<br />\nthey are, "
            '<a href="https://daringfireball.net/projects/markdown/">Markdown</a>\ncan be used.</p>\n'
            '<p>To <a href="https://en.wikipedia.org/wiki/Site">site</a> them.</p>\n<p>Sight them, sigh.</p>',
        )
        # note that property values are bare HTML fragments: there is no surrounding <p></p> or other element
        self.assertEqual(
            data["documents"][0]["properties"]["hopper"],
            '<a href="https://en.wikipedia.org/wiki/Stephen_Hopper">Stephen</a>',
        )
        self.assertEqual(
            data["documents"][0]["properties"]["spotted"],
            ['<a href="mall.html">the mall</a>', '<a href="beach.html">the beach</a>'],
        )
        self.assertEqual(
            data["documents"][0]["sections"][0]["properties"]["hopper"],
            '<a href="https://en.wikipedia.org/wiki/Grace_Hopper">Grace</a>',
        )
        self.assertEqual(
            data["documents"][0]["sections"][0]["properties"]["spotted"],
            [
                '<a href="mall.html">the mall</a>',
                '<a href="lumberyard.html">the lumberyard</a>',
            ],
        )

    def test_output_unordered_json(self):
        main(["eg/Referenced Llama Sightings.md", "--output-json"])
        data = json.loads(sys.stdout.getvalue())
        self.assertDictEqual(
            data["documents"][0]["properties"],
            {
                "author": "Alfred J. Prufrock",
                "link-target-url": "https://codeberg.org/catseye/Feedmark/src/branch/master/eg/Referenced%20Llama%20Sightings.md",
                "url": "http://example.com/refllama.xml",
                "hopper": "[Stephen](https://en.wikipedia.org/wiki/Stephen_Hopper)",
                "spotted": ["[the mall][]", "[the beach](beach.html)"],
            },
        )
        self.assertDictEqual(
            data["documents"][0]["sections"][0]["properties"],
            {
                "date": "Nov 1 2016 09:00:00",
                "hopper": "[Grace](https://en.wikipedia.org/wiki/Grace_Hopper)",
                "spotted": ["[the mall][]", "[the lumberyard](lumberyard.html)"],
            },
        )

    def test_output_ordered_json(self):
        main(["eg/Referenced Llama Sightings.md", "--output-json", "--ordered-json"])
        data = json.loads(sys.stdout.getvalue())
        self.assertEqual(
            data["documents"][0]["properties"],
            [
                ["author", "Alfred J. Prufrock"],
                ["url", "http://example.com/refllama.xml"],
                [
                    "link-target-url",
                    "https://codeberg.org/catseye/Feedmark/src/branch/master/eg/Referenced%20Llama%20Sightings.md",
                ],
                ["hopper", "[Stephen](https://en.wikipedia.org/wiki/Stephen_Hopper)"],
                ["spotted", ["[the mall][]", "[the beach](beach.html)"]],
            ],
        )
        self.assertEqual(
            data["documents"][0]["sections"][0]["properties"],
            [
                ["date", "Nov 1 2016 09:00:00"],
                ["hopper", "[Grace](https://en.wikipedia.org/wiki/Grace_Hopper)"],
                ["spotted", ["[the mall][]", "[the lumberyard](lumberyard.html)"]],
            ],
        )

    def test_parse_section_headings(self):
        with open("foo.md", "w") as f:
            f.write(
                r"""\
Some Resources
==============

### lo.logic - Most \'unintuitive\' application of the Axiom of Choice? - MathOverflow

*   url: https://mathoverflow.net/questions/20882/most-unintuitive-application-of-the-axiom-of-choice

### set theory - Set theories without \"junk\" theorems? - MathOverflow

*   url: http://mathoverflow.net/questions/90820/set-theories-without-junk-theorems/90945#90945

### The Origin of the Number Zero \| History \| Smithsonian

*   url: https://www.smithsonianmag.com/history/origin-number-zero-180953392/

### zajo/appler: Apple \]\[ emulator for MS-DOS, written in 8088 assembly

*   url: https://github.com/zajo/appler

### Computational \[Complexity\]\(Theory\)

That is not a link.
"""
            )
        main(["foo.md", "--output-json"])
        data = json.loads(sys.stdout.getvalue())
        self.assertDictEqual(
            data,
            {
                "documents": [
                    {
                        "filename": "foo.md",
                        "preamble": "",
                        "properties": {},
                        "sections": [
                            {
                                "anchor": "lo-logic-most-unintuitive-application-of-the-axiom-of-choice-mathoverflow",
                                "body": "\n",
                                "images": [],
                                "properties": {
                                    "url": "https://mathoverflow.net/questions/20882/most-unintuitive-application-of-the-axiom-of-choice"
                                },
                                "title": r"lo.logic - Most \'unintuitive\' application of the Axiom of Choice? - MathOverflow",
                            },
                            {
                                "anchor": "set-theory-set-theories-without-junk-theorems-mathoverflow",
                                "body": "\n",
                                "images": [],
                                "properties": {
                                    "url": "http://mathoverflow.net/questions/90820/set-theories-without-junk-theorems/90945#90945"
                                },
                                "title": r"set theory - Set theories without \"junk\" theorems? - MathOverflow",
                            },
                            {
                                "anchor": "the-origin-of-the-number-zero-history-smithsonian",
                                "body": "\n",
                                "images": [],
                                "properties": {
                                    "url": "https://www.smithsonianmag.com/history/origin-number-zero-180953392/"
                                },
                                "title": r"The Origin of the Number Zero \| History \| Smithsonian",
                            },
                            {
                                "anchor": "zajo-appler-apple-emulator-for-ms-dos-written-in-8088-assembly",
                                "body": "\n",
                                "images": [],
                                "properties": {"url": "https://github.com/zajo/appler"},
                                "title": r"zajo/appler: Apple \]\[ emulator for MS-DOS, written in 8088 assembly",
                            },
                            {
                                "anchor": "computational-complexitytheory",
                                "body": "\nThat is not a link.",
                                "images": [],
                                "properties": {},
                                "title": r"Computational \[Complexity\]\(Theory\)",
                            },
                        ],
                        "title": "Some Resources",
                    }
                ]
            },
        )

    def test_accumulate_properties_only_from_first_list_in_section(self):
        with open("foo.md", "w") as f:
            f.write(
                """# Document

### Bubble & Squeak

*   property1: one
*   property2: two

Have you heard, [Bubble & Squeak]()?

*   property3: three
*   property4: four

### Filthy Rich & Catflap

*   property3: three

It seems that you have not heard.

*   property3: four

[Bubble & Squeak]: TK
"""
            )
        main(["foo.md", "--output-json"])
        data = json.loads(sys.stdout.getvalue())
        self.assertDictEqual(
            data,
            {
                "documents": [
                    {
                        "filename": "foo.md",
                        "preamble": "",
                        "properties": {},
                        "sections": [
                            {
                                "anchor": "bubble-squeak",
                                "body": "\n\nHave you heard, [Bubble & Squeak]()?\n\n*   property3: three\n*   property4: four\n",
                                "images": [],
                                "properties": {"property1": "one", "property2": "two"},
                                "title": "Bubble & Squeak",
                            },
                            {
                                "anchor": "filthy-rich-catflap",
                                "body": "\n\nIt seems that you have not heard.\n\n*   property3: four\n",
                                "images": [],
                                "properties": {"property3": "three"},
                                "title": "Filthy Rich & Catflap",
                            },
                        ],
                        "title": "Document",
                    }
                ]
            },
        )
        os.unlink("foo.md")

    def test_accumulate_images_only_from_before_property_list(self):
        with open("foo.md", "w") as f:
            f.write(
                """# Document

### Bubble & Squeak

![first screenshot](https://example.com/bubble-and-squeak-001.png)  
![second screenshot](https://example.com/bubble-and-squeak-002.png)  

*   property1: one
*   property2: two

Have you heard, [Bubble & Squeak]()?

![third screenshot](https://example.com/bubble-and-squeak-003.png)  

[Bubble & Squeak]: TK
"""
            )
        main(["foo.md", "--output-json"])
        data = json.loads(sys.stdout.getvalue())
        self.assertEqual(
            data["documents"][0]["sections"][0]["images"],
            [
                {
                    "description": "first screenshot",
                    "source": "https://example.com/bubble-and-squeak-001.png",
                },
                {
                    "description": "second screenshot",
                    "source": "https://example.com/bubble-and-squeak-002.png",
                },
            ],
        )
        os.unlink("foo.md")

    def test_round_trip_preformatted_block(self):
        with open("foo.md", "w") as f:
            f.write(
                """\
# Document

### Bubble & Squeak

Sample:

    Have you heard?
    There are preformatted
    blocks in this section.
"""
            )
        main(["foo.md", "--output-markdown"])
        data = sys.stdout.getvalue()
        self.assertEqual(data, """\
Document
========

### Bubble & Squeak

Sample:

    Have you heard?
    There are preformatted
    blocks in this section.
""")
        os.unlink("foo.md")

    def test_output_refdex(self):
        main(
            [
                "eg/Recent Llama Sightings.md",
                "eg/Ancient Llama Sightings.md",
                "--output-refdex",
            ]
        )
        data = json.loads(sys.stdout.getvalue())
        self.assertDictEqual(
            data,
            {
                "2 Llamas Spotted Near Mall": {
                    "anchor": "2-llamas-spotted-near-mall",
                    "filenames": ["eg/Recent Llama Sightings.md"],
                },
                "A Possible Llama Under the Bridge": {
                    "anchor": "a-possible-llama-under-the-bridge",
                    "filenames": ["eg/Recent Llama Sightings.md"],
                },
                "Llamas: It's Time to Spot Them": {
                    "anchor": "llamas-it-s-time-to-spot-them",
                    "filenames": ["eg/Recent Llama Sightings.md"],
                },
                "Maybe sighting the llama": {
                    "anchor": "maybe-sighting-the-llama",
                    "filenames": ["eg/Ancient Llama Sightings.md"],
                },
            },
        )

    def test_output_refdex_with_overlap(self):
        # Both of these files contain an entry called "Llamas: It's Time to Spot Them".
        # The refdex is created with entries pointing to all files where the entry occurs.
        main(
            [
                "eg/Recent Llama Sightings.md",
                "eg/Referenced Llama Sightings.md",
                "--output-refdex",
            ]
        )
        data = json.loads(sys.stdout.getvalue())
        self.assertDictEqual(
            data,
            {
                "2 Llamas Spotted Near Mall": {
                    "anchor": "2-llamas-spotted-near-mall",
                    "filenames": [
                        "eg/Recent Llama Sightings.md",
                    ],
                },
                "A Possible Llama Under the Bridge": {
                    "anchor": "a-possible-llama-under-the-bridge",
                    "filenames": [
                        "eg/Recent Llama Sightings.md",
                    ],
                },
                "Llamas: It's Time to Spot Them": {
                    "anchor": "llamas-it-s-time-to-spot-them",
                    "filenames": [
                        "eg/Recent Llama Sightings.md",
                        "eg/Referenced Llama Sightings.md",
                    ],
                },
            },
        )

    def test_output_refdex_with_overlap_forcing_single_filename(self):
        # Both of these files contain an entry called "Llamas: It's Time to Spot Them"
        # The refdex is created pointing only to the file that was mentioned last.
        main(
            [
                "eg/Recent Llama Sightings.md",
                "eg/Referenced Llama Sightings.md",
                "--output-refdex",
                "--output-refdex-single-filename",
            ]
        )
        data = json.loads(sys.stdout.getvalue())
        self.assertDictEqual(
            data,
            {
                "2 Llamas Spotted Near Mall": {
                    "anchor": "2-llamas-spotted-near-mall",
                    "filename": "eg/Recent Llama Sightings.md",
                },
                "A Possible Llama Under the Bridge": {
                    "anchor": "a-possible-llama-under-the-bridge",
                    "filename": "eg/Recent Llama Sightings.md",
                },
                "Llamas: It's Time to Spot Them": {
                    "anchor": "llamas-it-s-time-to-spot-them",
                    "filename": "eg/Referenced Llama Sightings.md",
                },
            },
        )

    def test_input_refdex_output_markdown(self):
        """When given an input refdex, the tool replaces reference links with links from the input refdex."""
        main(
            [
                "eg/Ill-formed Llama Sightings.md",
                "--input-refdex",
                "eg/refdex.json",
                "--output-markdown",
            ]
        )
        output = sys.stdout.getvalue()
        self.assertIn(
            "[2 Llamas Spotted Near Mall]: eg/Recent%20Llama%20Sightings.md#2-llamas-spotted-near-mall",
            output,
            output,
        )

    def test_output_links(self):
        main(["eg/Ill-formed Llama Sightings.md", "--output-links"])
        data = json.loads(sys.stdout.getvalue())
        self.assertEqual(
            data,
            [
                {
                    "document": "Ill-formed Llama Sightings",
                    "name": "2 Llamas Spotted Near Mall",
                    "url": "TK",
                },
                {
                    "document": "Ill-formed Llama Sightings",
                    "section": "Definite llama sighting with no date",
                    "url": "https://tcrf.net/The_Cutting_Room_Floor",
                },
            ],
        )


class TestFeedmarkInternals(unittest.TestCase):

    def test_load_documents(self):
        doc1 = read_document_from("eg/Ancient Llama Sightings.md")
        self.assertEqual(doc1.title, "Ancient Llama Sightings")
        doc2 = read_document_from("eg/Recent Llama Sightings.md")
        self.assertEqual(doc2.title, "Recent Llama Sightings")
        self.assertEqual(len(doc2.sections), 3)

    def test_schema(self):
        schema_doc = read_document_from("eg/schema/Llama sighting.md")
        schema = Schema(schema_doc)

        doc1 = read_document_from("eg/Ancient Llama Sightings.md")
        doc2 = read_document_from("eg/Recent Llama Sightings.md")
        results = schema.check_documents([doc1, doc2])
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
