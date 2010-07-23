from django.shortcuts import render_to_response

from phennyfyxata.scores.models import Writer

def registerscore(request, nickname, score):
    if request.method == 'POST':
        writer, created = Writer.objects.get_or_create(nick=nickname)
        writer.totalscore += score
        writer.totalwars += 1
        writer.save()

def overview(request):
    writers = Writer.objects.all()
    return render_to_response('scores/overview.html', {'writers': writers})

def getallscores(request):
    pass
