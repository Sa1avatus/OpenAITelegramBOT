import allauth.socialaccount.models as au
from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .filters import PostFilter
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, TemplateView
from dotenv import load_dotenv
load_dotenv()


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'account/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name = 'authors').exists()
        return context


class BaseRegisterView(CreateView):
    model = User
    form_class = BasicSignupForm
    success_url = '/'


class PostList(ListView):
    model = Post
    ordering = '-creation'
    template_name = 'posts/posts.html'
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
    template_name = 'posts/post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        context['user_auth'] = self.request.user.is_authenticated
        id = self.kwargs.get('pk')
        post = Post.objects.get(pk=id)
        context['categories'] = post.category.all()
        return context


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'posts/post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.rating = 0
        return super().form_valid(form)


class NewsCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'posts/post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.rating = 0
        post.type = 2
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        new = Post(
            description=request.POST['description'],
            author_id=request.POST['author'],
            title=request.POST['title'],
        )
        new.save()
        new.category.set(request.POST['category'])
        #Notification().send(new)
        return redirect('/news/')


class ArticleCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'posts/post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.rating = 0
        post.type = 1
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        new = Post(
            description=request.POST['description'],
            author_id=request.POST['author'],
            title=request.POST['title'],
        )
        new.save()
        new.category.set(request.POST['category'])
        #Notification().send(new)
        return redirect('/news/')


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'posts/post_edit.html'


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'posts/post_delete.html'
    success_url = reverse_lazy('post_list')


class PostSearch(ListView):
    model = Post
    ordering = '-creation'
    template_name = 'posts/search.html'
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


class CategoryListView(ListView):
    model = Post
    template_name = 'posts/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(category=self.category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)
    return render(request, 'posts/subscribe.html', {'category': category, 'message': 'Вы подписались на категорию' })


@login_required
def unsubscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.remove(user)
    return redirect('/news/')


@login_required
def make_me_author(request):
    user = request.user
    author_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author_group.user_set.add(user)
    return redirect('/')