from django.shortcuts import render
from django.views.generic.edit import FormView
from .forms import FileFieldForm
from .tasks import process_uploaded_replay, selenium_process_replay
from django.http import JsonResponse, HttpResponse
import json

from .models import OverallSentiment, PlayerMatchSingular


# Create your views here.


class FileFieldView(FormView):
    form_class = FileFieldForm
    template_name = 'PlayerMatch/replay_file_upload.html'

    def get_context_data(self, **kwargs):
        context = super(FileFieldView, self).get_context_data(**kwargs)
        curSentiments = OverallSentiment.objects.get(pk=1)
        allPlayers = PlayerMatchSingular.objects.all()

        negativeMessages = []
        for i in allPlayers:
            if len(negativeMessages) >= 100:
                break
            for num in range(0, len(i.messages)):
                if i.messageSentiments[num] < -0.5:
                    negativeMessages.append('"' + i.messages[num] + '"' + "&nbsp;&nbsp;-" + i.username)
                    break

        context['curMessages'] = negativeMessages

        context['terran'] = str(
            round((curSentiments.terranSentimentOverall / curSentiments.terranSentimentCount) * 100, 2))

        context['zerg'] = str(round((curSentiments.zergSentimentOverall / curSentiments.zergSentimentCount) * 100, 2))

        context['protoss'] = str(
            round((curSentiments.protossSentimentOverall / curSentiments.protossSentimentCount) * 100, 2))

        return context

    def post(self, request, *args, **kwargs):
        requestFiles = {}
        if request.POST.get('process_btn'):
            selenium_process_replay()
        if request.is_ajax and request.method == "POST":
            form = FileFieldForm(request.POST)
            files = request.FILES.getlist('replay_file')

            requestResponse = []
            for f in files:
                # Verify Correct Files
                if f.name.endswith('.SC2Replay'):
                    print(f.name)
                    requestResponse.append(f.name)
                    process_uploaded_replay(f.file)
            requestFiles['data'] = requestResponse
            return JsonResponse(requestFiles)
