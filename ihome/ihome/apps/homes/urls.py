from django.conf.urls import url
from homes.views import AreaView,IndexView, DetailView, ShowReleaseView,\
        ReleaseHouseView,ReleaseHouseImageView
urlpatterns = [
        url(r'^areas/$',AreaView.as_view()),
        url(r'^houses/index/$',IndexView.as_view()),
        url(r'^houses/(?P<house_id>\d+)/$',DetailView.as_view()),
        url(r'^user/houses/$', ShowReleaseView.as_view()),
        url(r'^houses$',ReleaseHouseView.as_view()),
        url(r'^houses/(?P<house_id>\d+)/images$', ReleaseHouseImageView.as_view()),
]