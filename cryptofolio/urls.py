from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'logout.html'}, name='logout'),
    url(
	r'^password_reset/$',
	auth_views.password_reset,
	{'template_name': 'password_reset_form.html'},
	name='password_reset'
    ),
    url(
	r'^password_reset/done/$',
	auth_views.password_reset_done,
	{'template_name': 'password_reset_done.html'},
	name='password_reset_done'
    ),
    url(
	r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
	{'template_name': 'password_reset_confirm.html'},
	name='password_reset_confirm'
    ),
    url(
	r'^reset/done/$',
	auth_views.password_reset_complete,
	{'template_name': 'password_reset_complete.html'},
	name='password_reset_complete'
    ),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^settings/exchange/(?P<exchange_id>[0-9A-Za-z]+)/$', views.exchange, name='exchange'),
    url(r'^refreshBalances/$', views.refreshBalances, name='refreshBalances'),
    url(r'^settings/details/$', views.changeDetails, name='details'),
    url(r'^settings/password/$', views.changePassword, name='password'),
    url(r'^settings/exchange/(?P<exchange_id>[0-9A-Za-z]+)/remove$', views.removeExchange, name='removeExchange'),
    url(r'^policy/$', views.policy, name='policy'),
]

