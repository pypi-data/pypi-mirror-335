# -*- coding: UTF-8 -*-
# Copyright 2017-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""

.. autosummary::
   :toctree:

   doctests
   demo
   memory
   fixtures



"""

from lino.projects.std.settings import *
from lino.api.ad import _
from lino_avanti import __version__, intersphinx_urls


class Site(Site):

    verbose_name = "Lino Avanti"
    version = __version__
    url = intersphinx_urls['docs']

    demo_fixtures = [
        'std',
        'few_languages',
        'compass',
        # 'all_countries', 'all_languages',
        'demo',
        'demo2',
        'demo3',
        'checkdata'
    ]
    user_types_module = 'lino_avanti.lib.avanti.user_types'
    workflows_module = 'lino_avanti.lib.avanti.workflows'
    custom_layouts_module = 'lino_avanti.lib.avanti.layouts'
    migration_class = 'lino_avanti.lib.avanti.migrate.Migrator'

    project_model = 'avanti.Client'
    textfield_format = 'plain'
    # textfield_format = 'html'
    # use_silk_icons = False
    default_build_method = "appypdf"

    webdav_protocol = 'webdav'
    # beid_protocol = 'beid'

    auto_configure_logger_names = 'lino lino_xl lino_avanti'

    def get_installed_plugins(self):
        """Implements :meth:`lino.core.site.Site.get_installed_plugins`.

        """
        yield super(Site, self).get_installed_plugins()
        yield 'lino.modlib.help'
        yield 'lino_avanti.lib.users'
        # yield 'lino.modlib.users'
        yield 'lino_xl.lib.countries'
        yield 'lino_avanti.lib.contacts'
        # yield 'lino_xl.lib.extensible'
        yield 'lino_avanti.lib.cal'
        yield 'lino_xl.lib.calview'
        yield 'lino_avanti.lib.avanti'
        yield 'lino.modlib.comments'
        yield 'lino.modlib.notify'
        yield 'lino.modlib.changes'
        yield 'lino_xl.lib.clients'
        yield 'lino_xl.lib.uploads'
        yield 'lino.modlib.dupable'
        # yield 'lino_xl.lib.households'
        yield 'lino_avanti.lib.households'
        # yield 'lino_welfare.modlib.households'
        # yield 'lino_xl.lib.humanlinks'
        yield 'lino_xl.lib.lists'
        # yield 'lino_xl.lib.notes'
        yield 'lino_xl.lib.beid'
        yield 'lino_avanti.lib.cv'
        yield 'lino_xl.lib.trends'
        yield 'lino_xl.lib.polls'

        yield 'lino_avanti.lib.courses'  # pupil__gender
        # yield 'lino_xl.lib.courses'
        # yield 'lino_xl.lib.rooms'

        yield 'lino.modlib.checkdata'
        yield 'lino.modlib.export_excel'
        # yield 'lino.modlib.tinymce'
        yield 'lino.modlib.weasyprint'
        yield 'lino_xl.lib.excerpts'
        yield 'lino.modlib.dashboard'
        yield 'lino_xl.lib.appypod'
        # yield 'lino.modlib.davlink'

        # yield 'lino_xl.lib.votes'
        # yield 'lino_avanti.lib.tickets'
        # yield 'lino_xl.lib.tickets'
        # yield 'lino_xl.lib.skills'

    # def setup_plugins(self):
    #     super(Site, self).setup_plugins()
    #     self.plugins.cv.configure(
    #         person_model = 'avanti.Client')
    #     # self.plugins.humanlinks.configure(
    #     #     person_model = 'contacts.Person')
    #         # person_model = 'avanti.Client')
    #     # self.plugins.households.configure(
    #     #     person_model = 'contacts.Person')
    #         # person_model='avanti.Client')
    #     self.plugins.cal.configure(
    #         partner_model='avanti.Client')
    #     # self.plugins.skills.configure(
    #     #     end_user_model='avanti.Client')
    #     self.plugins.clients.configure(
    #         client_model='avanti.Client')
    #     self.plugins.trends.configure(
    #         subject_model='avanti.Client')
    #     # self.plugins.comments.configure(
    #     #     user_must_publish=False)

    def get_plugin_configs(self):
        yield super(Site, self).get_plugin_configs()
        yield ('cv', 'with_language_history', True)
        yield ('cv', 'person_model', 'avanti.Client')
        yield ('cal', 'partner_model', 'avanti.Client')
        yield ('clients', 'client_model', 'avanti.Client')
        yield ('trends', 'subject_model', 'avanti.Client')
        yield ('uploads', 'expiring_start', -30)
        yield ('uploads', 'expiring_end', 365)
        yield ('uploads', 'with_volumes', False)
        yield ('weasyprint', 'header_height', 30)
        yield ('comments', 'emotion_range', 'social')

    def setup_quicklinks(self, ut, tb):
        super(Site, self).setup_quicklinks(ut, tb)
        Clients = self.models.avanti.MyClients
        tb.add_action(Clients)
        tb.add_action(Clients.insert_action,
                      label=_("New {}").format(
                          Clients.model._meta.verbose_name))
        # tb.add_action(Clients, 'find_by_beid')
        tb.add_action(self.models.avanti.Clients.get_action_by_name('find_by_beid'))

    # def do_site_startup(self):

    def setup_actions(self):
        super().setup_actions()

        from lino.modlib.changes.utils import watch_changes as wc

        wc(self.models.avanti.Client)
        # wc(self.models.contacts.Person, master_key='partner_ptr')
        # wc(self.models.contacts.Company, master_key='partner_ptr')
        # wc(self.models.pcsw.Client, master_key='partner_ptr')

        # wc(self.models.coachings.Coaching, master_key='client__partner_ptr')
        wc(self.models.cal.Guest, master_key='partner')


# the following line should not be active in a checked-in version
# DATABASES['default']['NAME'] = ':memory:'

USE_TZ = True
TIME_ZONE = 'UTC'
