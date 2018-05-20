from django import http
from django.shortcuts import get_object_or_404, render
from django.views import generic
from django.utils import timezone
import json

from scheduler.core.constants import SUBTASK_TYPE, TASK_STATUS
from scheduler.core.models import Task, Subtask
from scheduler.core.tasks.parse_config import parse_config


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


class UserFormView(generic.FormView):
    template_name = 'core/user_form_form.html'

    def get(self, request, *args, **kwargs):
        subtask_id = kwargs['subtask_id']
        subtask = get_object_or_404(Subtask, pk=subtask_id, type=SUBTASK_TYPE.USER_INPUT)
        config = json.loads(subtask.configuration)
        context = {
            'form_fields': config['form_fields'],
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        subtask_id = kwargs['subtask_id']
        subtask = get_object_or_404(Subtask, pk=subtask_id, type=SUBTASK_TYPE.USER_INPUT)
        config = json.loads(subtask.configuration)

        next_action = Subtask.objects.get(stage=subtask.stage, type=SUBTASK_TYPE.ACTION)
        action_config = json.loads(next_action.configuration)

        action_config.setdefault('form_data', {})
        for field in config['form_fields']:
            action_config['form_data'][field] = request.POST.get(field, '')
        next_action.configuration = json.dumps(action_config)
        next_action.save(update_fields=['configuration'])

        subtask.status = TASK_STATUS.DONE
        subtask.finished_at = timezone.now()
        subtask.save(update_fields=['status', 'finished_at'])

        success_url = '/{}/'.format(subtask.parent_task.pk)
        return http.HttpResponseRedirect(success_url)

