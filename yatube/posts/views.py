from typing import Dict, Any

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm

POSTS_PER_PAGE = 10


def index(request):
    """View-функция для главной страницы"""

    template: str = 'posts/index.html'

    posts: Paginator = Paginator(Post.objects.select_related('author', 'group')
                                 .all(), POSTS_PER_PAGE)
    page_number: int = request.GET.get('page')
    page_obj: Paginator = posts.get_page(page_number)

    context: Dict[str, Any] = {
        'page_obj': page_obj,
        'index': True,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """View-функция для страницы группы записей"""

    template: str = 'posts/group_list.html'

    group: Group = get_object_or_404(Group, slug=slug)
    posts: Paginator = Paginator(group.group_posts.select_related('author').
                                 all(), POSTS_PER_PAGE)
    page_number: int = request.GET.get('page')
    page_obj: Paginator = posts.get_page(page_number)

    context: Dict[str, Any] = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """View-функция для страницы Профайл пользователя"""

    template: str = 'posts/profile.html'

    author: User = get_object_or_404(User, username=username)
    user: User = request.user
    following: bool = False
    if request.user.is_authenticated and Follow.objects.filter(user=user,
                                                               author=author):
        following = True
    posts: Paginator = Paginator(author.author_posts.select_related('group').
                                 all(), POSTS_PER_PAGE)
    posts_count: int = posts.count
    page_number: int = request.GET.get('page')
    page_obj: Paginator = posts.get_page(page_number)

    context: Dict[str, Any] = {
        'author': author,
        'page_obj': page_obj,
        'posts_count': posts_count,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """View-функция для страницы Подробности записи"""

    template: str = 'posts/post_detail.html'

    post: Post = get_object_or_404(Post, pk=post_id)
    posts_count: int = Post.objects.filter(author=post.author).count()
    comments: Comment = post.comments.select_related('author').all()
    form = CommentForm()

    context: Dict[str, Any] = {
        'post': post,
        'posts_count': posts_count,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """View-функция для формы добавления новой записи"""

    template: str = 'posts/post_create.html'

    form: PostForm = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if not form.is_valid():
        return render(request, template, {'form': form})
    fields = form.save(commit=False)
    fields.author = request.user
    fields.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    """View-функция редактирования записи"""

    template: str = 'posts/post_create.html'
    is_edit: bool = True

    post: Post = get_object_or_404(Post, pk=post_id)

    form: PostForm = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        if request.user != post.author:
            return redirect('posts:post_detail', post_id)
        return render(request, template, {'form': form, 'is_edit': is_edit})
    fields = form.save(commit=False)
    fields.author = request.user
    fields.save()
    return redirect('posts:post_detail', fields.pk)


@login_required
def add_comment(request, post_id):
    """View-функция добавления комментария"""

    post: Post = get_object_or_404(Post, pk=post_id)

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """View-функция для страницы Подписок"""

    template: str = 'posts/follow.html'

    authors_ids = Follow.objects.filter(user=request.user).values_list(
        'author_id',
        flat=True)
    posts: Paginator = Paginator(Post.objects.select_related('author', 'group')
                                 .filter(author_id__in=authors_ids),
                                 POSTS_PER_PAGE)
    page_number: int = request.GET.get('page')
    page_obj: Paginator = posts.get_page(page_number)

    context: Dict[str, Any] = {
        'page_obj': page_obj,
        'follow': True,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """View-функция Подписаться на автора"""

    author: User = get_object_or_404(User, username=username)
    if request.user == author or Follow.objects.filter(
            user=request.user, author=author):
        return redirect('posts:profile', username=username)
    Follow.objects.create(user=request.user, author=author)

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """View-функция Отписаться от автора"""

    author: User = get_object_or_404(User, username=username)
    follow: Follow = get_object_or_404(Follow, user=request.user,
                                       author=author)
    follow.delete()

    return redirect('posts:profile', username=username)
