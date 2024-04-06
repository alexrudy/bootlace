# SPDX-FileCopyrightText: 2024-present Alex Rudy <github@alexrudy.net>
#
# SPDX-License-Identifier: MIT
from . import __about__
from ._version import __version__
from .extension import Bootlace
from .util import _monkey_patch_dominate
from .util import as_tag
from .util import render

__all__ = ["__version__", "__about__", "as_tag", "render", "Bootlace"]


_monkey_patch_dominate()
