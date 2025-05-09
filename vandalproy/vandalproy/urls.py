"""
URL configuration for vandalproy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', views.dashboard, name='dashboard'),
]

urlpatterns += [
    path('', TemplateView.as_view(template_name='common/home.html'), name='home'),
    path('legal/', TemplateView.as_view(template_name='common/legal.html'), name='legal'),
    path('error/', TemplateView.as_view(template_name='common/error.html'), name='error'),
    path('blog/', TemplateView.as_view(template_name='portal/blog.html'), name='blog'),
    path('calendario/', TemplateView.as_view(template_name='portal/calendario.html'), name='calendario'),
    path('contacto/', TemplateView.as_view(template_name='portal/contacto.html'), name='contacto'),
    path('ranking/', TemplateView.as_view(template_name='portal/ranking.html'), name='ranking'),
    path('redactores/', TemplateView.as_view(template_name='portal/redactores.html'), name='redactores'),
    path('videos/', TemplateView.as_view(template_name='portal/videos.html'), name='videos'),
    path('login/', TemplateView.as_view(template_name='usuarios/login.html'), name='login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)