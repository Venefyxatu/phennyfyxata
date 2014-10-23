#!/usr/bin/env python
# coding=utf-8

import random
from collections import deque


genre_cache = deque()
max_cache_size = 5


def genre(phenny, input):
    """
    Say a random genre
    """
    genres = ['spaghettihorror', 'romantische spookverhalen',
              'hottentottententententoonstellingenmysterie',
              'aliens in fantasy', 'kiezeldetective',
              'macho women with guns', 'heroic bloodshed',
              'zombie komedie', 'sumodrama', 'ijslolliepolitiek',
              'lantaarnpaalsatire', 'landbouw op zee actie',
              'kattige karikatuur', 'road trip liedjesbundel',
              'mythologische detective', 'therapeutische thriller',
              'robotwestern', 'privatiserende plotbunnies',
              'rookworsten romance', 'complex computerprobleem detective',
              'flessenpostroman', 'held-op-sokken-avontuur',
              'geitewollensokkenmysterie', 'culinaire science fiction',
              'broodje aap verhaal', 'database shenanigans',
              'hoelahoepieromantiek', 'tijdreizende theezakjes',
              'maniakale mandalas',
              'historische thriller met planetoïden-etende melkwegen',
              ]

    chosen = random.choice(genres)
    while chosen in genre_cache:
        chosen = random.choice(genres)

    if len(genre_cache) > max_cache_size:
        genre_cache.popleft()

    genre_cache.append(chosen)

    phenny.say(chosen)


genre.rule = r'.*(geef.*een genre|heb je nu al een genre voor.*\?)'

if __name__ == '__main__':
    print __doc__.strip()
