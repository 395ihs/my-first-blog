from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^inha/get_data.php', views.set_data, name='set_data'),
    url(r'^$', views.post_list, name='post_list'),
]
