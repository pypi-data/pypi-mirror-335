# Copyright (c) 2019-2024 Chris Pressey, Cat's Eye Technologies
# This file is distributed under an MIT license.  See LICENSES/ directory.
# SPDX-License-Identifier: LicenseRef-MIT-X-Feedmark


from io import StringIO
from urllib.parse import quote, quote_plus


def items_in_priority_order(di, priority):
    for key in priority:
        if key in di:
            yield key, di[key]
    for key, item in sorted(di.items()):
        if key not in priority:
            yield key, item
