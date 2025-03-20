# -*- coding: UTF-8 -*-
# Copyright 2017-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Demo data for Lino Avanti.

- Change name of persons and create a client MTI child for them.

"""

from django.conf import settings
# from lino.utils import mti
from lino.utils.mti import mtichild
from lino.utils.ssin import generate_ssin
from lino.utils import Cycler, join_words
# from lino.utils.instantiator import create_row
from lino.api import rt, dd, _
from lino.utils.mldbc import babel_named as named
from lino.utils.mldbc import babeld
from lino_xl.lib.clients.choicelists import KnownContactTypes


def next_choice(cls, choice):
    for i, v_c in enumerate(cls.choices):
        v, c = v_c
        if v == choice and i + 1 < len(cls.choices):
            return cls.choices[i + 1][0]

from commondata.demonames import muslim, russian, african

def get_last_names():
    yield Cycler(muslim.LAST_NAMES)
    yield Cycler(russian.LAST_NAMES)
    yield Cycler(african.LAST_NAMES)


def get_male_first_names():
    yield Cycler(muslim.MALE_FIRST_NAMES)
    yield Cycler(russian.MALE_FIRST_NAMES)
    yield Cycler(african.MALE_FIRST_NAMES)


def get_female_first_names():
    yield Cycler(muslim.FEMALE_FIRST_NAMES)
    yield Cycler(russian.FEMALE_FIRST_NAMES)
    yield Cycler(african.FEMALE_FIRST_NAMES)


LAST_NAMES = Cycler(get_last_names())
MALES = Cycler(get_male_first_names())
FEMALES = Cycler(get_female_first_names())


def objects():

    Person = rt.models.contacts.Person
    Company = rt.models.contacts.Company
    Client = rt.models.avanti.Client
    ClientContact = rt.models.clients.ClientContact
    ClientContactType = rt.models.clients.ClientContactType
    TranslatorTypes = rt.models.avanti.TranslatorTypes
    ClientStates = rt.models.avanti.ClientStates
    EndingReason = rt.models.avanti.EndingReason
    Category = rt.models.avanti.Category
    LanguageKnowledge = rt.models.cv.LanguageKnowledge

    yield babeld(EndingReason, _("Successfully ended"), id=1)
    yield babeld(EndingReason, _("Health problems"), id=2)
    yield babeld(EndingReason, _("Familiar reasons"), id=3)
    yield babeld(EndingReason, _("Missing motivation"), id=4)
    yield babeld(EndingReason, _("Return to home country"), id=5)
    yield babeld(EndingReason, _("Other"), id=9)


    if dd.plugins.avanti.with_immigration:

        yield babeld(Category, _("Language course"))
        yield babeld(Category, _("Integration course"))
        yield babeld(Category, _("Language & integration course"))
        yield babeld(Category, _("External course"))
        yield babeld(Category, _("Justified interruption"))
        yield babeld(Category, _("Successfully terminated"))
    else:
        yield babeld(Category, _("Single"))
        yield babeld(Category, _("Worker"))
        yield babeld(Category, _("Families"))

    if dd.plugins.avanti.with_asylum:
        ResidencePermit = rt.models.avanti.ResidencePermit
        yield babeld(ResidencePermit, _("A card"))
        yield babeld(ResidencePermit, _("B card"))

        ResidenceReason = rt.models.avanti.ResidenceReason
        yield babeld(ResidenceReason, _("Economical"))
        yield babeld(ResidenceReason, _("Climate"))
        yield babeld(ResidenceReason, _("Political"))
        yield babeld(ResidenceReason, _("War"))
        yield babeld(ResidenceReason, _("Other"))

    # yield named(ClientContactType, _("Health insurance"))
    # yield named(ClientContactType, _("School"))
    # yield named(ClientContactType, _("Pharmacy"))
    # yield named(ClientContactType, _("GSS"))
    # yield named(ClientContactType, _("ISS"))
    for i in KnownContactTypes.get_list_items():
        yield i.create_object()

    yield named(ClientContactType, _("Other"))

    TRTYPES = Cycler(TranslatorTypes.objects())
    POLICIES = Cycler(rt.models.cal.EventPolicy.objects.all())
    CCTYPES = Cycler(ClientContactType.objects.all())

    for cct in ClientContactType.objects.all():
        yield Company(name="Favourite {}".format(cct), client_contact_type=cct)
        yield Company(name="Best {}".format(cct), client_contact_type=cct)

    CCT2COMPANIES = dict()
    for cct in ClientContactType.objects.all():
        CCT2COMPANIES[cct] = Cycler(
            Company.objects.filter(client_contact_type=cct))

    count = 0
    for person in Person.objects.all():
        count += 1
        if count % 7 and person.gender and not person.birth_date:
            # most persons, but not those from humanlinks and those
            # with empty gender field, become clients and receive a
            # new exotic name. Youngest client is 16; 170 days between
            # each client
            birth_date = settings.SITE.demo_date(-170 * count - 16 * 365)
            national_id = generate_ssin(birth_date, person.gender)

            client = mtichild(person,
                              Client,
                              national_id=national_id,
                              birth_date=birth_date)

            if count % 2:
                if hasattr(ClientStates, "coached"):
                    client.client_state = ClientStates.coached
                else:
                    client.client_state = ClientStates.active
                client.event_policy = POLICIES.pop()
            # elif count % 5:
            #     client.client_state = ClientStates.newcomer
            else:
                if hasattr(ClientStates, "coached"):
                    client.client_state = ClientStates.former
                else:
                    client.client_state = ClientStates.inactive

            # Dorothée is three times in our database
            if client.first_name == "Dorothée":
                client.national_id = None
                client.birth_date = ''
            else:
                p = client
                p.last_name = LAST_NAMES.pop()
                if p.gender == dd.Genders.male:
                    p.first_name = MALES.pop()
                    FEMALES.pop()
                else:
                    p.first_name = FEMALES.pop()
                    MALES.pop()
                p.first_name = p.first_name.replace('a', 'á')
                p.name = join_words(p.last_name, p.first_name)

            if count % 4:
                client.translator_type = TRTYPES.pop()

            # client.full_clean()
            # client.save()
            yield client

        else:
            pass
            # yield mtichild(
            #     person, Translator, translator_type=TT.pop())

    CefLevel = rt.models.cv.CefLevel
    LANGUAGES = Cycler(rt.models.languages.Language.objects.all())
    HOW_WELL = Cycler(rt.models.cv.HowWell.get_list_items())
    CEF_LEVELS = Cycler(CefLevel.get_list_items())
    LK_COUNTS = Cycler(1, 2, 3, 2, 1, 4)

    def language_knowledge(person, offset, language, native, **kwargs):
        kwargs.update(entry_date=dd.today(offset))
        kwargs.update(language=language, native=native)
        if not native:
            kwargs.update(spoken=HOW_WELL.pop(),
                          written=HOW_WELL.pop(),
                          spoken_passively=HOW_WELL.pop(),
                          written_passively=HOW_WELL.pop(),
                          cef_level=CEF_LEVELS.pop())
            kwargs.update(has_certificate=person.id % 2)
        return LanguageKnowledge(person=person, **kwargs)

    for i, obj in enumerate(Client.objects.all()):
        for j in range(i % 2):
            cct = CCTYPES.pop()
            company = CCT2COMPANIES[cct].pop()
            yield ClientContact(type=cct, client=obj, company=company)

        # if obj.client_state == ClientStates.coached:
        if obj.client_state.name in {'coached', 'active'}:
            for i in range(LK_COUNTS.pop()):
                yield language_knowledge(obj, -400, LANGUAGES.pop(), i == 0)
            lk = LanguageKnowledge.objects.filter(person=obj,
                                                  native=False).first()
            if lk:
                better = next_choice(CefLevel, lk.cef_level)
                if better:
                    # raise Exception("okay")
                    new_lk = language_knowledge(obj, -10, lk.language, False)
                    new_lk.cef_level = better
                    yield new_lk


    obj = Client.objects.get(id=142)
    obj.financial_notes = '<p>ÖSHZ</p><p><br></p>'
    obj.family_notes = '<p>Lives here with husband and 2 children (20 and 14 yo)</p>'
    obj.integration_notes = 'This is a note in plain text\n'
    yield obj
