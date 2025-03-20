# -*- coding: UTF-8 -*-
# Copyright 2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
Extends :mod:`lino_xl.lib.cv` for :ref:`avanti`.

See :doc:`/specs/avanti/cv`.

"""

from lino_xl.lib.cv import Plugin


class Plugin(Plugin):

    extends_models = ['Study']
