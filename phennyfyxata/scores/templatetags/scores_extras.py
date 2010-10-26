from django import template
from django.db.models import Avg
from django.db.models import Max
from django.utils.translation import ungettext

from phennyfyxata.scores.models import War
from phennyfyxata.scores.models import Writer
from phennyfyxata.scores.models import ParticipantScore

register = template.Library()

def get_winner_nick(war_id):
    participantScores = ParticipantScore.objects.filter(war__id=war_id)
    winningScore = participantScores.aggregate(Max('score'))['score__max']
    if winningScore:
        return participantScores.get(score=winningScore).writer.nick
    return ''


def format_writer_row(parser, token):
    try:
        tag_name, writer_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]

    return WriterRowNode(writer_name)

class WriterRowNode(template.Node):
    def __init__(self, writer_name):
        self.writer_name = template.Variable(writer_name)

    def render(self, context):
        writer_name = self.writer_name.resolve(context)
        participantScores = ParticipantScore.objects.filter(writer__nick=writer_name)
        totalscore = reduce(lambda x, y: x + y, [ps.score for ps in participantScores], 0)
        totalwars = len(participantScores)
        seconds_warred, time_warred = getTimeWarred(writer_name)
        return """<tr>
    <td><a href="/writers/%s/overview/">%s</a></td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
</tr>""" % (writer_name, writer_name, totalscore, totalwars, time_warred)

def war_participants(parser, token):
    try:
        tag_name, war_id = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]

    return WarParticipantsNode(war_id)

class WarParticipantsNode(template.Node):
    def __init__(self, war_id):
        self.war_id = template.Variable(war_id)

    def render(self, context):
        war_id = self.war_id.resolve(context)
        participantScores = ParticipantScore.objects.filter(war__id=war_id)
        winner = get_winner_nick(war_id)
        writers = map(lambda x: x.writer.nick, participantScores)
        writers = map(lambda x: winner == x and '<b><a href="/writers/%s/overview/">%s</a></b>' % (x, x) or '<a href="/writers/%s/overview/">%s</a>' % (x, x), writers)
        return ",".join(writers)

def war_count(parser, token):
    try:
        tag_name, writer_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]

    return WarcountNode(writer_name)

class WarcountNode(template.Node):
    def __init__(self, writer_name):
        self.writer_name = template.Variable(writer_name)

    def render(self, context):
        writer_name = self.writer_name.resolve(context)
        return ParticipantScore.objects.filter(writer__nick=writer_name).count()

def average_score(parser, token):
    try:
        tag_name, writer_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]

    return AveragescoreNode(writer_name)

class AveragescoreNode(template.Node):
    def __init__(self, writer_name):
        self.writer_name = template.Variable(writer_name)

    def render(self, context):
        writer_name = self.writer_name.resolve(context)
        return ParticipantScore.objects.filter(writer__nick=writer_name).aggregate(Avg('score'))['score__avg']

def wars_won(parser, token):
    try:
        tag_name, writer_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]

    return WarswonNode(writer_name)

class WarswonNode(template.Node):
    def __init__(self, writer_name):
        self.writer_name = template.Variable(writer_name)

    def render(self, context):
        writer_name = self.writer_name.resolve(context)
        participantWars = ParticipantScore.objects.filter(writer__nick=writer_name)
        warsWon = 0
        for war in participantWars:
            winner_nick = get_winner_nick(war.war.id)
            if winner_nick == writer_name:
                warsWon += 1
        return warsWon

def war_participant_details(parser, token):
    try:
        tag_name, war_id = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]

    return WarParticipantDetailsNode(war_id)

class WarParticipantDetailsNode(template.Node):
    def __init__(self, war_id):
        self.war_id = template.Variable(war_id)

    def render(self, context):
        war_id = self.war_id.resolve(context)
        participantScores = ParticipantScore.objects.filter(war__id=war_id).order_by("-score")
        return "".join(map(lambda x: '<tr><td><a href="/writers/%s/overview/">%s</a></td><td>%s</td></tr>' % (x.writer.nick, x.writer.nick, x.score), participantScores))

def wars_for_writer(parser, token):
    try:
        tag_name, writer_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]

    return WarsForWriterNode(writer_name)

class WarsForWriterNode(template.Node):
    def __init__(self, writer_name):
        self.writer_name = template.Variable(writer_name)

    def render(self, context):
        writer_name = self.writer_name.resolve(context)
        participantWars = ParticipantScore.objects.filter(writer__nick=writer_name).order_by("war__id")
        return "".join(map(lambda x: '<tr><td><a href="/wars/%s/overview/">%s</a></td><td>%s</td><td>%s</td><td>%s</td>' % (x.war.id, x.war.id, x.war.timestamp.strftime("%Y-%m-%d %H:%M"), x.war.endtime.strftime("%Y-%m-%d %H:%M"), x.score), participantWars))

def time_warred(parser, token):
    try:
        tag_name, writer_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]

    return TimeWarredNode(writer_name)

class TimeWarredNode(template.Node):
    def __init__(self, writer_name):
        self.writer_name = template.Variable(writer_name)

    def render(self, context):
        writer_name = self.writer_name.resolve(context)
        secondsWarred, timeWarred = getTimeWarred(writer_name)
        return timeWarred

def getTimeWarred(writer_name):
        participantWars = War.objects.filter(participantscore__writer__nick=writer_name)
        totalSeconds = 0
        for war in participantWars:
            duration = war.endtime - war.timestamp 
            durationSeconds = duration.seconds + (duration.days * 86400)
            totalSeconds += durationSeconds
        secondsLeft = totalSeconds % 86400
        days = totalSeconds / 86400
        hours = secondsLeft / 3600
        secondsLeft = secondsLeft % 3600
        minutes = secondsLeft / 60
        daysText = days == 1 and 'day' or 'days'
        hoursText = hours == 1 and 'hour' or 'hours'
        minutesText = minutes == 1 and 'minute' or 'minutes'
        daysText = ungettext("%(days)s day", "%(days)s days", days) % locals()
        hoursText = ungettext("%(hours)s hour", "%(hours)s hours", hours) % locals()
        minutesText = ungettext("%(minutes)s minute", "%(minutes)s minutes", minutes) % locals()
        return totalSeconds, "%(daysText)s, %(hoursText)s, %(minutesText)s" % locals()

register.tag("writer_row", format_writer_row)
register.tag("war_participants", war_participants)
register.tag("warcount", war_count)
register.tag("averagescore", average_score)
register.tag("warswon", wars_won)
register.tag("war_participant_details", war_participant_details)
register.tag("wars_for_writer", wars_for_writer)
register.tag("timewarred", time_warred)
