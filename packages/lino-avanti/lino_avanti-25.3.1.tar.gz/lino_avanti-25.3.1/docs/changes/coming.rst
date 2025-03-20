.. _avanti.changes.coming:

================
Kommende Version
================

- Vorschau verfügbar seit 05.06.2023

ÄNDERUNGEN:

- Das :term:`front end` ist nicht mehr ExtJS sondern React.

- Lino lässt jetzt Dossiernummern (:attr:`avanti.Client.ref`) mit mehr als 4
  Stellen zu. Wenn die letzte Eupener Dossiernummer "IP 6999" vergeben ist,
  schlägt Lino bei Eingabe von "ip6" jetzt "IP 61000" vor. Die alte Version
  schlägt in diesem Fall "IP 7000" vor. Diese Sonderregel ist übrigens `hier
  dokumentiert
  <https://dev.lino-framework.org/specs/avanti/avanti.html#the-legacy-file-number>`__.

- Feld :attr:`nationality_text <lino_xl.lib.beid.BeIdCardHolder.nationality_text>`
  wird jetzt in der Detailansicht anstelle von "Nationalität 2" angezeigt.

- (:guilabel:`[eID-Karte einlesen]` funktionierte anfangs nicht in der neuen
  Version.)

TODO

- Hochladen von Dateien über Drag & Drop
- Überprüfen, ob :attr:`nationality_text <lino_xl.lib.beid.BeIdCardHolder.nationality_text>`
