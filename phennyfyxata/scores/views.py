import time
import logging

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator, InvalidPage, EmptyPage

from templatetags.scores_extras import get_time_warred
from templatetags.scores_extras import get_winner_nick
from templatetags.scores_extras import get_participant_list

from phennyfyxata.scores.models import War
from phennyfyxata.scores.models import Writer
from phennyfyxata.scores.models import ParticipantScore

import django_tables as tables

def registerScore(request, nickname):
    if request.method == 'POST':
        logging.log(logging.INFO, "POST method found")
        writer, writerCreated = Writer.objects.get_or_create(nick=nickname)
        logging.log(logging.INFO, "Writer is created: %s" % writerCreated)
        if writerCreated:
            writer.save()

        score = request.POST['score']
        warId = request.POST['war']

        logging.log(logging.INFO, "Score is %s. War ID is %s" % (score, warId))

        war, warCreated = War.objects.get_or_create(id=warId)
        if warCreated:
            war.save()
        
        ps, psCreated = ParticipantScore.objects.get_or_create(writer=writer, war=war)
        ps.score = score
        ps.save()
    return HttpResponse("OK")


def goToWars(request):
    return HttpResponseRedirect("/wars/")

def writersOverview(request):
    getDict = {}
    for key, value in request.GET.items():
        getDict[key] = value
    if getDict.get('sort') == 'time_warred':
        getDict['sort'] = 'seconds_warred'
    elif getDict.get('sort') == '-time_warred':
        getDict['sort'] = '-seconds_warred'

    class WriterTable(tables.Table):
        writer_name = tables.Column(name='writer_name', verbose_name=_("Writer nick"))
        total_score = tables.Column(name='total_score', verbose_name=_("Total wordcount in wars"))
        total_wars = tables.Column(name='total_wars', verbose_name=_("Wars participated in"))
        time_warred = tables.Column(name='time_warred', verbose_name=_("Time spent in wars"))
        seconds_warred = tables.Column(name='seconds_warred', visible=False, sortable=True)

    allwriters = []
    for writer in Writer.objects.all():
        writer_name = writer.nick
        writer_link = '<a href="/writers/%s/overview/">%s</a>' % (writer_name, writer_name)
        participantScores = ParticipantScore.objects.filter(writer__nick=writer_name)
        totalscore = reduce(lambda x, y: x + y, [ps.score for ps in participantScores], 0)
        totalwars = len(participantScores)
        seconds_warred, time_warred = get_time_warred(writer_name)

        allwriters.append({"writer_name":writer_link, "total_score":totalscore, "total_wars":totalwars, "time_warred":time_warred, "seconds_warred":seconds_warred})

    writertable = WriterTable(allwriters, order_by=getDict.get('sort', 'writer_name'))

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    writertable.paginate(Paginator, 20, page=page, orphans=0)

    for row in writertable.rows.page():
        pass

    sort = request.GET.get('sort', 'writer_name')

    return render_to_response('scores/writersOverview.html', {'table':writertable, 'sort':sort})

def singleWriterOverview(request, nickname):
    try:
        writer  = Writer.objects.get(nick=nickname)
    except ObjectDoesNotExist:
        raise Http404
    return render_to_response('scores/singleWriterOverview.html', {'writer': writer})

def warsOverview(request):

    class WarTable(tables.Table):
        war_id = tables.Column(name='war_id', verbose_name=_("War ID"), sortable=False)
        timestamp = tables.Column(name='timestamp', verbose_name=_("Timestamp"), sortable=False)
        participants = tables.Column(name='participants', verbose_name=_("Participants"), sortable=False)

    allwars = []
    for war in War.objects.all():
        war_link = '<a href="/wars/%s/overview/">%s</a>' % (war.id, war.id)
        wartime = '%s - %s' % (war.timestamp, war.endtime)
        participantlist = get_participant_list(war.id)

        allwars.append({"war_id":war.id, "timestamp":wartime, "participants":participantlist})

    wartable = WarTable(allwars, order_by=request.GET.get('sort', 'war_id'))

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    wartable.paginate(Paginator, 20, page=page, orphans=0)

    for row in wartable.rows.page():
        pass

    sort = request.GET.get('sort', 'war_id')

    return render_to_response('scores/warsOverview.html', {'table': wartable, 'sort':sort})

def documentation(request):
    return render_to_response('scores/documentation.html')

def documentationDutch(request):
    return render_to_response('scores/documentation.nl.html')

def singleWarOverview(request, war_id):
    try:
        war = War.objects.get(id=war_id)
    except ObjectDoesNotExist:
        raise Http404
    return render_to_response('scores/singleWarOverview.html', {'war': war})

def createWar(request):
    logging.log(logging.INFO, "Creating a new war")
    if request.method == 'POST':
        logging.log(logging.INFO, "POST method found in createWar")
        logging.log(logging.INFO, "POST data: %s" % request.POST)
        endtime = request.POST['endtime']
        starttime = request.POST['starttime']
        logging.log(logging.INFO, "Start time is %s (type %s)" % (starttime, type(starttime)))
        logging.log(logging.INFO, "End time is %s (type %s)" % (endtime, type(endtime)))
        war = War.objects.create(timestamp=time.strftime("%Y-%m-%d %H:%M", time.localtime(float(starttime))), endtime=time.strftime("%Y-%m-%d %H:%M", time.localtime(float(endtime))))
        logging.log(logging.INFO, "Created war")
        html = str(war.id)
        return HttpResponse(html)
    raise Http404

def language(request):
    return render_to_response('scores/language.html')
