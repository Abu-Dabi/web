from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import upload_photo, check_user_view

from sec_sem.views import (
    login_view,
    logout_view,
    home_view,
    find_user_view
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('photo/', upload_photo, name='upload_photo'),
    path('check_user/', check_user_view, name='check_user'),
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('classify/', find_user_view, name='classify'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
