from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'protect/index.html'


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'