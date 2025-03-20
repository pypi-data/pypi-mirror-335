# -*- coding: UTF-8 -*-
# Copyright 2017-2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Default workflows for Lino Avanti.

This can be used as :attr:`workflows_module
<lino.core.site.Site.workflows_module>`

"""

from lino.api import _

# calendar events and presences:
from lino_xl.lib.cal.workflows.voga import *
# courses
from lino_avanti.lib.courses.workflows import *


class MarkExcused(dd.ChangeStateAction):

    required_states = 'invited'

    def get_action_permission(self, ar, obj, state):
        if not obj.event_id:
            return False
        if not obj.event.owner_id:
            return False
        owner = obj.event.owner
        if not isinstance(owner, rt.models.courses.Course):
            return False
        if not owner.can_excuse:
            return False
        return super().get_action_permission(ar, obj, state)




# same as in voga except that we remove transition to "excused"
GuestStates.clear_transitions()
GuestStates.present.add_transition(
    # "\u2611",  # BALLOT BOX WITH CHECK
    required_states='invited')
# help_text=_("Participant was present."))

GuestStates.missing.add_transition(
    # "☉",  # 2609 SUN
    required_states='invited')
# help_text=_("Participant was absent."))

GuestStates.excused.add_transition(MarkExcused)
# GuestStates.excused.add_transition(
#     # "⚕",  # 2695
#     required_states='invited')

GuestStates.invited.add_transition(
    # "☐",  # BALLOT BOX \u2610
    required_states='missing present excused cancelled')
# help_text=_("Reset state to invited."))

GuestStates.cancelled.add_transition(required_states='invited')

from lino_xl.lib.clients.choicelists import KnownContactTypes

KnownContactTypes.clear()
add = KnownContactTypes.add_item
add('10', _("Health insurance"), 'health_insurance')
add('20', _("School"), 'school')
add('30', _("Pharmacy"), 'pharmacy')
add('40', _("Public Center for Social Welfare"), 'social_center')
# add('40', _("General social assistant"), 'general_assistant')
# code 50 might still exist in their database but should be replaced by 40:
# in your restore.py function create_clients_clientcontacttype() say ::
# if known_contact_type == '50': known_contact_type = '40'
# add('50', _("Integration assistant"), 'unused_integ_assistant')
add('60', _("Work consultant"), 'work_consultant')
