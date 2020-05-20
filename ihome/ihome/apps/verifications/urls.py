from django.conf.urls import url
from verifications import views
urlpatterns = [
    url(r'^imagecode$', views.ImageCodeView.as_view()),
    url(r'^sms$', views.SMSCodeView.as_view()),
    url(r'^imagecode$', views.ImageCodeView.as_view())
]