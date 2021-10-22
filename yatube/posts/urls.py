from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

app_name = 'posts'

urlpatterns = [
    path('', cache_page(20)(views.index), name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.post_create, name='create_post'),
    path('posts/<post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'), 
]
