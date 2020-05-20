from django.conf.urls import url
from users import views
urlpatterns = [
    url(r'^users$', views.RegisterView.as_view()),
    url(r'^session$', views.LoginView.as_view()),
    url(r'^user$', views.UserInfoView.as_view()),
    url(r'^user/avatar$', views.AvatarView.as_view()),
    url(r'^user/name$', views.ModifyNameView.as_view()),
    url(r'^user/auth', views.UserAuthView.as_view()),
]