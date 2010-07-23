#!/usr/bin/env python

import re

_WAR_COMMAND = 'war'
_SCORE_COMMAND = 'score'

class PhennyError(Exception):
    def __str__(self):
        return repr(self.args[0].lstrip("'").rstrip("'").lstrip('"').rstrip('"'))

class ArgumentFormatError(PhennyError):
    pass

class ArgumentCountError(PhennyError):
    pass

class ArgumentTypeError(PhennyError):
    pass

class ArgumentOrderError(PhennyError):
    pass

class ArgumentSanitiser:
    @staticmethod
    def create(command):
        if command == _WAR_COMMAND:
            return WarSanitiser()
        elif command == _SCORE_COMMAND:
            return ScoreSanitiser()
        else:
            raise RuntimeError("%s is an unknown command" % command)

    def orderArguments(self, arguments):
        arguments.sort(reverse=True)
        return arguments

    def argumentsToLowerCase(self, arguments):
        result = list()
        for arg in arguments:
            result.append(arg.lower())

        return result

class WarSanitiser(ArgumentSanitiser):
    def sanitise(self, argumentString):
        splitArguments = argumentString.split()
        splitArguments = self.argumentsToLowerCase(splitArguments)
        if 'busy' in splitArguments:
            splitArguments = self.orderArguments(splitArguments)

        return splitArguments

class ScoreSanitiser(ArgumentSanitiser):
    def sanitise(self, argumentString):
        splitArguments = argumentString.split()
        splitArguments = self.argumentsToLowerCase(splitArguments)
        splitArguments = self.orderArguments(splitArguments)

        return splitArguments

class ArgumentValidator:
    @staticmethod
    def create(command):
        if command == _WAR_COMMAND:
            return WarValidator()
        elif command == _SCORE_COMMAND:
            return ScoreValidator()
        else:
            raise RuntimeError("%s is an unknown command" % command)

    def checkParameterCount(self, arguments, desiredCount, helpmessage):
        if len(arguments) != desiredCount:
            print "Didn't get %s parameters." % desiredCount
            raise ArgumentCountError(helpmessage)

    def checkCorrectFormat(self, argument, desired_format):
        if argument == 'busy':
            return

        format_regex = re.compile(desired_format)
        if not re.match(format_regex, argument):
            raise ArgumentFormatError("%s is not a correct time (use hh:mm)." % argument)

class WarValidator(ArgumentValidator):
    def validate(self, arguments):
        helpmessage = 'You need to tell me when the war starts and when it ends, like so : .%s 15:00 15:15.' % _WAR_COMMAND
        self.checkParameterCount(arguments, 2, helpmessage)
        if arguments[0] == arguments[1]:
            raise ArgumentFormatError("Very funny, but I don't do 0-seconds wars. You don't either and you know it ;-)")
        time_regex = "^(([0]?[0-9]|1[0-9]|2[0-3]):[0-5]?[0-9])$"
        for arg in arguments:
            self.checkCorrectFormat(arg, time_regex)

        self.checkArgumentOrder(arguments)

    def checkArgumentOrder(self, arguments):
        if 'busy' in arguments and arguments.index('busy') != 0:
            raise ArgumentOrderError('"Busy" is no time for a lady to end a war.')

class ScoreValidator(ArgumentValidator):
    def validate(self, arguments):
        helpmessage = 'You need to tell me which war you want to register your score to, and your score, like so: .%s war1 478' % _SCORE_COMMAND
        self.checkParameterCount(arguments, 2, helpmessage)
        try:
            int(arguments[1])
        except ValueError:
            raise ArgumentTypeError("I'll need a numeric score.")
