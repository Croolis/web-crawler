"""scheduler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib import admin

from scheduler.core.views import IndexView, TaskView, SubmitTaskView, UserFormView

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'', IndexView.as_view(), name='index'),
    path(r'<int:pk>/', TaskView.as_view(), name='task'),
    path(r'submit/', SubmitTaskView.as_view(), name='createtask'),
    path(r'userform/<int:subtask_id>/', UserFormView.as_view(), name='userform')
]
