from django.conf.urls.static import static
from django.conf import settings

from django.urls import path, include

from . import views

app_name = 'blog'

url_category = [
    path('<slug:slug>/',
         views.CategoryPostsView.as_view(),
         name='category_posts'
         ),
]

url_profile = [
    path('<slug:username>/',
         views.ProfileDetailView.as_view(),
         name='profile'
         ),
    path('<slug:username>/edit/',
         views.ProfileUpdateView.as_view(),
         name='edit_profile'
         ),
]

url_post = [
    path('<int:pk>/',
         views.PostDetailView.as_view(),
         name='post_detail'
         ),
    path('create/',
         views.PostCreateView.as_view(),
         name='create_post'
         ),
    path('<int:pk>/edit/',
         views.EditPostView.as_view(),
         name='edit_post'
         ),
    path('<int:pk>/comment/',
         views.CommentAddCreateView.as_view(),
         name='add_comment'
         ),
    path('<int:pk>/delete/',
         views.PostDeleteView.as_view(),
         name='delete_post'
         ),
    path('<int:pk>/edit_comment/<int:comment_id>/',
         views.EditCommentView.as_view(),
         name='edit_comment'
         ),
    path('<int:pk>/delete_comment/<int:comment_id>/',
         views.DeleteCommentView.as_view(),
         name='delete_comment'
         ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = [
    path('',
         views.IndexView.as_view(),
         name='index'
         ),
    path('posts/',
         include(url_post)
         ),
    path('profile/',
         include(url_profile)
         ),
    path('category/',
         include(url_category)
         )
]
