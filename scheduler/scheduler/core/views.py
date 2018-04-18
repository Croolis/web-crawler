from django.views import generic

from scheduler.core.models import Task


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        """Return the last five published questions."""
        return Task.objects.order_by('-created_at', '-finished_at')
