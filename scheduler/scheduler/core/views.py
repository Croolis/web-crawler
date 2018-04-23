from django.views import generic

from scheduler.core.models import Task


class IndexView(generic.ListView):
    template_name = 'core/index.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        """Return the last five published questions."""
        return Task.objects.order_by('-created_at', '-finished_at')


class TaskView(generic.DetailView):
    template_name = 'core/task.html'
    context_object_name = 'task'
    model = Task


class SubmitTaskView(generic.CreateView):
    model = Task
    fields = ['name', 'configuration', 'stages_number']
    success_url = '/'
