"""Представления приложения блога."""
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from .models import Post, Category, Comment
from django.views.generic import (
    ListView, UpdateView, CreateView, DeleteView, DetailView
)
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from .forms import PostForm, CommentForm
from django.db.models import Count
from django.http import Http404

User = get_user_model()


def get_published_posts():
    """Возвращает queryset опубликованных постов."""
    return Post.objects.select_related('category').filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).annotate(comment_count=Count('comments'))


class IndexView(ListView):
    """Возвращает главную страницу блога со списком постов."""

    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return get_published_posts().order_by('-pub_date')


class PostDetailView(DetailView):
    """Возвращает страницу с деталями поста по его id."""

    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'id'

    def get_object(self, queryset=None):
        """Возвращает пост, скрывая неопубликованные от чужих читателей."""
        post = super().get_object(queryset)

        if self.request.user == post.author:
            return post

        if (
            not post.is_published or not post.category.is_published
            or post.pub_date > timezone.now()
        ):
            raise Http404("Пост не найден")
        return post

    def get_context_data(self, **kwargs):
        """Добавляет в контекст форму и список комментариев."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryPostsView(ListView):
    """Возвращает страницу с постами выбранной категории."""

    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        """Возвращает опубликованные посты выбранной категории."""
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category'],
            is_published=True,
        )
        return get_published_posts().filter(
            category=self.category
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        """Добавляет категорию в контекст."""
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileView(ListView):
    """Возвращает страницу профиля пользователя с его постами."""

    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self):
        """Возвращает посты автора; скрытые — только для него самого."""
        self.profile_user = get_object_or_404(User, username=(
            self.kwargs['username']
        ))
        queryset = Post.objects.filter(author=self.profile_user)

        if self.request.user != self.profile_user:
            queryset = queryset.filter(pub_date__lte=timezone.now())

        return queryset.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        """Добавляет автора постов в контекст."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile_user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирует профиль текущего пользователя."""

    model = User
    fields = ['username', 'first_name', 'last_name', 'email']
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        """Возвращает объект текущего пользователя."""
        return self.request.user

    def get_success_url(self):
        """Перенаправляет на страницу профиля."""
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username
        })


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создаёт новый пост от имени текущего пользователя."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Назначает автора поста до сохранения."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправляет на страницу профиля автора."""
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username
        })


class PostUpdateView(UpdateView):
    """Редактирует пост; доступно только его автору."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        """Перенаправляет неавтора на страницу поста."""
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', id=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Перенаправляет на страницу отредактированного поста."""
        return reverse('blog:post_detail', kwargs={'id': self.object.id})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаляет пост; доступно только его автору."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'id'

    def test_func(self):
        """Разрешает удаление только автору поста."""
        return self.get_object().author == self.request.user

    def get_success_url(self):
        """Перенаправляет на страницу профиля автора."""
        return reverse('blog:profile', kwargs={
            'username': self.request.user.username
        })


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Добавляет комментарий к посту от имени текущего пользователя."""

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        """Привязывает комментарий к посту и автору."""
        post = get_object_or_404(Post, pk=self.kwargs['id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправляет на страницу поста."""
        return reverse('blog:post_detail', kwargs={
            'id': self.kwargs['id']
        })


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирует комментарий; доступно только его автору."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        """Разрешает редактирование только автору комментария."""
        return self.get_object().author == self.request.user

    def get_success_url(self):
        """Перенаправляет на страницу поста."""
        return reverse('blog:post_detail', kwargs={'id': self.kwargs['id']})


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаляет комментарий; доступно только его автору."""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        """Разрешает удаление только автору комментария."""
        return self.get_object().author == self.request.user

    def get_success_url(self):
        """Перенаправляет на страницу поста."""
        return reverse('blog:post_detail', kwargs={
            'id': self.kwargs['id']
        })
