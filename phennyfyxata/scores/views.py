import time
import logging

from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist

from templatetags.scores_extras import getTimeWarred

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
    logging.log(logging.CRITICAL, request.GET)
    for key, value in request.GET.items():
        getDict[key] = value
    if getDict.get('sort') == 'time_warred':
        getDict['sort'] = 'seconds_warred'
    elif getDict.get('sort') == '-time_warred':
        getDict['sort'] = '-seconds_warred'

    class WriterTable(tables.Table):
        writer_name = tables.Column(name='writer_name', verbose_name="Writer nick")
        total_score = tables.Column(name='total_score', verbose_name="Total wordcount in wars")
        total_wars = tables.Column(name='total_wars', verbose_name="Wars participated in")
        time_warred = tables.Column(name='time_warred', verbose_name="Time spent in wars")
        seconds_warred = tables.Column(name='seconds_warred', visible=False, sortable=True)

    allwriters = []
    for writer in Writer.objects.all():
        writer_name = writer.nick
        writer_link = '<a href="/writers/%s/overview/">%s</a>' % (writer_name, writer_name)
        participantScores = ParticipantScore.objects.filter(writer__nick=writer_name)
        totalscore = reduce(lambda x, y: x + y, [ps.score for ps in participantScores], 0)
        totalwars = len(participantScores)
        seconds_warred, time_warred = getTimeWarred(writer_name)

        allwriters.append({"writer_name":writer_link, "total_score":totalscore, "total_wars":totalwars, "time_warred":time_warred, "seconds_warred":seconds_warred})

    writertable = WriterTable(allwriters, order_by=getDict.get('sort', 'writer_name'))

    #if getDict.get('sort') == 'time_warred':
    #    writertable.time_warred.direction('asc')
    #    writertable.seconds_warred.direction('desc')
    #elif getDict.get('sort') == '-time_warred':
    #    writertable.time_warred.direction('desc')
    #    writertable.seconds_warred.direction('asc')

    return render_to_response('scores/writersOverview.html', {'table':writertable})
#    writers = Writer.objects.all().order_by("nick")
#    return render_to_response('scores/writersOverview.html', {'writers': writers})

def singleWriterOverview(request, nickname):
    try:
        writer  = Writer.objects.get(nick=nickname)
    except ObjectDoesNotExist:
        raise Http404
    return render_to_response('scores/singleWriterOverview.html', {'writer': writer})

def warsOverview(request):
    wars = War.objects.all()
    return render_to_response('scores/warsOverview.html', {'wars': wars})

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
