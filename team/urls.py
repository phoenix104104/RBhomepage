from django.conf.urls import url, include
from team import views

urlpatterns = [
	url('^$', views.index, name='index'),
	url(r'^login$', views.login_view, name='login_view'),
	url(r'^logout$', views.logout_view, name='logout_view')
]
