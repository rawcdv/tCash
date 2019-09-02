from django.urls import path

from . import views

urlpatterns = [
    # ex: /
    path('', views.index, name='index'),
    # ex: /profile/fred/
    path('profile/<username>/', views.detail, name='detail'),
    path('buy/', views.buy_ads, name='buy_ads'),
    path('sell/', views.sell_ads, name='sell_ads'),
    # ex: /ad/1
    path('ad/<int:ad_id>/', views.ad_detail, name='ad'),
    path('new_ad/', views.new_ad, name='new_ad'),
    # # ex: /chat
    # path('chat/', views.chat, name='chat'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('myprofile/', views.profile, name='profile'),
    path('myprofile/edit/', views.edit_profile, name='edit_profile'),
    path('new_review/<username>/', views.new_review, name='new_review'),

    # ajax
    path('ajax/get_locations/', views.get_locations, name='get_locations'),
]
