#!/usr/bin/env python
# coding=utf-8

import random


text_prompts = []
image_prompts = []
text_prompt_store = "/opt/projects/phenny/text_prompts.txt"
image_prompt_store = "/opt/projects/phenny/image_prompts.txt"


def load_prompts():
    global text_prompts
    global image_prompts

    with open(text_prompt_store, 'r') as fp:
        text_prompts = fp.read().split('\n')

    with open(image_prompt_store, 'r') as fp:
        image_prompts = fp.read().split('\n')


def refresh_prompts(phenny, input):
    if input.owner:
        refresh_prompts()


refresh_prompts.rule = r'Phennyfyxata: je hebt nieuwe prompts'


def text_prompt(phenny, input):
    """
    Give a text prompt
    """
    phenny.say(random.choice(text_prompts))


text_prompt.commands = ["prompt", "textprompt"]
text_prompt.example = '.textprompt'


def image_prompt(phenny, input):
    """
    Give a image prompt
    """
    phenny.say(random.choice(image_prompts))


def setup(self):
    load_prompts()


image_prompt.commands = ["imageprompt"]
image_prompt.example = '.imageprompt'


if __name__ == '__main__':
    print __doc__.strip()
