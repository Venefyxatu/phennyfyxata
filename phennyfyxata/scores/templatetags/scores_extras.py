from django import template
from django.db.models import Avg
from django.db.models import Max

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
        return """<tr>
    <td><a href="/writers/%s/overview/">%s</a></td>
    <td>%s</td>
    <td>%s</td>
</tr>""" % (writer_name, writer_name, totalscore, totalwars)

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

register.tag("writer_row", format_writer_row)
register.tag("war_participants", war_participants)
register.tag("warcount", war_count)
register.tag("averagescore", average_score)
register.tag("warswon", wars_won)
register.tag("war_participant_details", war_participant_details)
register.tag("wars_for_writer", wars_for_writer)
