# SPDX-FileCopyrightText: 2024-present Alex Rudy <github@alexrudy.net>
#
# SPDX-License-Identifier: MIT
from . import __about__
from ._version import __version__
from .util import _monkey_patch_dominate

__all__ = ["__version__", "__about__"]


_monkey_patch_dominate()
