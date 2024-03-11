from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Post, Comment
from .forms import CommentsForm, CreatePostForm

User = get_user_model()


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
    pk_url_kwarg = 'post_id'
    pk_field = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != self.request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
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
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']}
                       )


class CommentEditDeletePermission(LoginRequiredMixin):
    def dispatch(self, request, **kwargs):
        instance = get_object_or_404(Comment, id=self.kwargs['comment_id'])
        if instance.author != self.request.user:
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, **kwargs)
