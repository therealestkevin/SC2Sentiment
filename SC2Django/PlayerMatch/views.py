from django.shortcuts import render
from django.views.generic.edit import FormView
from .forms import FileFieldForm
from .tasks import process_uploaded_replay
from django.urls import reverse
# Create your views here.


class FileFieldView(FormView):
    form_class = FileFieldForm
    template_name = 'PlayerMatch/replay_file_upload.html'

    def get_success_url(self):
        return reverse('PlayerMatch:replay-upload')

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('replay_file')
        if form.is_valid():
            for f in files:
                process_uploaded_replay(f)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


