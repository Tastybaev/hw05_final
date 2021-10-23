from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow


@cache_page(60 * 15)
def index(request):
    templates = 'posts/index.html'
    text = 'Это главная страница проекта Yatube'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGINATOR_OBJECTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'text': text,
        'page_obj': page_obj,
    }
    return render(request, templates, context)


def group_posts(request, slug):
    templates = 'posts/group_list.html'
    text = 'Здесь будет информация о группах проекта Yatube'
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    paginator = Paginator(post_list, settings.PAGINATOR_OBJECTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'text': text,
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, templates, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user)
    paginator = Paginator(post_list, settings.PAGINATOR_OBJECTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        'user': user,
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    posts_count = post.author.posts.all().count()
    is_author = request.user == post.author   
    context = {
        'post': post,
        'post_id': post_id,
        'posts_count': posts_count,
        'is_author': is_author,
    }
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:index')
    if request.method == "POST":
        form = PostForm(request.POST or None,
                        files=request.FILES or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(instance=post)
    return render(request, 'posts/create_post.html', {
        'form': form,
        'post_id': post_id,
        'is_edit': True,
    })

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)

@login_required
def follow_index(request):
    post = Post.object.filter(author__following__user=request.user)
    return render(request, 'posts/follow.html', {'page_obj': page_obj})

@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != username and not Follow.objects.filter(author=username, user=request.user).exists():
        follow = Follow(author=username, user=request.user)
        follow.save()

    return redirect('posts:profile', username=username)

@login_required
def profile_unfollow(request, username):
    following = Follow.objects.filter(author=username, user=request.user).first()
    if following is not None:
        following.delete()
    return redirect('posts:profile', username=username)
