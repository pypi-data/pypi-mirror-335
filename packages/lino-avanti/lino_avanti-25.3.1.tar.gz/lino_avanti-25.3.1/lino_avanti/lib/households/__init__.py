# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
This module extends :mod:`lino_xl.lib.households`

"""

from lino_xl.lib.households import Plugin


class Plugin(Plugin):

    extends_models = ['Member']
