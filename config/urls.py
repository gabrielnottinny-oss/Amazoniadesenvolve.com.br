from django.contrib import admin
from core.territory import is_global
admin.site.has_permission = lambda request: bool(request.user.is_active and request.user.is_staff and is_global(request.user))
from django.urls import path,include
from core import views
urlpatterns=[
 path('admin/',admin.site.urls),path('accounts/',include('django.contrib.auth.urls')),
 path('',views.dashboard,name='dashboard'),path('health/',views.health,name='health'),
 path('gestao/<str:module>/',views.records,name='records'),
 path('gestao/<str:module>/novo/',views.record_form,name='record_create'),
 path('gestao/<str:module>/<int:pk>/editar/',views.record_form,name='record_edit'),
]
