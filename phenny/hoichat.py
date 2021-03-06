#!/usr/bin/env python
# coding=utf-8

import random


def hoichat(phenny, input):
    """
    Hoi chat
    """
    greetings = ['Hoi', 'Hallo', 'Hey', 'Dag', 'Wees gegroet,', 'Allo', 'Yo', 'Hai', 'Bonjour',
                 'Howdi', 'Hee']
    if input.nick.lower() == 'maria':
        phenny.say('Ave %s' % input.nick)
    else:
        phenny.say("%s %s" % (random.choice(greetings), input.nick))


hoichat.rule = r'(?i)^(en )?(ho+i|ha+i|hello|hallo|hey)( chat| iedereen| phenny(fyxata)?).*$'

if __name__ == '__main__':
    print __doc__.strip()
