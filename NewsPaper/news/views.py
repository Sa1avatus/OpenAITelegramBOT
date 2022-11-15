from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post
from datetime import datetime
from .filters import PostFilter
from .forms import PostForm
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin



class PostList(ListView):
    model = Post
    ordering = '-creation'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class PostCreate(LoginRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.rating = 0
        return super().form_valid(form)


class NewsCreate(LoginRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.rating = 0
        post.type = 2
        return super().form_valid(form)


class ArticleCreate(LoginRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.rating = 0
        post.type = 1
        return super().form_valid(form)


#@method_decorator(LoginRequiredMixin, TemplateView)
class PostUpdate(LoginRequiredMixin, UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


class PostDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')


class PostSearch(ListView):
    model = Post
    ordering = '-creation'
    template_name = 'search.html'
    context_object_name = 'posts'
    paginate_by = 10
    success_url = reverse_lazy('post_list')

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

