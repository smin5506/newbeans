from django.conf.urls import urls
from . import views

urlpatterns = [
	url(r'^keyboard/', views.keyboard),
	url(r'^messages/', views.answer),
	
]