from django.conf.urls import url, include
from team import views

urlpatterns = [
	url('^$', views.index, name='index'),
	url(r'^login$', views.login, name='login'),
	url(r'^logout$', views.logout, name='logout'),
	url(r'', include('social_auth.urls')),
]
