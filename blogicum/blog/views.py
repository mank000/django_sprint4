import datetime as dt

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.utils.timezone import make_aware
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models import Count
from django.http import Http404

from .models import Post, Category, Comment
from .forms import CommentsForm
from .mixins import (
    PostFormMixin,
    PostDispatchMixin,
    ProfileMixin,
    CommentMixin,
    CommentEditDeletePermission
    )

User = get_user_model()
PAGINATE_NUM = 10


def get_post_info():
    return Post.objects.filter(is_published=True,
                               pub_date__lte=make_aware(dt.datetime.now()),
                               category__is_published=True,
                               location__is_published=True,)


def get_paginated_data(data, request):
    return Paginator(data, PAGINATE_NUM).get_page(request.GET.get('page'))


class IndexView(ListView):
    """Отображает главную страницу."""

    model = Post
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = {
            'page_obj': get_paginated_data(get_post_info().order_by('-pub_date').annotate(
                comment_count=Count('comments')), self.request)
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
            category__slug=self.kwargs['slug']
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category,
                                                slug=self.kwargs['slug'],
                                                is_published=True)
        return context


class PostCreateView(LoginRequiredMixin, PostFormMixin, CreateView):
    """Страница создания поста."""

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user})


class EditPostView(LoginRequiredMixin, PostDispatchMixin, UpdateView):
    """Страница изменнеия поста."""

    def get_success_url(self) -> str:
        return reverse('blog:post_detail', kwargs={
            'post_id': self.kwargs['post_id']
        }
        )


class PostDetailView(DetailView):
    """Страница детализации поста."""

    model = Post
    template_name = 'blog/detail.html'

    def get_object(self):
        post = get_object_or_404(Post,
                                 pk=self.kwargs['post_id'])
        if post.author != self.request.user and post.is_published is False:
            raise Http404('Этот пост ещё не опубликован!')
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentsForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostDeleteView(LoginRequiredMixin, PostDispatchMixin, DeleteView):
    """Страница удаления поста."""

    def get_success_url(self) -> str:
        return reverse('blog:index')


class ProfileDetailView(ProfileMixin, DetailView):
    """Страница профиля пользователя."""

    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        posts = user.post_set.all().annotate(
            comment_count=Count('comments'))
        if self.request.user != user:
            posts = get_post_info().filter(
                author__username=self.kwargs['username']).annotate(
                    comment_count=Count('comments'))
        context['page_obj'] = get_paginated_data(
            posts.order_by('-pub_date'), self.request
        )
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


class EditCommentView(CommentEditDeletePermission,
                      CommentMixin,
                      UpdateView):
    """Страница изменения коммента."""

    def get_object(self):
        return get_object_or_404(Comment, id=self.kwargs['comment_id'])


class DeleteCommentView(CommentEditDeletePermission,
                        CommentMixin,
                        DeleteView):
    """Страница удаления комментарция."""

    def get_object(self):
        post_id = self.kwargs['post_id']
        comment_id = self.kwargs['comment_id']
        return get_object_or_404(Comment, id=comment_id, post_id=post_id)


class CommentAddCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    """Страница добавления комментария."""

    def dispatch(self, request, **kwargs):
        self.post_id = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_id']
        if self.request.user.is_authenticated:
            return super().form_valid(form)
        raise Http404()
