from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm

from django.urls import include, path, reverse_lazy

from django.views.generic.edit import CreateView

from django.conf import settings
from django.conf.urls.static import static

app_name = 'blogicum'
handler404 = 'pages.views.pagenotfound'
handler500 = 'pages.views.servererror'

urlpatterns = [
    path('', include('blog.urls', namespace='blog')),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
    path('auth/logout/', CreateView.as_view(
        template_name='registration/logget_out.html',
        form_class=UserCreationForm,
        success_url=reverse_lazy('blog:index')),
        name='logout',
    ),
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
