# from django.contrib.auth.models import User
# from django.views.generic.edit import CreateView
# from django.views.generic import TemplateView
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.contrib.auth.decorators import login_required
# from .models import BaseRegisterForm
#
#
# class IndexView(LoginRequiredMixin, TemplateView):
#     template_name = 'account/index.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['is_not_author'] = not self.request.user.groups.filter(name = 'authors').exists()
#         return context
#
#
# class BaseRegisterView(CreateView):
#     model = User
#     form_class = BaseRegisterForm
#     success_url = '/'
