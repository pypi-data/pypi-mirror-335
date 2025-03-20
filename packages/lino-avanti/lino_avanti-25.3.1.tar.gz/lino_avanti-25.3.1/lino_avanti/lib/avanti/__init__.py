# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
The main plugin for Lino Avanti.

See :doc:`/specs/avanti/avanti`.

.. autosummary::
   :toctree:

    migrate
    layouts
    choicelists

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."

    verbose_name = _("Master")

    needs_plugins = ['lino_xl.lib.countries']

    with_asylum = False
    with_immigration = True

    def setup_main_menu(self, site, user_type, m, ar=None):
        mg = site.plugins.contacts
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('avanti.Clients')
        m.add_action('avanti.MyClients')
        # m.add_action('avanti.Translators')
        # m.add_action('courses.CourseProviders')
        # m.add_action('coachings.CoachedClients')
        # m.add_action('coachings.MyCoachings')

    def setup_config_menu(self, site, user_type, m, ar=None):
        mg = site.plugins.contacts
        # mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('avanti.Categories')
        m.add_action('avanti.EndingReasons')
        if self.with_asylum:
            m.add_action('avanti.ResidencePermits')
            m.add_action('avanti.ResidenceReason')

    def setup_explorer_menu(self, site, user_type, m, ar=None):
        mg = site.plugins.contacts
        # mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('avanti.AllClients')
        m.add_action('avanti.Residences')
