#!/usr/bin/env python
# coding=utf-8

import time
import random

from collections import deque

topics = ["war", "smileys", "nick", "motivation", "roulette", "voedsel", "plannedwars", "activewars", "participate", "withdraw"]
randomwords = ['tafelpoot', 'olifantenteennagel', 'rijstpap', 'autoradioantennevlaggetje', 'muggenvleugel', ]

action = chr(1) + "ACTION "

topicCache = deque()


def motivation_help(phenny, input):
    choices = ["GA SCHRIJVEN, %s!" % input.nick,
            "Gewoon het ene woord na het andere zetten, %s!" % input.nick,
            "Kom op, je kunt het, %s!" % input.nick,
            "en wat gebeurde er toen, %s?" % input.nick,
            "%s, laat je characters een hapje eten?" % input.nick,
            "%s, laat een van je characters een boterham smeren en beschrijf alles in detail. Maar wel een GROTE boterham he, want ik heb honger!" % input.nick,
            "Hier %s, speciaal voor jou! http://phenny.venefyxatu.be/inspiration.jpg" % input.nick,
            "Je zou me heel gelukkig maken als je wat ging schrijven, %s" % input.nick,
            "30 november nadert sneller dan je zou denken... met een beetje moeite haal je het wel!",
            "Geef me een S! Geef me een c! Geef me een h! Geef me... weet je wat? Schrij-ven! Schrij-ven! Schrij-ven! *\o/* o//** **\\o */o\* *\o/*",
            "Misschien moet je een war organiseren, %s? Wars helpen altijd!" % input.nick,
            "%s, ik eis een zin in je verhaal waarin je het woord %s gebruikt." % (input.nick, random.choice(randomwords)),
            "Komkom, nog een klein beetje. *aait %s over het hoofd*" % input.nick,
            "Hup %s hup! Hup %s hup! Jeeeeeeee! *\o/*" % (input.nick, input.nick),
            "Nog eventjes doorbijten! Dan haal je het en dan is het parrr-tayyy-tijd!",
            action + "houdt een bordje omhoog met 'Minder miepen, meer tiepen!'",
            "Beschrijf het landschap tot in detail. Gooi er nu een mega-aardbeving tegenaan. Of een atoombom. Nu kan je het volledig veranderde landschap nog eens beschrijven!",
            "Bekijk dit eens: http://phenny.venefyxatu.be/Procrastination.jpg",
            action + "pomponeert voor %s" % input.nick,
            "Je hebt duidelijk meer koffie, red bull, appels, chocolade, nog chocolade of nog VEEL MEER chocolade nodig, %s" % input.nick,
            "%s, zoals Ralph Waldo Emerson ooit zei: \"Every artist was once an amateur.\"" % input.nick,
            "%s, zoals Arthur C. Clarke ooit zei: \"The only way of finding the limits of the possible is by going beyond them into the impossible.\"" % input.nick,
            "%s, zoals Aristoteles ooit zei: \"We zijn wat we herhaaldelijk doen. Daarom is uitmuntendheid geen daad maar een gewoonte.\" Hetzelfde geldt voor schrijverschap, dus maak er maar snel een gewoonte van!" % input.nick,
            "%s, er is een Latijns spreekwoord: Destitus ventis, remos adhibe. Vrij vertaald: als de woorden zichzelf niet op je virtuele papier zetten moet je ze uit je toetsenbord rammen." % input.nick,
            "%s, zoals Robert Frost zei: \"The best way out is always through.\" Blijf dus dapper verderschrijven aan de weg door je NaNo!" % input.nick,
            "Hier is een tip van F. Scott Fitzgerald, %s: \"What people are ashamed of usually makes a good story.\". Ga nu, en schrijf!" % input.nick,
            "Probeer dit eens, %s: http://bit.ly/ps4KZ2" % input.nick,
            "Zoals Jarsto het zo mooi zegt: BICHOK! Butt In Chair, Hands On Keyboard.",
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
    phenny.say("Ik kan ook je score bijhouden. Daarvoor zeg je gewoon .score <war nr> <score> en ik schrijf 'm op samen met je nick.")
    phenny.say("Als je 0 opgeeft als score verwijder ik 'm weer, dat kan handig zijn als je je score op een verkeerde war hebt gezet.")
    phenny.say("Je kan de scores bekijken op http://phenny.venefyxatu.be")


def voedsel_help(phenny):
    phenny.say("Af en toe heb je voedsel nodig. Ik ben dan misschien maar een bot, maar geloof me toch maar.")
    phenny.say("Echt voedsel wordt enkel in het echt geleverd... hier moet je het stellen met een digitale sandwich. Gebruik .eten of .noms")


def roulette_help(phenny):
    phenny.say("Als je het helemaal niet meer ziet zitten kan je misschien een virtueel spelletje Russische roulette spelen...")
    phenny.say("Je stopt een kogel in de revolver met .load")
    phenny.say("Vervolgens draai je met .spin")
    phenny.say("Als je het dan nog steeds niet ziet zitten haal je de trekker over met .pull")
    phenny.say("DOE DIT NIET IN HET ECHT, want dan kan je eraan doodgaan!")


def plannedwars_help(phenny):
    phenny.say("Je kan een overzicht krijgen van welke wars gepland zijn met het commando .plannedwars")


def activewars_help(phenny):
    phenny.say("Je kan een overzicht krijgen van welke wars bezig zijn met het commando .activewars")


def participate_help(phenny):
    phenny.say('Ik kan je persoonlijk verwittigen door je nick te vermelden 10 seconden voordat een war begint, en ook weer wanneer hij afloopt.')
    phenny.say('Als je dat wil, zeg dan .participate <war nr>')


def withdraw_help(phenny):
    phenny.say('Als je voor een war toch geen verwittiging wil ontvangen, zeg dan .withdraw <war nr>.')


def help(phenny, input):
    """
    Show the help
    """
    print "%s New command received in help module" % time.localtime()
    arguments = input.group(2)

    if arguments == "war":
        war_help(phenny)
    elif arguments == "smileys":
        smileys_help(phenny)
    elif arguments == "nick":
        nick_help(phenny)
    elif arguments in ["motivation", "motivatie"]:
        motivation_help(phenny, input)
    elif arguments == "voedsel":
        voedsel_help(phenny)
    elif arguments == "plannedwars":
        plannedwars_help(phenny)
    elif arguments == "activewars":
        activewars_help(phenny)
    elif arguments == "participate":
        participate_help(phenny)
    elif arguments == "withdraw":
        withdraw_help(phenny)
    else:
        general_help(phenny)


help.commands = ["help"]
help.example = '.help'

if __name__ == '__main__':
    print __doc__.strip()
