"""Представления статических страниц."""
from django.shortcuts import render


# def about(request):
#     """Возвращает страницу «О проекте»."""
#     return render(request, 'pages/about.html')


# def rules(request):
#     """Возвращает страницу «Наши правила»."""
#     return render(request, 'pages/rules.html')


def page_not_found(request, exception):
    """Возвращает страницу «404 - Страница не найдена»."""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    """Возвращает страницу «403 - Доступ запрещен»."""
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request):
    """Возвращает страницу «500 - Ошибка сервера»."""
    return render(request, 'pages/500.html', status=500)
