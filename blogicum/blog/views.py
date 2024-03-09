import datetime as dt
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from blog.models import Post, Category, Comment
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.utils.timezone import make_aware
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from .models import Post
from django.urls import reverse_lazy, reverse
from .forms import CommentsForm, CreatePostForm
from django.db.models import Count
from django.http import Http404

User = get_user_model()
PAGINATE_NUM = 10


def get_post_info():
    return Post.objects.filter(is_published=True,
                               pub_date__lte=make_aware(dt.datetime.now()),
                               category__is_published=True,
                               location__is_published=True)


class PostFormMixin:
    model = Post
    template_name = 'blog/create.html'
    form_class = CreatePostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDispatchMixin:
    model = Post
    template_name = 'blog/create.html'
    form_class = CreatePostForm

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != self.request.user:
            return redirect('blog:post_detail', self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


class ProfileMixin:
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentsForm

    def get_success_url(self) -> str:
        success_url = reverse_lazy('blog:post_detail',
                                   kwargs={'pk': self.kwargs['pk']})
        return success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        context['comment'] = get_object_or_404(Comment,
                                               pk=self.kwargs['comment_id'])
        return context


class IndexView(ListView):
    """Отображает главную страницу."""

    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATE_NUM

    def get_context_data(self, **kwargs):
        post_list = get_post_info().order_by('-pub_date')
        context = {
            'page_obj': post_list[:PAGINATE_NUM].annotate(
                comment_count=Count('comments')),
        }
        return context


class CategoryPostsView(ListView):
    """Отображает страницу категорий."""

    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = PAGINATE_NUM

    def get_queryset(self):
        return get_post_info().filter(
            category__slug=self.kwargs['slug']).order_by(
                '-pub_date').annotate(comment_count=Count('comments'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category,
                                                slug=self.kwargs['slug'],
                                                is_published=True)
        return context


class PostCreateView(LoginRequiredMixin, PostFormMixin, CreateView):
    """Страница создания поста."""

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user})


class EditPostView(LoginRequiredMixin, PostDispatchMixin, UpdateView):
    """Страница изменнеия поста."""

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class PostDetailView(DetailView):
    """Страница детализации поста."""

    model = Post
    template_name = 'blog/detail.html'

    def get_object(self):
        post = get_object_or_404(Post,
                                 pk=self.kwargs['pk'])
        if post.author != self.request.user and post.is_published is False:
            raise Http404("Этот пост ещё не опубликован!")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentsForm()
        context['comments'] = self.object.comments.select_related(
            'author').order_by('created_at')
        return context


class PostDeleteView(LoginRequiredMixin, PostDispatchMixin, DeleteView):
    """Страница удаления поста."""

    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class ProfileDetailView(ProfileMixin, DetailView):

    """Страница профиля пользователя."""
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        posts = user.post_set.all().order_by('-pub_date').annotate(
            comment_count=Count('comments'))
        if self.request.user != user:
            posts = get_post_info().filter(
                author__username=self.kwargs['username']).order_by(
                    '-pub_date').annotate(comment_count=Count('comments'))
        paginator = Paginator(posts, PAGINATE_NUM)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        context['user'] = self.request.user
        context['profile'] = self.object
        return context


class ProfileUpdateView(LoginRequiredMixin, ProfileMixin, UpdateView):
    """Страница обновления информации в профиле у пользователя."""

    template_name = 'blog/user.html'
    fields = ('username', 'first_name', 'last_name', 'email',)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.kwargs['username']}
                       )


class EditCommentView(LoginRequiredMixin, CommentMixin, UpdateView):
    """Страница изменения поста."""

    def get_object(self):
        post_id = self.kwargs['pk']
        comment_id = self.kwargs['comment_id']
        return get_object_or_404(Comment, id=comment_id, post__id=post_id)

    def dispatch(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user or self.request.user.is_superuser:
            raise Http404('У вас нет разрешения на'
                          ' редактирование этого комментария')
        return super().dispatch(request, *args, **kwargs)


class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin,
                        CommentMixin, DeleteView):
    """Страница удаления комментарция."""

    def test_func(self):
        comment = self.get_object()
        return (self.request.user == comment.author
                or self.request.user.is_superuser)

    def get_object(self):
        post_id = self.kwargs['pk']
        comment_id = self.kwargs['comment_id']
        return get_object_or_404(Comment, id=comment_id, post__id=post_id)


class CommentAddCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    """Страница добавления комментария."""

    def dispatch(self, request, *args, **kwargs):
        self.post_id = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['pk']
        if self.request.user.is_authenticated:
            return super().form_valid(form)
        raise Http404()
