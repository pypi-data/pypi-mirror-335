from lino_avanti.projects.avanti.settings import *


class Site(Site):
    title = "Our Lino Avanti site"


SITE = Site(globals())
DEBUG = True
