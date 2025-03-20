============================
Older changes in Lino Avanti
============================


2018-01-24
==========

- Der neue Klientenzustand "Empfangsbestätigung" fehlte noch.

Abmahnungen :

- Feld "Ausgestellt am" umbenennen nach "Situation am", und dieses
  Feld automatisch ausfüllen mit dem Datum der "letzten Stunde, für
  die der Kursleiter seine Anwesenheiten erfasst hat". Die Lehrer
  erfassen die Anwesenheiten manchmal verspätet, aber Mahnungen können
  nicht warten.

- Neuer ReminderState "Storniert" für wenn eine gültige Entschuldigung
  erst nach Verschicken der Mahnung eingereicht wird.

Verwaltung der Erstkontakte:

- Neuer Klientenzustand "Empfangsbestätigung"
- insert_layout in EntriesByClient : Eintragsart rein, Enddatum raus
- Unbestätigte Termine : (1) default 1 Woche vorher und (2) ins
  Dashboard rein


  

Version 0.0.1
=============

This project was first publised on 2016-08-07.
