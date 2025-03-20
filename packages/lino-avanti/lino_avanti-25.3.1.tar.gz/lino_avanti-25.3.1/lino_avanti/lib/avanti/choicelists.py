# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""The choicelists for this plugin.

"""

from lino.api import dd, _


class TranslatorTypes(dd.ChoiceList):
    """
    Types of registries for the Belgian residence.

    """
    verbose_name = _("Translator type")


add = TranslatorTypes.add_item
add('10', _("SETIS"))
add('20', _("Other"))
add('30', _("Private"))


class StartingReasons(dd.ChoiceList):

    verbose_name = _("Starting reason")


add = StartingReasons.add_item
add('100', _("Voluntarily"))
add('200', _("Mandatory"))


class OldEndingReasons(dd.ChoiceList):

    verbose_name = _("Old Ending reason")


add = OldEndingReasons.add_item
add('100', _("Successfully ended"))
add('200', _("Health problems"))
add('300', _("Familiar reasons"))
add('400', _("Missing motivation"))
add('500', _("Return to home country"))
add('900', _("Other"))


class ProfessionalStates(dd.ChoiceList):
    verbose_name = _("Professional situation")

add = ProfessionalStates.add_item
add('100', _("Student"))
add('200', _("Workless"))
add('300', _("Seeking"))
add('400', _("Employed"))
add('500', _("Independent"))
add('600', _("Retired"))  # pensioniert
add('700', _("Unemployable"))  # arbeitsunfähig

# Aufenthaltsstatus (befristet, unbefristet, unsicher, ohne)
# In migratio we don't need a "professional state" but a "residence state". We
# reconfigure the ProfessionalStates to hold "residence states".

class ResidenceStates(dd.ChoiceList):
    verbose_name = _("Residence state")
    verbose_name_plural = _("Residence states")

add = ResidenceStates.add_item
add('100', _("Temporary"))
add('200', _("Permanent"))
add('300', _("Uncertain"))
add('400', _("Without"))
