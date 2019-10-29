from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^keyboard/', views.keyboard),
	url(r'^messages/', views.answer),
	
]
