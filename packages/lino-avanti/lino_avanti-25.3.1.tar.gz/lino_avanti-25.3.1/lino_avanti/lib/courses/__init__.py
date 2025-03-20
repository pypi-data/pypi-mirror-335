# -*- coding: UTF-8 -*-
# Copyright 2017-2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""See :doc:`/specs/avanti/courses`.

"""

from lino_xl.lib.courses import Plugin


class Plugin(Plugin):

    extends_models = ['Course', 'Enrolment']

    teacher_model = 'contacts.Person'
    pupil_model = 'avanti.Client'
    pupil_name_fields = "pupil__last_name pupil__first_name"

    def setup_main_menu(self, site, user_type, main, ar=None):
        super(Plugin, self).setup_main_menu(site, user_type, main, ar)
        m = main.add_menu(self.app_label, self.verbose_name)
        m.add_action('courses.ActivityPlanning')
        m.add_action('courses.DitchingEnrolments')

    def setup_explorer_menu(self, site, user_type, main, ar=None):
        super(Plugin, self).setup_explorer_menu(site, user_type, main, ar)
        m = main.add_menu(self.app_label, self.verbose_name)
        m.add_action('courses.Reminders')
