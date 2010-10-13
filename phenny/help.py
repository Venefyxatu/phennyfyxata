#!/usr/bin/env python
# coding=utf-8

import random

from validation import _SCORE_COMMAND
from collections import deque

topics = ["war", "smileys", "nick", "motivation", "roulette", "voedsel"]

topicCache = deque()

def motivation_help(phenny, nick):
    choices = ["GA SCHRIJVEN, %s!" % nick,
            "Zou je niet beter wat schrijven in plaats van mij te storen? Ik ben al gestoord genoeg...",
            "Gewoon het ene woord na het andere zetten!",
            "Kom op, je kunt het, %s!" % nick,
            "en wat gebeurde er toen, %s?" % nick,
            "%s, laat je characters een hapje eten?" % nick,
            "%s, laat een van je characters een boterham smeren en beschrijf alles in detail. Maar wel een GROTE boterham he, want ik heb honger!" % nick,
            "Misschien helpt dit? http://phenny.venefyxatu.be/inspiration.jpg",
            "Je zou me heel gelukkig maken als je wat ging schrijven, %s" % nick,
            "30 november nadert sneller dan je zou denken... met een beetje moeite haal je het wel!",
            "Geef me een S! Geef me een c! Geef me een h! Geef me... weet je wat? Schrij-ven! Schrij-ven! Schrij-ven! *\o/* o//** **\\o */o\* *\o/*",
            "Misschien moet je een war organiseren? Wars helpen altijd!",
            "Schrijf een zin waarin je het woord tafelpoot gebruikt",
            "Komkom, nog een klein beetje. *aait %s over het hoofd*" % nick,
            "Hup %s hup! Hup %s hup! Jeeeeeeee! *\o/*" % (nick, nick),
            "Nog eventjes doorbijten! Dan haal je het en dan is het parrr-tayyy-tijd!",
            ]
    chosen = random.choice(choices)
    while chosen in topicCache:
        chosen = random.choice(choices)

    if len(topicCache) >= 5:
        topicCache.popleft()
    topicCache.append(chosen)

    phenny.say(chosen)

def general_help(phenny):
    phenny.say("Je kan me om hulp vragen over de volgende onderwerpen met .help <onderwerp>")
    phenny.say(", ".join(topics))

def nick_help(phenny):
    phenny.say("Je kan je naam veranderen met /nick <nieuwenaam>")

def smileys_help(phenny):
    phenny.say("Dit zijn enkele vaak gebruikte smileys en hoe je ze maakt: ")
    phenny.say(":-) is : - )")
    phenny.say(":( is : (")
    phenny.say("O_o en O.o zijn O _ o en O . o")

def war_help(phenny):
    phenny.say("Ik zal je vertellen wanneer je moet starten en stoppen met schrijven als je mij een begin- en einduur geeft.")
    phenny.say("Zorg ervoor dat je het 24-uren formaat gebruikt, want anders raak ik in de war.")
    phenny.say("bv. als je een war wil tussen 15:00 en 15:15, dan zeg je .war 15:00 15:15")
    phenny.say("Als ik gewoon het stopsignaal moet geven gebruik je het woordje 'busy' in plaats van een starttijd")
    phenny.say("Ik kan ook je score bijhouden. Daarvoor zeg je gewoon %s <war nr> <score> en ik schrijf 'm op samen met je nick." % _SCORE_COMMAND)
    phenny.say("Je kan de scores bekijken op http://phenny.venefyxatu.be")

def voedsel_help(phenny):
    phenny.say("Af en toe heb je voedsel nodig. Ik ben dan misschien maar een bot, maar geloof me toch maar.")
    phenny.say("Echt voedsel wordt enkel in het echt geleverd... hier moet je het stellen met een digitale sandwich. Gebruik .food of .noms")

def roulette_help(phenny):
    phenny.say("Als je het helemaal niet meer ziet zitten kan je misschien een virtueel spelletje Russische roulette spelen...")
    phenny.say("Je stopt een kogel in de revolver met .load")
    phenny.say("Vervolgens draai je met .spin")
    phenny.say("Als je het dan nog steeds niet ziet zitten haal je de trekker over met .pull")
    phenny.say("DOE DIT NIET IN HET ECHT, want dan kan je eraan doodgaan!")

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
    elif arguments == "voedsel":
        voedsel_help(phenny)
    elif arguments == "roulette":
        roulette_help(phenny)
    else:
        general_help(phenny)


help.commands = ["help"]
help.example = '.help'

if __name__ == '__main__': 
    print __doc__.strip()