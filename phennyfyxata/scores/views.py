import time
import datetime
import logging

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.core.paginator import Paginator

from templatetags.scores_extras import get_time_warred
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

        if score == '0':
            try:
                ps = ParticipantScore.objects.get(writer=writer, war=war)
                ps.delete()
            except ObjectDoesNotExist:
                return HttpResponse("OK")
        else:
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

        allwriters.append({"writer_name": writer_link, "total_score": totalscore, "total_wars": totalwars, "time_warred": time_warred, "seconds_warred": seconds_warred})

    writertable = WriterTable(allwriters, order_by=getDict.get('sort', 'writer_name'))

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    writertable.paginate(Paginator, 20, page=page, orphans=0)

    for row in writertable.rows.page():
        pass

    sort = request.GET.get('sort', 'writer_name')

    return render_to_response('scores/writersOverview.html', {'table': writertable, 'sort': sort})


def singleWriterOverview(request, nickname):
    try:
        writer = Writer.objects.get(nick=nickname)
    except ObjectDoesNotExist:
        raise Http404
    return render_to_response('scores/singleWriterOverview.html', {'writer': writer})


def warsOverview(request):

    class WarTable(tables.Table):
        war_id = tables.Column(name='war_id', verbose_name=_("War ID"), sortable=False)
        starttime = tables.Column(name='starttime', verbose_name=_("Starttime"), sortable=False)
        participants = tables.Column(name='participants', verbose_name=_("Participants"), sortable=False)

    allwars = []
    for war in War.objects.all():
        war_link = '<a href="/wars/%s/overview/">%s</a>' % (war.id, war.id)
        wartime = '%s - %s' % (war.starttime, war.endtime)
        participantlist = get_participant_list(war.id)

        allwars.append({"war_id": war_link, "starttime": wartime, "participants": participantlist})

    wartable = WarTable(allwars, order_by=request.GET.get('sort', 'war_id'))

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    wartable.paginate(Paginator, 20, page=page, orphans=0)

    for row in wartable.rows.page():
        pass

    sort = request.GET.get('sort', 'war_id')

    return render_to_response('scores/warsOverview.html', {'table': wartable, 'sort': sort})


def documentation(request):
    return render_to_response('scores/documentation.html')


def documentationDutch(request):
    return render_to_response('scores/documentation.nl.html')


def singleWarInfo(request, war_id):
    try:
        war = War.objects.get(id=war_id)
    except ObjectDoesNotExist:
        raise Http404

    info = "{'start': '%s', 'end': '%s'}" % (war.starttime, war.endtime)
    return HttpResponse(info)


def singleWarOverview(request, war_id):
    try:
        war = War.objects.get(id=war_id)
    except ObjectDoesNotExist:
        raise Http404
    return render_to_response('scores/singleWarOverview.html', {'war': war})


def participateWar(request):
    pass


def withdrawWar(request):
    pass


def createWar(request):
    logging.log(logging.INFO, "Creating a new war")
    if request.method == 'POST':
        logging.log(logging.INFO, "POST method found in createWar")
        logging.log(logging.INFO, "POST data: %s" % request.POST)
        endtime = request.POST['endtime']
        starttime = request.POST['starttime']
        logging.log(logging.INFO, "Start time is %s (type %s)" % (starttime, type(starttime)))
        logging.log(logging.INFO, "End time is %s (type %s)" % (endtime, type(endtime)))
        war = War.objects.create(starttime=time.strftime("%Y-%m-%d %H:%M", time.localtime(float(starttime))), endtime=time.strftime("%Y-%m-%d %H:%M", time.localtime(float(endtime))))
        logging.log(logging.INFO, "Created war")
        html = str(war.id)
        return HttpResponse(html)
    raise Http404


def language(request):
    return render_to_response('scores/language.html')


def activeWars(request):
    now_time = time.localtime()
    now = datetime.datetime(now_time[0], now_time[1], now_time[2], now_time[3], now_time[4], now_time[5])
    wars = War.objects.filter(starttime__lt=now, endtime__gt=now)
    wars_string = ','.join(["War %s: %s tot %s (%s minuten)" % (war.id, war.starttime.strftime("%H:%M"), war.endtime.strftime("%H:%M"), (war.endtime - war.starttime).seconds / 60) for war in wars])
    return HttpResponse(wars_string)


def plannedWars(request):
    logging.log(logging.INFO, 'Retrieving planned wars')
    now_time = time.localtime()
    now = datetime.datetime(now_time[0], now_time[1], now_time[2], now_time[3], now_time[4], now_time[5])
    wars = War.objects.filter(starttime__gt=now)
    wars_string = ','.join(["War %s: %s tot %s (%s minuten)" % (war.id, war.starttime.strftime("%H:%M"), war.endtime.strftime("%H:%M"), (war.endtime - war.starttime).seconds / 60) for war in wars])
    return HttpResponse(wars_string)
