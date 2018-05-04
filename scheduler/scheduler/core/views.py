from django import http
from django.views import generic
import json

from scheduler.core.models import Task
from scheduler.core.taskutils.parse_config import parse_config


class IndexView(generic.ListView):
    template_name = 'core/index.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.order_by('-finished_at', '-created_at')


class TaskView(generic.DetailView):
    template_name = 'core/task.html'
    context_object_name = 'task'
    model = Task


class SubmitTaskView(generic.CreateView):
    model = Task
    fields = ['name', 'configuration']
    success_url = '/{id}/'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            name = form.cleaned_data['name']
            config = json.loads(form.cleaned_data['configuration'])
            self.object = parse_config(name, config)
            return http.HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)
