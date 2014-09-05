#!/usr/bin/env python
# coding=utf-8

import random


def genre(phenny, input):
    """
    Say a random genre
    """
    genres = ['spaghettihorror', 'romantische spookverhalen',
              'hottentottententententoonstellingenmysterie',
              'aliens in fantasy', 'kiezeldetective',
              'macho women with guns', 'heroic bloodshed',
              'zombie komedie', 'sumodrama', 'ijslolliepolitiek',
              'lantaarnpaalsatire', 'landbouw op zee actie']
    phenny.say(random.choice(genres))


genre.rule = r'.*(geef.*een genre|heb je nu al een genre voor.*\?)'

if __name__ == '__main__':
    print __doc__.strip()
