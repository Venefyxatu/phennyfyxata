#!/usr/bin/env python
# coding=utf-8

import urllib2
from xml.dom import minidom
import sqlite3
import os


def openUrl(url):
    """ Open een URL en geef deze als leesbare resource terug """
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url)
    request.add_header('Content-Type', 'text/http')
    request.get_method = lambda: 'GET'
    resource = opener.open(request)
    return resource


def userstats(phenny, input):
    """ Haalt de user zijn wordcount op adhv de nanowrimo API """
    command, nick = input.groups()
    if not nick:
        nick = input.nick
    slugnick = searchNanoByIRC(nick)
    if not slugnick:
        slugnick = nick.lower()  # simple and probably wrong
        phenny.say(
            "Ik weet niet zeker of ik met de juiste nickname zoek, maar ik doe het met '{}'".format(
                slugnick))
        phenny.say(
            "(Als dit fout zou zijn, identificeer jezelf dan met .ikben <nano-gebruikersnaam>)")
    phenny.say(
        "Even zoeken hoeveel woordjes {0!s} ('{1!s}') al geschreven heeft...".format(nick,
                                                                                     slugnick))
    url = "http://nanowrimo.org/wordcount_api/wc/{}".format(slugnick)
    resource = openUrl(url)
    result = resource.read()
    xmldoc = minidom.parseString(result)
    woordjes = xmldoc.getElementsByTagName("user_wordcount")
    if woordjes:
        phenny.say(
            "{0!s} heeft zowaar al {1} woordjes geschreven!".format(nick,
                                                                    woordjes[0].firstChild.data))
    else:
        phenny.say("Blijkbaar bestaat er niemand met de nano-gebruikersnaam '{}'".format(slugnick))

userstats.commands = ['woordjes']
userstats.example = ".woordjes OF .woordjes <irc nick>"


def ikben(phenny, input):
    """ User zegt wie hij/zij zelf is """
    command, nanonick = input.groups()
    if not nanonick:
        phenny.say("Je moet wel zeggen wie je bent he... met .ikben <nano-gebruikersnaam>")
        phenny.say(
            "Je vindt je gebruikersnaam in de URL van je profiel, bvb "
            "http://nanowrimo.org/participants/lambik")
        return
    saveIRCByNano(input.nick, nanonick)
    phenny.say("Ok {0!s}, ik heb je onthouden als '{1!s}'".format(input.nick, nanonick))

ikben.commands = ['ikben']
ikben.example = (".ikben <nano-gebruikersnaam> (die je kunt vinden in de URL van je profiel, "
                 "bvb http://nanowrimo.org/participants/lambik)")


def hijis(phenny, input):
    """ User zegt wie iemand anders is """
    command, args = input.groups()
    ircnick, nanonick = args.split()
    if not ircnick:
        phenny.say("Over wie hebben we het? Je moet me zijn IRC nickname zeggen he... met .hijis "
                   "<irc nickname> <nano-gebruikersnaam>")
        phenny.say("Je vindt zijn gebruikersnaam in de URL van zijn profiel, bvb "
                   "http://nanowrimo.org/participants/lambik")
        return
    if not nanonick:
        phenny.say("Je moet wel zeggen wie hij is he... met .hijis "
                   "<irc nickname> <nano-gebruikersnaam>")
        phenny.say("Je vindt zijn gebruikersnaam in de URL van zijn profiel, bvb "
                   "http://nanowrimo.org/participants/lambik")
        return
    saveIRCByNano(ircnick, nanonick)
    phenny.say("Ok {0!s}, ik heb onthouden dat {1!s} gekend staat als '{2!s}'".format(input.nick,
                                                                                      ircnick,
                                                                                      nanonick))

hijis.commands = ['hijis']
hijis.example = (".hijis <irc nickname> <nano-gebruikersnaam> (die je kunt vinden in de URL van "
                 "zijn profiel, bvb http://nanowrimo.org/participants/lambik)")


def zijis(phenny, input):
    """ User zegt wie iemand anders is """
    command, args = input.groups()
    ircnick, nanonick = args.split()
    if not ircnick:
        phenny.say("Over wie hebben we het? Je moet me haar IRC nickname zeggen he... met .zijis "
                   "<irc nickname> <nano-gebruikersnaam>")
        phenny.say("Je vindt haar gebruikersnaam in de URL van haar profiel, bvb "
                   "http://nanowrimo.org/participants/lambik")
        return
    if not nanonick:
        phenny.say("Je moet wel zeggen wie zij is he... met .zijis "
                   "<irc nickname> <nano-gebruikersnaam>")
        phenny.say("Je vindt haar gebruikersnaam in de URL van haar profiel, bvb "
                   "http://nanowrimo.org/participants/lambik")
        return
    saveIRCByNano(ircnick, nanonick)
    phenny.say("Ok {0!s}, ik heb onthouden dat {1!s} gekend staat als '{2!s}'".format(input.nick,
                                                                                      ircnick,
                                                                                      nanonick))

zijis.commands = ['zijis']
zijis.example = (".zijis <irc nickname> <nano-gebruikersnaam> (die je kunt vinden in de URL van "
                 "haar profiel, bvb http://nanowrimo.org/participants/lambik)")


def createDB():
    """ maak een lege sqlite database """
    tmpcon = sqlite3.connect(DBFILE)
    cur = tmpcon.cursor()
    cur.execute("CREATE TABLE irc2nano(id INTEGER PRIMARY KEY, irc VARCHAR, nano VARCHAR);")
    # cur.execute("INSERT INTO triggers(irc, nano) VALUES ('Lambik', 'lambik');")
    tmpcon.commit()
    cur.close()
    tmpcon.close()


def searchNanoByIRC(irc):
    """ zoek in de sqlite database """
    db = sqlite3.connect(DBFILE)
    db.text_factory = str
    c = db.cursor()
    c.execute('select nano from irc2nano where irc = ?', (str(irc),))
    nano = c.fetchone()
    c.close()
    db.close()
    if nano:
        return nano[0]
    return None


def saveIRCByNano(ircnick, nanonick):
    """ Opslaan in de database """
    db = sqlite3.connect(DBFILE)
    db.text_factory = str
    c = db.cursor()
    c.execute('select id from irc2nano where irc = ?', (str(ircnick),))
    id = c.fetchone()
    if id:
        c.execute('update irc2nano set nano = ? where id = ?', (str(nanonick), id[0],))
    else:
        c.execute('insert into irc2nano(irc, nano) values (?, ?)', (str(ircnick), str(nanonick),))
    db.commit()
    c.close()
    db.close()


DBFILE = 'nano.sqlite'
if not os.path.isfile(DBFILE):
    createDB()

if __name__ == '__main__':
    print __doc__.strip()
