from django.conf.urls import url, include
from django.contrib import admin
from rest_framework_nested import routers
from api_handler import views
from rest_framework.urlpatterns import format_suffix_patterns

router = routers.DefaultRouter()
router.register(r'platform_users', views.PlatformUserViewSet, base_name="platform_users")
router.register(r'projects', views.ProjectViewSet, base_name='projects')
router.register(r'companies', views.CompanyViewSet, base_name='companies')

urlpatterns = [
    url(r'^', include(router.urls)),
]

# urlpatterns += format_suffix_patterns([url(r'^api-auth/', include('rest_framework.urls'))])