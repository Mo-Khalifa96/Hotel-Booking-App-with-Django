from django.contrib import admin
from django.urls import path, include 
from django.conf import settings 
from django.conf.urls.static import static 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('bookings.urls')),
    path('api/', include('APIs.urls')), 
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        #add django debugging toolbar
        path('__debug__/', include(debug_toolbar.urls)),  
        path('silk/', include('silk.urls', namespace='silk'))
    ]
    
#Serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

