from django.conf.urls import url

from . import views

app_name = 'wechat'
urlpatterns = [
    url(r'^wechat/$', views.wechat, name='wechat'),
]