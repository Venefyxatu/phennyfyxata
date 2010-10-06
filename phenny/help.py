#!/usr/bin/env python
# coding=utf-8

import random

from validation import _SCORE_COMMAND

topics = ["war", "smileys", "nick", "motivation"]

def motivation_help(phenny, nick):
    choices = ["GA SCHRIJVEN, %s!" % nick,
            "Zou je niet beter wat schrijven in plaats van mij te storen?",
            "Gewoon het ene woord na het andere zetten!",
            "Kom op, je kunt het, %s!" % nick,
            "en wat gebeurde er toen, %s?" % nick,
            "%s, laat je characters een hapje eten?" % nick,
            "%s, laat een van je characters een boterham smeren en beschrijf alles in detail. Maar wel een GROTE boterham he, want ik heb honger!" % nick,
            "Misschien helpt dit? http://phenny.venefyxatu.be/inspiration.jpg",
            ]
    phenny.say(random.choice(choices))

def general_help(phenny):
    phenny.say("Je kan me om hulp vragen over de volgende onderwerpen met .help <onderwerp>")
    phenny.say(", ".join(topics))

def nick_help(phenny):
    phenny.say("Je kan je naam veranderen met /nick <nieuwenaam>")

def smileys_help(phenny):
    phenny.say("Dit zijn enkele vaak gebruikte smileys en hoe je ze maakt: ")
    phenny.say(":-) is : - )")
    phenny.say(":( is : (")
    phenny.say("O_o en O.o are O _ o en O . o")

def war_help(phenny):
    phenny.say("Ik zal je vertellen wanneer je moet starten en stoppen met schrijven als je mij een begin- en einduur geeft.")
    phenny.say("Zorg ervoor dat je het 24-uren formaat gebruikt, want anders raak ik in de war.")
    phenny.say("bv. als je een war wil tussen 15:00 en 15:15, dan zeg je .war 15:00 15:15")
    phenny.say("Als ik gewoon het stopsignaal moet geven gebruik je het woordje 'busy' in plaats van een starttijd")
    phenny.say("Ik kan ook je score bijhouden. Daarvoor zeg je gewoon %s <war nr> <score> en ik schrijf 'm op samen met je nick." % _SCORE_COMMAND)
    phenny.say("Je kan de scores bekijken op http://phenny.venefyxatu.be")

def help(phenny, input): 
    """
    Show the help
    """
    print "New command received in help module"
    arguments = input.group(2)
    command = input.group(1)

    if arguments == "war":
        war_help(phenny)
    elif arguments == "smileys":
        smileys_help(phenny)
    elif arguments == "nick":
        nick_help(phenny)
    elif arguments in ["motivation", "motivatie"]:
        motivation_help(phenny, input.nick)
    else:
        general_help(phenny)


help.commands = ["help"]
help.example = '.help'

if __name__ == '__main__': 
    print __doc__.strip()
