from django.conf.urls import url, include
from team import views

urlpatterns = [
	url('^$',							views.index,			name='index'),
	url(r'^login$',						views.login_view, 		name='login_view'),
	url(r'^logout$',					views.logout_view, 		name='logout_view'),
	url(r'^game$',						views.show_all_game, 	name='show_all_game'),
	url(r'^game/(?P<game_id>\d+)/$',	views.show_game,	 	name='show_game'),
	url(r'^member/(?P<member_id>\d+)/$',views.show_member, 		name='show_member'),
	url(r'^addgame/$',					views.add_game,			name='add_game'),
	url(r'^editgame/(?P<game_id>\d+)/$',views.edit_game,		name='edit_game'),
	url(r'^batting/$',					views.show_all_batting, name='show_all_batting'),
    url(r'^pitching/$',					views.show_all_pitching,name='show_all_pitching'),
]
