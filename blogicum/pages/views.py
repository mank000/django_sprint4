from django.shortcuts import render

from django.views.generic import TemplateView


class AboutPage(TemplateView):
    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    template_name = 'pages/rules.html'


def PageNotFound(request, exception):
    return render(request, 'pages/404.html', status=404)


def ServerError(request):
    return render(request, 'pages/500.html', status=500)


def csrfError(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)
