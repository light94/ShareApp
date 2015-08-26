from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
import views
urlpatterns = [
	url(r'^index/$',views.index),
	url(r'^fblogin/(?P<code>.*)',views.fblogin),
	url(r'^display',views.index),
	url(r'^lilogin',views.lilogin),
	url(r'^showForm',views.showForm),
	url(r'^postUpdate',views.postUpdate),
	url(r'^retrieveData',views.retrieveData),
	url(r'^getAnalyticsForPost',views.getAnalyticsForPost)
]